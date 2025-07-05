# budget_settings.py
import tkinter as tk
from tkinter import ttk, messagebox
from config import get_config, update_config, save_config, ConfigManager

class BudgetSettings:
    """Handles the settings tab for configuration options"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.config_manager = ConfigManager()
        self.config = get_config()
        
        # Callbacks for settings changes
        self.on_theme_change_callback = None
        self.on_display_change_callback = None
        
        self.setup_settings()
    
    def setup_settings(self):
        """Setup the settings interface"""
        # Main settings frame
        main_frame = ttk.Frame(self.parent_frame, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Create all setting sections
        self._create_appearance_settings(main_frame)
        self._create_behavior_settings(main_frame)
        self._create_display_settings(main_frame)
        self._create_action_buttons(main_frame)
    
    def _create_appearance_settings(self, parent):
        """Create appearance settings section"""
        theme_frame = ttk.LabelFrame(parent, text="Appearance", padding=10)
        theme_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(theme_frame, text="Theme:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_combo = ttk.Combobox(
            theme_frame, 
            textvariable=self.theme_var,
            values=["light", "dark"], 
            state="readonly", 
            width=10
        )
        theme_combo.grid(row=0, column=1, sticky="w")
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)
    
    def _create_behavior_settings(self, parent):
        """Create behavior settings section"""
        behavior_frame = ttk.LabelFrame(parent, text="Behavior", padding=10)
        behavior_frame.pack(fill="x", pady=(0, 10))
        
        # Auto-save setting
        self.auto_save_var = tk.BooleanVar(value=self.config.auto_save)
        auto_save_check = ttk.Checkbutton(
            behavior_frame, 
            text="Auto-save changes", 
            variable=self.auto_save_var,
            command=self._on_auto_save_change
        )
        auto_save_check.pack(anchor="w", pady=2)
        
        # Auto-backup setting
        self.auto_backup_var = tk.BooleanVar(value=self.config.auto_backup)
        auto_backup_check = ttk.Checkbutton(
            behavior_frame, 
            text="Auto-backup database", 
            variable=self.auto_backup_var,
            command=self._on_auto_backup_change
        )
        auto_backup_check.pack(anchor="w", pady=2)
    
    def _create_display_settings(self, parent):
        """Create display settings section"""
        display_frame = ttk.LabelFrame(parent, text="Display", padding=10)
        display_frame.pack(fill="x", pady=(0, 10))
        
        # Show percentages setting
        self.show_percentages_var = tk.BooleanVar(value=self.config.show_percentages)
        percentages_check = ttk.Checkbutton(
            display_frame, 
            text="Show percentages", 
            variable=self.show_percentages_var,
            command=self._on_display_change
        )
        percentages_check.pack(anchor="w", pady=2)
        
        # Show fixed indicators setting
        self.show_fixed_var = tk.BooleanVar(value=self.config.show_fixed_indicators)
        fixed_check = ttk.Checkbutton(
            display_frame, 
            text="Show fixed amount indicators", 
            variable=self.show_fixed_var,
            command=self._on_display_change
        )
        fixed_check.pack(anchor="w", pady=2)
        
        # Currency settings
        self._create_currency_settings(display_frame)
    
    def _create_currency_settings(self, parent):
        """Create currency settings within display section"""
        currency_frame = ttk.Frame(parent)
        currency_frame.pack(fill="x", pady=(10, 0))
        
        # Currency symbol
        ttk.Label(currency_frame, text="Currency symbol:").pack(side="left")
        self.currency_var = tk.StringVar(value=self.config.currency_symbol)
        currency_entry = ttk.Entry(currency_frame, textvariable=self.currency_var, width=5)
        currency_entry.pack(side="left", padx=(5, 10))
        currency_entry.bind("<KeyRelease>", self._on_currency_change)
        
        # Decimal places
        ttk.Label(currency_frame, text="Decimal places:").pack(side="left")
        self.decimal_var = tk.IntVar(value=self.config.decimal_places)
        decimal_spin = ttk.Spinbox(
            currency_frame, 
            from_=0, 
            to=4,
            textvariable=self.decimal_var, 
            width=5,
            command=self._on_decimal_change
        )
        decimal_spin.pack(side="left", padx=(5, 0))
    
    def _create_action_buttons(self, parent):
        """Create action buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            button_frame, 
            text="Save Settings",
            command=self._save_settings
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Reset to Defaults",
            command=self._reset_settings
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Export Settings",
            command=self._export_settings
        ).pack(side="left")
    
    # Event handlers
    def _on_theme_change(self, event=None):
        """Handle theme change"""
        new_theme = self.theme_var.get()
        update_config(theme=new_theme)
        
        if self.on_theme_change_callback:
            self.on_theme_change_callback(new_theme)
        
        messagebox.showinfo(
            "Theme Changed", 
            f"Theme changed to {new_theme}. Some changes may require a restart."
        )
    
    def _on_auto_save_change(self):
        """Handle auto-save setting change"""
        update_config(auto_save=self.auto_save_var.get())
    
    def _on_auto_backup_change(self):
        """Handle auto-backup setting change"""
        update_config(auto_backup=self.auto_backup_var.get())
    
    def _on_display_change(self):
        """Handle display setting changes"""
        update_config(
            show_percentages=self.show_percentages_var.get(),
            show_fixed_indicators=self.show_fixed_var.get()
        )
        
        if self.on_display_change_callback:
            self.on_display_change_callback()
    
    def _on_currency_change(self, event=None):
        """Handle currency symbol change"""
        update_config(currency_symbol=self.currency_var.get())
        
        if self.on_display_change_callback:
            self.on_display_change_callback()
    
    def _on_decimal_change(self):
        """Handle decimal places change"""
        update_config(decimal_places=self.decimal_var.get())
        
        if self.on_display_change_callback:
            self.on_display_change_callback()
    
    def _save_settings(self):
        """Save all settings to config file"""
        if save_config():
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save settings.")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to defaults?"):
            self.config_manager.reset_to_defaults()
            self.refresh_settings()
            messagebox.showinfo("Settings Reset", "Settings have been reset to defaults.")
    
    def _export_settings(self):
        """Export current settings to a file"""
        from tkinter import filedialog
        import json
        from datetime import datetime
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialname=f"budget_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                # Get current config as dictionary
                config_dict = {
                    'theme': self.config.theme,
                    'auto_save': self.config.auto_save,
                    'auto_backup': self.config.auto_backup,
                    'show_percentages': self.config.show_percentages,
                    'show_fixed_indicators': self.config.show_fixed_indicators,
                    'currency_symbol': self.config.currency_symbol,
                    'decimal_places': self.config.decimal_places,
                    'chart_style': self.config.chart_style,
                    'window_width': self.config.window_width,
                    'window_height': self.config.window_height,
                    'exported_at': datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(config_dict, f, indent=2)
                
                messagebox.showinfo("Export Successful", f"Settings exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export settings: {str(e)}")
    
    def refresh_settings(self):
        """Refresh settings display with current config values"""
        self.config = get_config()  # Reload config
        
        # Update all setting variables
        self.theme_var.set(self.config.theme)
        self.auto_save_var.set(self.config.auto_save)
        self.auto_backup_var.set(self.config.auto_backup)
        self.show_percentages_var.set(self.config.show_percentages)
        self.show_fixed_var.set(self.config.show_fixed_indicators)
        self.currency_var.set(self.config.currency_symbol)
        self.decimal_var.set(self.config.decimal_places)
    
    def set_theme_change_callback(self, callback):
        """Set callback for theme changes"""
        self.on_theme_change_callback = callback
    
    def set_display_change_callback(self, callback):
        """Set callback for display changes"""
        self.on_display_change_callback = callback