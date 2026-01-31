"""Tests for document loaders."""

import pytest
import tempfile
from pathlib import Path
from paper2skill.loaders import MultiFormatLoader


def test_markdown_loader():
    """Test loading a Markdown file."""
    # Create a test markdown file in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_doc.md"
        test_content = "# Test Document\n\nThis is a test."
        test_file.write_text(test_content)
        
        # Load the file
        content = MultiFormatLoader.load(test_file)
        
        assert content == test_content
        assert "# Test Document" in content


def test_unsupported_format():
    """Test that unsupported formats raise ValueError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.xyz"
        test_file.write_text("test")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            MultiFormatLoader.load(test_file)


def test_file_not_found():
    """Test that missing files raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        MultiFormatLoader.load("/nonexistent/file.pdf")
