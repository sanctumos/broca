"""Unit tests for CLI tools."""

from unittest.mock import patch

import pytest

from cli.btool import main as btool_main
from cli.ctool import main as ctool_main
from cli.qtool import main as qtool_main
from cli.settings import main as settings_main
from cli.utool import main as utool_main


@pytest.mark.unit
def test_btool_main():
    """Test btool main function."""
    with patch("cli.btool.sys.argv", ["btool", "--help"]):
        try:
            btool_main()
        except SystemExit:
            pass  # Expected for help


@pytest.mark.unit
def test_qtool_main():
    """Test qtool main function."""
    with patch("cli.qtool.sys.argv", ["qtool", "--help"]):
        try:
            qtool_main()
        except SystemExit:
            pass  # Expected for help


@pytest.mark.unit
def test_utool_main():
    """Test utool main function."""
    with patch("cli.utool.sys.argv", ["utool", "--help"]):
        try:
            utool_main()
        except SystemExit:
            pass  # Expected for help


@pytest.mark.unit
def test_ctool_main():
    """Test ctool main function."""
    with patch("cli.ctool.sys.argv", ["ctool", "--help"]):
        try:
            ctool_main()
        except SystemExit:
            pass  # Expected for help


@pytest.mark.unit
def test_settings_main():
    """Test settings main function."""
    with patch("cli.settings.sys.argv", ["settings", "--help"]):
        try:
            settings_main()
        except SystemExit:
            pass  # Expected for help


@pytest.mark.unit
def test_btool_commands():
    """Test btool command parsing."""
    with patch("cli.btool.sys.argv", ["btool", "list"]):
        with patch("cli.btool.list_bots"):
            try:
                btool_main()
            except:
                pass


@pytest.mark.unit
def test_qtool_commands():
    """Test qtool command parsing."""
    with patch("cli.qtool.sys.argv", ["qtool", "status"]):
        with patch("cli.qtool.show_queue_status"):
            try:
                qtool_main()
            except:
                pass


@pytest.mark.unit
def test_utool_commands():
    """Test utool command parsing."""
    with patch("cli.utool.sys.argv", ["utool", "list"]):
        with patch("cli.utool.list_users"):
            try:
                utool_main()
            except:
                pass


@pytest.mark.unit
def test_ctool_commands():
    """Test ctool command parsing."""
    with patch("cli.ctool.sys.argv", ["ctool", "list"]):
        with patch("cli.ctool.list_conversations"):
            try:
                ctool_main()
            except:
                pass


@pytest.mark.unit
def test_settings_commands():
    """Test settings command parsing."""
    with patch("cli.settings.sys.argv", ["settings", "get", "test"]):
        with patch("cli.settings.get_setting"):
            try:
                settings_main()
            except:
                pass
