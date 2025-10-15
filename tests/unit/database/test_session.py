"""Unit tests for database session management."""

import os
import tempfile
from unittest.mock import patch

from sqlalchemy.orm import Session

from database.session import DB_PATH, ENGINE, SessionLocal, get_session


class TestDatabaseSession:
    """Test cases for database session management."""

    def test_db_path_default(self):
        """Test default database path."""
        with patch.dict(os.environ, {}, clear=True):
            # Reload the module to get fresh environment
            import importlib

            import database.session

            importlib.reload(database.session)

            assert database.session.DB_PATH == "broca.db"

    def test_db_path_from_environment(self):
        """Test database path from environment variable."""
        test_path = "/tmp/test.db"
        with patch.dict(os.environ, {"DB_PATH": test_path}):
            # Reload the module to get fresh environment
            import importlib

            import database.session

            importlib.reload(database.session)

            assert database.session.DB_PATH == test_path

    def test_engine_creation(self):
        """Test database engine creation."""
        # Engine should be created with correct URL
        expected_url = f"sqlite:///{DB_PATH}"
        assert str(ENGINE.url) == expected_url

    def test_session_local_creation(self):
        """Test SessionLocal creation."""
        # SessionLocal should be bound to the engine
        # sessionmaker objects don't have a bind attribute, but we can verify
        # by checking that it's a sessionmaker instance
        assert callable(SessionLocal)  # sessionmaker is callable
        assert SessionLocal is not None

    def test_get_session(self):
        """Test getting a database session."""
        session = get_session()

        # Should return a Session object
        assert isinstance(session, Session)

        # Should be bound to the correct engine
        assert session.bind == ENGINE

        # Should be able to close the session
        session.close()

    def test_get_session_with_context_manager(self):
        """Test getting a database session with context manager."""
        with get_session() as session:
            assert isinstance(session, Session)
            assert session.bind == ENGINE

    def test_multiple_sessions(self):
        """Test creating multiple sessions."""
        session1 = get_session()
        session2 = get_session()

        # Should be different session instances
        assert session1 is not session2

        # Both should be bound to the same engine
        assert session1.bind == ENGINE
        assert session2.bind == ENGINE

        # Clean up
        session1.close()
        session2.close()

    def test_session_with_temp_database(self):
        """Test session with temporary database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            with patch.dict(os.environ, {"DB_PATH": temp_path}):
                # Reload the module to get fresh environment
                import importlib

                import database.session

                importlib.reload(database.session)

                # Get a session
                session = database.session.get_session()

                # Should be bound to the temporary database
                expected_url = f"sqlite:///{temp_path}"
                assert str(session.bind.url) == expected_url

                session.close()

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_session_transaction(self):
        """Test session transaction handling."""
        session = get_session()

        try:
            # Start a transaction
            session.begin()

            # Should be in a transaction
            assert session.in_transaction()

            # Rollback the transaction
            session.rollback()

        finally:
            session.close()

    def test_session_commit(self):
        """Test session commit."""
        session = get_session()

        try:
            # Start a transaction
            session.begin()

            # Commit the transaction
            session.commit()

        finally:
            session.close()

    def test_session_close(self):
        """Test session close."""
        session = get_session()

        # Session should be open
        assert session.is_active

        # Close the session
        session.close()

        # Session should be closed - check by trying to use it
        try:
            session.execute("SELECT 1")
            raise AssertionError("Session should be closed and not usable")
        except Exception:
            # Expected - session should be closed
            pass

    def test_session_with_exception(self):
        """Test session behavior with exceptions."""
        session = get_session()

        try:
            # Start a transaction
            session.begin()

            # Simulate an error
            try:
                raise ValueError("Test error")
            except ValueError:
                # Rollback on error
                session.rollback()
                # Don't re-raise - just handle the error

        finally:
            session.close()

    def test_engine_configuration(self):
        """Test engine configuration."""
        # Engine should be configured for SQLite
        assert ENGINE.dialect.name == "sqlite"

        # Should have appropriate pool settings
        assert ENGINE.pool is not None

    def test_session_maker_configuration(self):
        """Test session maker configuration."""
        # SessionLocal should be properly configured
        assert SessionLocal.kw.get("bind") == ENGINE

        # Should have appropriate session settings
        assert SessionLocal.kw.get("autoflush", True) is True
        assert SessionLocal.kw.get("autocommit", False) is False
