"""
Unit tests for configuration management.
Simple tests that can run with minimal dependencies.
"""

import pytest
import tempfile
import json
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import ConfigManager, AppConfig, get_config, update_config


class TestAppConfig:
    """Test AppConfig dataclass."""
    
    def test_app_config_defaults(self):
        """Test AppConfig with default values."""
        config = AppConfig()
        
        assert config.theme == "dark"
        assert config.window_width == 1400
        assert config.window_height == 900
        assert config.default_scenario == "July-December 2025"
        assert config.auto_save is False
        assert config.currency_symbol == "$"
        assert config.decimal_places == 2
    
    def test_app_config_custom_values(self):
        """Test AppConfig with custom values."""
        config = AppConfig(
            theme="light",
            window_width=1600,
            auto_save=True,
            currency_symbol="€"
        )
        
        assert config.theme == "light"
        assert config.window_width == 1600
        assert config.auto_save is True
        assert config.currency_symbol == "€"
    
    def test_app_config_chart_colors_default(self):
        """Test that chart colors are initialized properly."""
        config = AppConfig()
        
        assert config.chart_colors is not None
        assert "budgeted" in config.chart_colors
        assert "actual" in config.chart_colors
        assert "under_budget" in config.chart_colors
        assert "over_budget" in config.chart_colors


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            assert manager.config_file == config_file
            assert isinstance(manager.config, AppConfig)
    
    def test_config_file_creation(self):
        """Test that config file is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "new_config.json"
            
            # Ensure file doesn't exist
            assert not config_file.exists()
            
            manager = ConfigManager(str(config_file))
            
            # File should be created
            assert config_file.exists()
            
            # File should contain valid JSON
            with open(config_file) as f:
                data = json.load(f)
                assert "theme" in data
                assert "window_width" in data
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            # Modify config
            manager.config.theme = "light"
            manager.config.auto_save = True
            manager.config.decimal_places = 3
            
            # Save config
            result = manager.save_config()
            assert result is True
            
            # Create new manager to test loading
            manager2 = ConfigManager(str(config_file))
            
            # Verify loaded values
            assert manager2.config.theme == "light"
            assert manager2.config.auto_save is True
            assert manager2.config.decimal_places == 3
    
    def test_get_config_value(self):
        """Test getting configuration values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            # Test existing key
            result = manager.get("theme")
            assert result == "dark"
            
            # Test with default
            result = manager.get("nonexistent_key", "default_value")
            assert result == "default_value"
    
    def test_set_config_value(self):
        """Test setting configuration values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            # Test setting existing key
            result = manager.set("theme", "light")
            assert result is True
            assert manager.config.theme == "light"
            
            # Test setting non-existent key
            result = manager.set("nonexistent_key", "value")
            assert result is False
    
    def test_update_config_multiple_values(self):
        """Test updating multiple configuration values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            manager.update_config(
                theme="light",
                auto_save=True,
                decimal_places=4
            )
            
            assert manager.config.theme == "light"
            assert manager.config.auto_save is True
            assert manager.config.decimal_places == 4
    
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            # Modify config
            manager.config.theme = "light"
            manager.config.auto_save = True
            
            # Reset to defaults
            manager.reset_to_defaults()
            
            # Verify defaults are restored
            assert manager.config.theme == "dark"
            assert manager.config.auto_save is False
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            errors = manager.validate_config()
            assert len(errors) == 0
    
    def test_validate_config_invalid(self):
        """Test configuration validation with invalid values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_file))
            
            # Set invalid values
            manager.config.theme = "invalid_theme"
            manager.config.window_width = 500  # Too small
            manager.config.decimal_places = 10  # Too many
            
            errors = manager.validate_config()
            assert len(errors) > 0
            assert any("theme" in error.lower() for error in errors.values())
            assert any("width" in error.lower() for error in errors.values())


class TestConfigUtilityFunctions:
    """Test utility functions in config module."""
    
    def test_get_config_function(self):
        """Test get_config utility function."""
        config = get_config()
        assert isinstance(config, AppConfig)
    
    def test_update_config_function(self):
        """Test update_config utility function."""
        original_theme = get_config().theme
        
        try:
            # Update config
            update_config(theme="light")
            
            # Verify change
            updated_config = get_config()
            assert updated_config.theme == "light"
            
        finally:
            # Restore original value
            update_config(theme=original_theme)


def test_config_integration():
    """Simple integration test for configuration system."""
    # Test basic configuration operations
    config = AppConfig()
    assert config.theme in ["light", "dark"]
    assert config.window_width > 0
    assert config.window_height > 0
    
    # Test that required fields exist
    required_fields = [
        'theme', 'window_width', 'window_height', 'default_scenario',
        'auto_save', 'currency_symbol', 'decimal_places'
    ]
    
    for field in required_fields:
        assert hasattr(config, field), f"Missing required field: {field}"
    
    print("✅ Configuration integration test passed!")


if __name__ == "__main__":
    # Simple test runner for debugging
    test_config_integration()
    print("All basic config tests completed!")