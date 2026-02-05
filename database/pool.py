"""Database connection pool for aiosqlite connections."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiosqlite

logger = logging.getLogger(__name__)

# Global pool instance
_pool: "ConnectionPool | None" = None


def get_pool() -> "ConnectionPool":
    """Get the global connection pool instance.

    If pool is not initialized, creates a default pool (for tests).

    Returns:
        ConnectionPool: The global connection pool
    """
    global _pool
    if _pool is None:
        # Auto-initialize with defaults (useful for tests)
        _pool = ConnectionPool(pool_size=5, max_overflow=10)
    return _pool


def initialize_pool(pool_size: int = 5, max_overflow: int = 10) -> "ConnectionPool":
    """Initialize the global connection pool.

    Args:
        pool_size: Number of connections to maintain in pool
        max_overflow: Maximum additional connections beyond pool_size

    Returns:
        ConnectionPool: The initialized connection pool
    """
    global _pool
    if _pool is not None:
        logger.warning("Connection pool already initialized")
        return _pool

    _pool = ConnectionPool(pool_size=pool_size, max_overflow=max_overflow)
    return _pool


class ConnectionPool:
    """Connection pool for aiosqlite connections."""

    def __init__(self, pool_size: int = 5, max_overflow: int = 10):
        """Initialize connection pool.

        Args:
            pool_size: Number of connections to maintain in pool
            max_overflow: Maximum additional connections beyond pool_size
        """
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self._pool: asyncio.Queue[
            aiosqlite.Connection
        ] | None = None  # Created in event loop
        self._created = 0
        self._lock: asyncio.Lock | None = None  # Created in event loop
        self._closed = False

    async def _create_connection(self) -> aiosqlite.Connection:
        """Create a new database connection."""
        # Import here to avoid circular dependency
        from .operations.shared import get_db_path

        db_path = get_db_path()
        conn = await aiosqlite.connect(db_path)
        await conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _ensure_loop_objects(self) -> None:
        """Create queue and lock in the current event loop (lazy init)."""
        if self._pool is None:
            self._pool = asyncio.Queue(maxsize=self.pool_size)
            self._lock = asyncio.Lock()

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Get a connection from the pool.

        Yields:
            aiosqlite.Connection: Database connection
        """
        self._ensure_loop_objects()
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        conn = None
        try:
            # Try to get connection from pool (non-blocking)
            try:
                conn = self._pool.get_nowait()
            except asyncio.QueueEmpty:
                # Pool empty, check if we can create new connection
                should_create = False
                async with self._lock:
                    current_count = self._created
                    if current_count < self.pool_size + self.max_overflow:
                        self._created += 1
                        should_create = True

                if should_create:
                    try:
                        conn = await self._create_connection()
                        logger.debug(f"Created new connection (total: {self._created})")
                    except Exception:
                        async with self._lock:
                            self._created -= 1
                        raise
                else:
                    # Wait for connection to become available (with timeout to prevent hanging)
                    try:
                        conn = await asyncio.wait_for(self._pool.get(), timeout=30.0)
                    except asyncio.TimeoutError as e:
                        raise RuntimeError(
                            "Timeout waiting for database connection. "
                            "All connections are in use."
                        ) from e

            yield conn

        finally:
            # Return connection to pool if pool not full and not closed
            if conn and not self._closed:
                try:
                    self._pool.put_nowait(conn)
                except asyncio.QueueFull:
                    # Pool full, close this connection
                    await conn.close()
                    async with self._lock:
                        self._created -= 1

    async def close(self):
        """Close all connections in the pool."""
        self._closed = True
        if self._pool is None:
            return
        while not self._pool.empty():
            conn = await self._pool.get()
            await conn.close()
        async with self._lock:
            self._created = 0
        logger.info("Connection pool closed")

    async def initialize(self):
        """Pre-populate pool with initial connections."""
        self._ensure_loop_objects()
        # Only pre-populate if pool is empty and we haven't created connections yet
        if self._pool.empty() and self._created == 0:
            for _ in range(self.pool_size):
                async with self._lock:
                    self._created += 1
                try:
                    conn = await self._create_connection()
                    await self._pool.put(conn)
                except Exception:
                    async with self._lock:
                        self._created -= 1
                    raise
            logger.info(
                f"Connection pool initialized with {self.pool_size} connections"
            )
        else:
            logger.debug(
                "Connection pool already has connections, skipping pre-population"
            )
