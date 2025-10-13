#!/usr/bin/env python3
"""
Test runner script for Broca2 test suite.

This script provides convenient commands for running different types of tests:
- Unit tests
- Integration tests
- End-to-end tests
- All tests
- Coverage reports
- Performance tests
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def run_unit_tests(verbose: bool = False) -> int:
    """Run unit tests."""
    cmd = ["python", "-m", "pytest", "tests/unit/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose: bool = False) -> int:
    """Run integration tests."""
    cmd = ["python", "-m", "pytest", "tests/integration/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Integration Tests")


def run_e2e_tests(verbose: bool = False) -> int:
    """Run end-to-end tests."""
    cmd = ["python", "-m", "pytest", "tests/e2e/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "End-to-End Tests")


def run_all_tests(verbose: bool = False) -> int:
    """Run all tests."""
    cmd = ["python", "-m", "pytest", "tests/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "All Tests")


def run_coverage_tests(verbose: bool = False) -> int:
    """Run tests with coverage reporting."""
    cmd = [
        "python",
        "-m",
        "pytest",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-fail-under=80",
        "tests/",
    ]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Coverage Tests")


def run_performance_tests(verbose: bool = False) -> int:
    """Run performance tests."""
    cmd = ["python", "-m", "pytest", "-m", "performance", "tests/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Performance Tests")


def run_slow_tests(verbose: bool = False) -> int:
    """Run slow tests."""
    cmd = ["python", "-m", "pytest", "-m", "slow", "tests/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Slow Tests")


def run_async_tests(verbose: bool = False) -> int:
    """Run async tests."""
    cmd = ["python", "-m", "pytest", "-m", "async", "tests/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Async Tests")


def run_database_tests(verbose: bool = False) -> int:
    """Run database tests."""
    cmd = ["python", "-m", "pytest", "-m", "database", "tests/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Database Tests")


def run_external_tests(verbose: bool = False) -> int:
    """Run external service tests."""
    cmd = ["python", "-m", "pytest", "-m", "external", "tests/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "External Service Tests")


def lint_code() -> int:
    """Run code linting."""
    cmd = ["python", "-m", "ruff", "check", "."]
    return run_command(cmd, "Code Linting")


def format_code() -> int:
    """Run code formatting."""
    cmd = ["python", "-m", "black", "."]
    return run_command(cmd, "Code Formatting")


def type_check() -> int:
    """Run type checking."""
    cmd = ["python", "-m", "mypy", "."]
    return run_command(cmd, "Type Checking")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Broca2 Test Runner")
    parser.add_argument(
        "command",
        choices=[
            "unit",
            "integration",
            "e2e",
            "all",
            "coverage",
            "performance",
            "slow",
            "async",
            "database",
            "external",
            "lint",
            "format",
            "type",
        ],
        help="Test command to run",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["DEBUG_MODE"] = "true"
    os.environ["MESSAGE_MODE"] = "echo"

    # Run the appropriate command
    commands = {
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "e2e": run_e2e_tests,
        "all": run_all_tests,
        "coverage": run_coverage_tests,
        "performance": run_performance_tests,
        "slow": run_slow_tests,
        "async": run_async_tests,
        "database": run_database_tests,
        "external": run_external_tests,
        "lint": lint_code,
        "format": format_code,
        "type": type_check,
    }

    exit_code = commands[args.command](args.verbose)

    if exit_code == 0:
        print(f"\n[SUCCESS] {args.command.title()} completed successfully!")
    else:
        print(f"\n[FAILED] {args.command.title()} failed with exit code {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
