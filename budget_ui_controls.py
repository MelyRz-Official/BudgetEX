# budget_ui_controls.py - Manages the control panel UI
import tkinter as tk
from tkinter import ttk
from budget_models import ViewMode

class ControlsManager:
    """Manages the control panel at the top of the budget tab"""
    
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
        self.controls_frame = None
        self.monthly_total_label = None
    
    def create_controls(self):
        """Create all control widgets"""
        # Controls frame
        self.controls_frame = ttk.Frame(self.parent_frame)
        self.controls_frame.pack(fill="x", padx=10, pady=5)
        
        self._create_first_control_row()
        self._create_second_control_row()
        self._create_third_control_row()
    
    def _create_first_control_row(self):
        """Create first row: scenario, period, view mode"""
        control_row1 = ttk.Frame(self.controls_frame)
        control_row1.pack(fill="x", pady=(0, 5))
        
        # Scenario selection
        ttk.Label(control_row1, text="Budget Scenario:").pack(side="left", padx=5)
        self.app.scenario_var = tk.StringVar(value=self.app.current_scenario_name)
        scenario_combo = ttk.Combobox(control_row1, textvariable=self.app.scenario_var,
                                     values=self.app.budget_data.get_scenario_names(),
                                     state="readonly", width=25)
        scenario_combo.pack(side="left", padx=5)
        scenario_combo.bind("<<ComboboxSelected>>", self.app.on_scenario_change)
        
        # Period selector
        ttk.Label(control_row1, text="Period:").pack(side="left", padx=(20, 5))
        self.app.period_var = tk.StringVar()
        self.app.period_combo = ttk.Combobox(control_row1, textvariable=self.app.period_var,
                                           state="readonly", width=20)
        self.app.period_combo.pack(side="left", padx=5)
        self.app.period_combo.bind("<<ComboboxSelected>>", self.app.on_period_change)
        
        # View mode selection
        ttk.Label(control_row1, text="View:").pack(side="left", padx=(20, 5))
        self.app.view_var = tk.StringVar(value=self.app.view_mode.value)
        view_combo = ttk.Combobox(control_row1, textvariable=self.app.view_var,
                                 values=[mode.value for mode in ViewMode],
                                 state="readonly", width=15)
        view_combo.pack(side="left", padx=5)
        view_combo.bind("<<ComboboxSelected>>", self.app.on_view_change)
    
    # def _create_second_control_row(self):
    #     """Create second row: paycheck inputs"""
    #     control_row2 = ttk.Frame(self.controls_frame)
    #     control_row2.pack(fill="x", pady=(0, 5))
        
    #     # First paycheck input
    #     ttk.Label(control_row2, text="1st Paycheck (6th): $").pack(side="left", padx=5)
    #     first_entry = ttk.Entry(control_row2, textvariable=self.app.first_paycheck, width=12)
    #     first_entry.pack(side="left", padx=5)
    #     first_entry.bind("<KeyRelease>", lambda e: self.app.on_paycheck_change())
        
    #     # Second paycheck input
    #     ttk.Label(control_row2, text="2nd Paycheck (21st): $").pack(side="left", padx=(20, 5))
    #     second_entry = ttk.Entry(control_row2, textvariable=self.app.second_paycheck, width=12)
    #     second_entry.pack(side="left", padx=5)
    #     second_entry.bind("<KeyRelease>", lambda e: self.app.on_paycheck_change())
        
    #     # Monthly total display
    #     self.monthly_total_label = ttk.Label(control_row2, text="Monthly Total: $4319.19", 
    #                                        font=("", 10, "bold"), foreground="cyan")
    #     self.monthly_total_label.pack(side="left", padx=(20, 5))
    def _create_second_control_row(self):
        """Create second row: paycheck inputs"""
        control_row2 = ttk.Frame(self.controls_frame)
        control_row2.pack(fill="x", pady=(0, 5))
        
        # First paycheck input
        ttk.Label(control_row2, text="1st Paycheck (6th): $").pack(side="left", padx=5)
        first_entry = ttk.Entry(control_row2, textvariable=self.app.first_paycheck, width=12)
        first_entry.pack(side="left", padx=5)
        first_entry.bind("<KeyRelease>", lambda e: self.app.on_paycheck_change())
        
        # Second paycheck input
        ttk.Label(control_row2, text="2nd Paycheck (21st): $").pack(side="left", padx=(20, 5))
        second_entry = ttk.Entry(control_row2, textvariable=self.app.second_paycheck, width=12)
        second_entry.pack(side="left", padx=5)
        second_entry.bind("<KeyRelease>", lambda e: self.app.on_paycheck_change())
        
        # Add traces for programmatic changes
        self.app.first_paycheck.trace_add("write", lambda *args: self.app.on_paycheck_change())
        self.app.second_paycheck.trace_add("write", lambda *args: self.app.on_paycheck_change())
        
        # Monthly total display
        self.monthly_total_label = ttk.Label(control_row2, text="Monthly Total: $4319.19", 
                                        font=("", 10, "bold"), foreground="cyan")
        self.monthly_total_label.pack(side="left", padx=(20, 5))
    
    def _create_third_control_row(self):
        """Create third row: buttons"""
        control_row3 = ttk.Frame(self.controls_frame)
        control_row3.pack(fill="x")
        
        # Buttons
        button_frame = ttk.Frame(control_row3)
        button_frame.pack(side="left")
        
        # Save button
        ttk.Button(button_frame, text="Save Data", 
                  command=self.app.save_data).pack(side="left", padx=2)
        
        # CSV operations dropdown
        self._create_csv_menu(button_frame)
        
        # Action buttons
        ttk.Button(button_frame, text="Clear All", 
                  command=self.app.clear_all_spending).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Create Period", 
                  command=self.app.create_manual_period).pack(side="left", padx=2)
        
        # Auto-save indicator
        if self.app.config.auto_save:
            ttk.Label(button_frame, text="Auto-save: ON", 
                     foreground="green").pack(side="left", padx=10)
    
    def _create_csv_menu(self, parent):
        """Create CSV operations dropdown menu"""
        csv_menu = ttk.Menubutton(parent, text="CSV Backup", direction="below")
        csv_menu.pack(side="left", padx=2)
        
        csv_submenu = tk.Menu(csv_menu, tearoff=0)
        csv_submenu.add_command(label="Export to CSV", command=self.app.export_csv)
        csv_submenu.add_command(label="Import from CSV", command=self.app.import_from_csv)
        csv_submenu.add_command(label="Create CSV Backup", command=self.app.manual_csv_backup)
        csv_submenu.add_separator()
        csv_submenu.add_command(label="Show Data Location", command=self.app.show_data_location)
        csv_menu.config(menu=csv_submenu)
    
    def update_monthly_total(self):
        """Update monthly total display"""
        try:
            first = self.app.first_paycheck.get()
            second = self.app.second_paycheck.get()
            total = first + second
            self.monthly_total_label.config(text=f"Monthly Total: ${total:.2f}")
        except (ValueError, tk.TclError):
            self.monthly_total_label.config(text="Monthly Total: $0.00")