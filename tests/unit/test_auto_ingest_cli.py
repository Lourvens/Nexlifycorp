"""Tests for auto-ingest CLI commands."""
import subprocess
import sys
from pathlib import Path
import pytest


PROJECT_ROOT = Path(__file__).parent.parent.parent
PYTHON = sys.executable


class TestAutoCommandsExist:
    """Test that auto commands exist and show in help."""

    def test_auto_command_in_help(self):
        """--help shows auto command."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "auto" in result.stdout

    def test_auto_public_command_in_help(self):
        """--help shows auto-public command."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "auto-public" in result.stdout

    def test_auto_internal_command_in_help(self):
        """--help shows auto-internal command."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "auto-internal" in result.stdout

    def test_manifest_command_in_help(self):
        """--help shows manifest command."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "manifest" in result.stdout

    def test_reset_command_in_help(self):
        """--help shows reset command."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "reset" in result.stdout


class TestAutoCommandHelp:
    """Test auto command help displays correctly."""

    def test_auto_help_shows_type_option(self):
        """auto --help shows --type option."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "auto", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "--type" in result.stdout

    def test_auto_public_help_shows_tickers_option(self):
        """auto-public --help shows --tickers option."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "auto-public", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "--tickers" in result.stdout

    def test_manifest_help_shows_type_filter(self):
        """manifest --help shows --type filter option."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "manifest", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "--type" in result.stdout

    def test_reset_help_shows_doc_id_argument(self):
        """reset --help shows doc_id argument."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "reset", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "DOC_ID" in result.stdout


class TestAutoCommandExamples:
    """Test auto command examples are present."""

    def test_auto_public_help_has_examples(self):
        """auto-public --help includes examples."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "auto-public", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "Example" in result.stdout or "example" in result.stdout.lower()

    def test_auto_help_has_examples(self):
        """auto --help includes examples."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "auto", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "Example" in result.stdout or "example" in result.stdout.lower()


class TestResetCommand:
    """Test reset command functionality."""

    def test_reset_requires_doc_id(self):
        """reset without doc_id shows error."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "reset"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0


class TestManifestCommand:
    """Test manifest command functionality."""

    def test_manifest_runs_without_error(self):
        """manifest command runs (may show empty if no manifest)."""
        result = subprocess.run(
            [PYTHON, "scripts/ingest.py", "manifest"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        # Should not crash even if manifest doesn't exist or is empty
        assert result.returncode == 0