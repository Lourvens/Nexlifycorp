"""Unit tests for scripts/ingest.py CLI with Click.

Tests CLI structure and command routing without requiring Qdrant.
"""
import subprocess
import sys
from pathlib import Path
import pytest


PROJECT_ROOT = Path(__file__).parent.parent.parent
PYTHON = sys.executable


# =============================================================================
# Test CLI Structure (no Qdrant required)
# =============================================================================

class TestCLIStructure:
    """Test CLI structure without requiring Qdrant connection."""

    def test_cli_help_shows_all_commands(self):
        """CLI --help shows all available commands."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "public" in result.stdout
        assert "internal" in result.stdout
        assert "stats" in result.stdout
        assert "list" in result.stdout
        assert "clear" in result.stdout
        assert "auto" in result.stdout
        assert "manifest" in result.stdout

    def test_public_help_shows_ticker_argument(self):
        """public --help shows ticker as argument."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "public", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "ticker" in result.stdout.lower()

    def test_internal_help_shows_arguments(self):
        """internal --help shows doc_id and doc_type arguments."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "internal", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "doc_id" in result.stdout.lower()
        assert "doc_type" in result.stdout.lower()

    def test_list_help(self):
        """list --help works."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "list", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0

    def test_stats_help(self):
        """stats --help works."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "stats", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0

    def test_clear_help_shows_confirm_flag(self):
        """clear --help shows --confirm flag."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "clear", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "--confirm" in result.stdout


# =============================================================================
# Test Command Routing
# =============================================================================

class TestCommandRouting:
    """Verify commands route to correct handlers."""

    def test_public_requires_ticker(self):
        """public without ticker shows error."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "public"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0

    def test_internal_requires_doc_id_and_type(self):
        """internal without required args shows error."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "internal"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0

    def test_clear_requires_confirm(self):
        """clear without --confirm is rejected."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "clear"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=60,
        )
        assert result.returncode == 1
        output = result.stdout + result.stderr
        assert "--confirm" in output

    def test_unknown_command_returns_error(self):
        """Unknown command shows error."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "unknown_command"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0


# =============================================================================
# Test CLI Group
# =============================================================================

class TestCLIGroup:
    """Test main CLI group behavior."""

    def test_cli_no_args_shows_help(self):
        """CLI with no args shows help (Click returns exit code 2 for no args)."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        # Click returns exit code 2 when no command given, but still shows help
        assert result.returncode in [0, 2]
        assert "NexlifyCorp" in result.stdout or "NexlifyCorp" in result.stderr

    def test_all_commands_exist(self):
        """All 10 commands are accessible."""
        commands = ["public", "internal", "stats", "list", "clear", "auto", "auto-public", "auto-internal", "manifest", "reset"]
        for cmd in commands:
            result = subprocess.run(
                [PYTHON, "scripts/ingest.py", cmd, "--help"],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode == 0, f"Command {cmd} should exist"


# =============================================================================
# Test Argument Validation
# =============================================================================

class TestArgumentValidation:
    """Test that arguments are validated correctly."""

    def test_internal_without_content_or_file(self):
        """internal without content or file shows error."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "internal", "DOC1", "board_memo"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=60,
        )
        assert result.returncode == 1
        output = result.stdout + result.stderr
        assert "Must provide" in output

    def test_public_form_choice(self):
        """public --form only accepts 10-K or 10-Q."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "public", "NVDA", "--form", "10-X"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0


# =============================================================================
# Test File Input
# =============================================================================

class TestFileInput:
    """Test file-based input handling."""

    def test_internal_with_nonexistent_file(self):
        """internal with non-existent file shows error."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "internal", "DOC1", "board_memo",
             "--file", "/nonexistent/path.md"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0