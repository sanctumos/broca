"""
Tests for CLI queue management tool (qtool.py).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import sys
import pytest

from cli.qtool import (
    delete_queue,
    flush_queue,
    list_queue,
    main,
    print_json,
    print_queue_items,
)


class TestQtoolFunctions:
    """Test qtool.py functions."""

    @pytest.mark.asyncio
    async def test_list_queue_json_output(self):
        """Test listing queue items with JSON output."""
        mock_items = [
            {"id": "1", "message": "test1", "status": "pending"},
            {"id": "2", "message": "test2", "status": "processing"},
        ]

        args = MagicMock()
        args.json = True

        with patch(
            "cli.qtool.get_all_queue_items", new_callable=AsyncMock
        ) as mock_get, patch("cli.qtool.print_json") as mock_print_json:
            mock_get.return_value = mock_items
            await list_queue(args)

            mock_print_json.assert_called_once_with(mock_items)

    @pytest.mark.asyncio
    async def test_list_queue_table_output(self):
        """Test listing queue items with table output."""
        mock_items = [
            {"id": "1", "message": "test1", "status": "pending"},
            {"id": "2", "message": "test2", "status": "processing"},
        ]

        args = MagicMock()
        args.json = False

        with patch(
            "cli.qtool.get_all_queue_items", new_callable=AsyncMock
        ) as mock_get, patch("cli.qtool.print_queue_items") as mock_print_table:
            mock_get.return_value = mock_items
            await list_queue(args)

            mock_print_table.assert_called_once_with(mock_items)

    @pytest.mark.asyncio
    async def test_flush_queue_all_success(self):
        """Test flushing all queue items successfully."""
        args = MagicMock()
        args.all = True
        args.id = None

        with patch(
            "cli.qtool.flush_all_queue_items", new_callable=AsyncMock
        ) as mock_flush, patch("builtins.print") as mock_print:
            mock_flush.return_value = True
            await flush_queue(args)

            mock_flush.assert_called_once_with("echo")
            mock_print.assert_called_once_with("All queue items flushed successfully")

    @pytest.mark.asyncio
    async def test_flush_queue_all_failure(self):
        """Test flushing all queue items with failure."""
        args = MagicMock()
        args.all = True
        args.id = None

        with patch(
            "cli.qtool.flush_all_queue_items", new_callable=AsyncMock
        ) as mock_flush, patch("builtins.print") as mock_print, patch(
            "sys.exit"
        ) as mock_exit:
            mock_flush.return_value = False
            await flush_queue(args)

            mock_flush.assert_called_once_with("echo")
            mock_print.assert_called_once_with(
                "Failed to flush queue items", file=sys.stderr
            )
            mock_exit.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_flush_queue_by_id_success(self):
        """Test flushing queue item by ID successfully."""
        args = MagicMock()
        args.all = False
        args.id = "123"

        with patch(
            "cli.qtool.delete_queue_item", new_callable=AsyncMock
        ) as mock_delete, patch("builtins.print") as mock_print:
            mock_delete.return_value = True
            await flush_queue(args)

            mock_delete.assert_called_once_with("123")
            mock_print.assert_called_once_with("Queue item 123 flushed successfully")

    @pytest.mark.asyncio
    async def test_flush_queue_by_id_failure(self):
        """Test flushing queue item by ID with failure."""
        args = MagicMock()
        args.all = False
        args.id = "123"

        with patch(
            "cli.qtool.delete_queue_item", new_callable=AsyncMock
        ) as mock_delete, patch("builtins.print") as mock_print, patch(
            "sys.exit"
        ) as mock_exit:
            mock_delete.return_value = False
            await flush_queue(args)

            mock_delete.assert_called_once_with("123")
            mock_print.assert_called_once_with(
                "Failed to flush queue item 123", file=sys.stderr
            )
            mock_exit.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_queue_all_success(self):
        """Test deleting all queue items successfully."""
        mock_items = [{"id": "1", "message": "test1"}, {"id": "2", "message": "test2"}]

        args = MagicMock()
        args.all = True
        args.id = None

        with patch(
            "cli.qtool.get_all_queue_items", new_callable=AsyncMock
        ) as mock_get, patch(
            "cli.qtool.delete_queue_item", new_callable=AsyncMock
        ) as mock_delete, patch(
            "builtins.print"
        ) as mock_print:
            mock_get.return_value = mock_items
            mock_delete.return_value = True

            await delete_queue(args)

            assert mock_delete.call_count == 2
            mock_print.assert_called_once_with("All queue items deleted successfully")

    @pytest.mark.asyncio
    async def test_delete_queue_all_partial_failure(self):
        """Test deleting all queue items with partial failure."""
        mock_items = [{"id": "1", "message": "test1"}, {"id": "2", "message": "test2"}]

        args = MagicMock()
        args.all = True
        args.id = None

        with patch(
            "cli.qtool.get_all_queue_items", new_callable=AsyncMock
        ) as mock_get, patch(
            "cli.qtool.delete_queue_item", new_callable=AsyncMock
        ) as mock_delete, patch(
            "builtins.print"
        ) as mock_print:
            mock_get.return_value = mock_items
            mock_delete.side_effect = [True, False]  # First succeeds, second fails

            await delete_queue(args)

            assert mock_delete.call_count == 2
            mock_print.assert_called_once_with(
                "Failed to delete queue item 2", file=sys.stderr
            )

    @pytest.mark.asyncio
    async def test_delete_queue_by_id_success(self):
        """Test deleting queue item by ID successfully."""
        args = MagicMock()
        args.all = False
        args.id = "123"

        with patch(
            "cli.qtool.delete_queue_item", new_callable=AsyncMock
        ) as mock_delete, patch("builtins.print") as mock_print:
            mock_delete.return_value = True
            await delete_queue(args)

            mock_delete.assert_called_once_with("123")
            mock_print.assert_called_once_with("Queue item 123 deleted successfully")

    @pytest.mark.asyncio
    async def test_delete_queue_by_id_failure(self):
        """Test deleting queue item by ID with failure."""
        args = MagicMock()
        args.all = False
        args.id = "123"

        with patch(
            "cli.qtool.delete_queue_item", new_callable=AsyncMock
        ) as mock_delete, patch("builtins.print") as mock_print, patch(
            "sys.exit"
        ) as mock_exit:
            mock_delete.return_value = False
            await delete_queue(args)

            mock_delete.assert_called_once_with("123")
            mock_print.assert_called_once_with(
                "Failed to delete queue item 123", file=sys.stderr
            )
            mock_exit.assert_called_once_with(1)

    def test_print_json(self):
        """Test printing JSON output."""
        mock_items = [{"id": "1", "message": "test1"}, {"id": "2", "message": "test2"}]

        with patch("builtins.print") as mock_print:
            print_json(mock_items)
            mock_print.assert_called_once()

    def test_print_queue_items(self):
        """Test printing queue items in table format."""
        mock_items = [
            {"id": "1", "message": "test1", "status": "pending"},
            {"id": "2", "message": "test2", "status": "processing"},
        ]

        with patch("builtins.print") as mock_print:
            print_queue_items(mock_items)
            # Should print header and items
            assert mock_print.call_count >= 2

    def test_print_queue_items_empty(self):
        """Test printing empty queue items."""
        with patch("builtins.print") as mock_print:
            print_queue_items([])
            mock_print.assert_called_once_with("No queue items found")

    def test_main_list_command(self):
        """Test main function with list command."""
        args = MagicMock()
        args.command = "list"
        args.json = False

        with patch("cli.qtool.list_queue", new_callable=AsyncMock), patch(
            "asyncio.run"
        ) as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_flush_command(self):
        """Test main function with flush command."""
        args = MagicMock()
        args.command = "flush"
        args.all = True
        args.id = None

        with patch("cli.qtool.flush_queue", new_callable=AsyncMock), patch(
            "asyncio.run"
        ) as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_delete_command(self):
        """Test main function with delete command."""
        args = MagicMock()
        args.command = "delete"
        args.all = True
        args.id = None

        with patch("cli.qtool.delete_queue", new_callable=AsyncMock), patch(
            "asyncio.run"
        ) as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("sys.argv", ["qtool.py", "invalid"]), patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
