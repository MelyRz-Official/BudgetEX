"""
Configuration management for the Budget Manager application.
Handles application settings, default values, and user preferences.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # UI Settings
    theme: str = "dark"  # "light" or "dark"
    window_width: int = 1400
    window_height: int = 900
    
    # Default Values
    default_scenario: str = "July-December 2025"
    default_paycheck: float = 3984.94
    
    # Behavior Settings
    auto_save: bool = False
    auto_backup: bool = True
    backup_frequency_days: int = 7
    
    # File Settings
    database_filename: str = "budget_data.db"
    backup_directory: str = "backups"
    export_directory: str = "exports"
    
    # Display Settings
    currency_symbol: str = "$"
    decimal_places: int = 2
    show_percentages: bool = True
    show_fixed_indicators: bool = True
    
    # Chart Settings
    chart_style: str = "dark_background"  # matplotlib style
    chart_colors: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize default chart colors if not provided."""
        if self.chart_colors is None:
            self.chart_colors = {
                "budgeted": "#4CAF50",
                "actual": "#FF6B6B",
                "under_budget": "#2E7D32",
                "over_budget": "#D32F2F",
                "on_target": "#1976D2",
                "not_set": "#757575"
            }


class ConfigManager:
    """Manages application configuration loading, saving, and validation."""
    
    DEFAULT_CONFIG_FILE = "budget_config.json"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file. Uses default if None.
        """
        self.config_file = Path(config_file or self.DEFAULT_CONFIG_FILE)
        self.config = AppConfig()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file, create default if not exists."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update config with loaded values
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                print(f"Configuration loaded from {self.config_file}")
            else:
                # Create default config file
                self.save_config()
                print(f"Default configuration created at {self.config_file}")
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}. Using defaults.")
            self.config = AppConfig()
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            config_dict = asdict(self.config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"Configuration saved to {self.config_file}")
            return True
            
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key name.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value.
        
        Args:
            key: Configuration key name.
            value: Value to set.
            
        Returns:
            bool: True if successful, False if key doesn't exist.
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            return True
        return False
    
    def update_config(self, **kwargs) -> None:
        """
        Update multiple configuration values.
        
        Args:
            **kwargs: Key-value pairs to update.
        """
        for key, value in kwargs.items():
            self.set(key, value)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = AppConfig()
        self.save_config()
    
    def create_directories(self) -> None:
        """Create necessary directories based on configuration."""
        directories = [
            self.config.backup_directory,
            self.config.export_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def validate_config(self) -> Dict[str, str]:
        """
        Validate configuration values.
        
        Returns:
            Dict of validation errors (empty if valid).
        """
        errors = {}
        
        # Validate theme
        if self.config.theme not in ["light", "dark"]:
            errors["theme"] = "Theme must be 'light' or 'dark'"
        
        # Validate window dimensions
        if self.config.window_width < 800:
            errors["window_width"] = "Window width must be at least 800"
        if self.config.window_height < 600:
            errors["window_height"] = "Window height must be at least 600"
        
        # Validate decimal places
        if not 0 <= self.config.decimal_places <= 4:
            errors["decimal_places"] = "Decimal places must be between 0 and 4"
        
        # Validate backup frequency
        if self.config.backup_frequency_days < 1:
            errors["backup_frequency_days"] = "Backup frequency must be at least 1 day"
        
        return errors


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config_manager.config


def save_config() -> bool:
    """Save the global configuration."""
    return config_manager.save_config()


def update_config(**kwargs) -> None:
    """Update global configuration values."""
    config_manager.update_config(**kwargs)


# Example usage and configuration presets
PRESET_CONFIGS = {
    "minimal": {
        "auto_save": True,
        "auto_backup": False,
        "show_percentages": False,
        "show_fixed_indicators": False,
    },
    "power_user": {
        "auto_save": False,
        "auto_backup": True,
        "backup_frequency_days": 1,
        "decimal_places": 4,
    },
    "presentation": {
        "theme": "light",
        "show_percentages": True,
        "show_fixed_indicators": True,
        "window_width": 1600,
        "window_height": 1000,
    }
}


def apply_preset(preset_name: str) -> bool:
    """
    Apply a configuration preset.
    
    Args:
        preset_name: Name of the preset to apply.
        
    Returns:
        bool: True if preset applied successfully.
    """
    if preset_name in PRESET_CONFIGS:
        config_manager.update_config(**PRESET_CONFIGS[preset_name])
        return True
    return False


if __name__ == "__main__":
    # Demo usage
    print("Configuration Demo")
    print("-" * 50)
    
    # Load config
    config = get_config()
    print(f"Theme: {config.theme}")
    print(f"Default scenario: {config.default_scenario}")
    print(f"Auto-save: {config.auto_save}")
    
    # Update a setting
    update_config(theme="light", auto_save=True)
    print(f"\nAfter update - Theme: {config.theme}, Auto-save: {config.auto_save}")
    
    # Validate configuration
    errors = config_manager.validate_config()
    if errors:
        print(f"\nValidation errors: {errors}")
    else:
        print("\nConfiguration is valid!")
    
    # Apply preset
    apply_preset("power_user")
    print(f"\nAfter applying 'power_user' preset:")
    print(f"Auto-backup: {config.auto_backup}")
    print(f"Decimal places: {config.decimal_places}")