"""Shared pytest fixtures for NexlifyCorp tests."""
import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Sample Document

## CONFIDENTIAL - INTERNAL

---

| Field | Value |
|-------|-------|
| **Document ID** | TEST-001 |
| **Date** | January 1, 2025 |
| **Classification** | CONFIDENTIAL |

---

## Section 1

Some content here.

## Section 2

More content here.
"""


@pytest.fixture
def sample_markdown_file(tmp_path, sample_markdown_content):
    """Create a sample markdown file for testing."""
    file_path = tmp_path / "test_doc.md"
    file_path.write_text(sample_markdown_content)
    return file_path


@pytest.fixture
def sample_risk_register_content():
    """Sample risk register markdown for testing."""
    return """# NEXLIFY CORP - INTERNAL RISK REGISTER

## CONFIDENTIAL

---

| Field | Value |
|-------|-------|
| **Document ID** | NCR-2025-Q2-001 |
| **Version** | 1.0 |
| **Date** | May 17, 2025 |
| **Classification** | CONFIDENTIAL |

---

## 1. Executive Summary

This is the executive summary.

## 2. Risk Summary

| Risk | Rating |
|------|--------|
| R-001 | HIGH |

## 3. Detailed Risks

### R-001: Supply Chain Risk

Content about supply chain risk.
"""