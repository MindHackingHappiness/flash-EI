"""
Test for the Streamlit app functionality.

This test verifies that the app.py file can be imported without errors.
"""

import pytest
import os
import sys

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_app_import():
    """Test that the app module can be imported without errors."""
    try:
        import app
        assert True, "App imported successfully"
    except ImportError as e:
        assert False, f"Failed to import app: {e}"


def test_app_has_required_components():
    """Test that the app has the required components."""
    import app
    
    # Check that the app has the required components
    assert hasattr(app, 'st'), "App should use streamlit"
    assert hasattr(app, 'EIHarness'), "App should use EIHarness"
