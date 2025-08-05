# # budget_app_main.py
# import tkinter as tk
# from tkinter import ttk, messagebox, filedialog
# from datetime import datetime
# import csv

# # Import our separated modules
# from budget_models import BudgetData, ViewMode
# from budget_database import BudgetDatabase
# from budget_calculator import BudgetCalculator
# from budget_dashboard import BudgetDashboard
# from budget_settings import BudgetSettings
# from budget_history_tab import BudgetHistoryTab
# from budget_time_tracker import PeriodType
# from config import get_config

# class BudgetApp:
#     def __init__(self, root):
#         self.root = root
#         self.config = get_config()
        
#         # Initialize data models
#         self.budget_data = BudgetData()
#         self.database = BudgetDatabase(self.config.database_filename)
        
#         # Application state
#         self.current_scenario_name = self.config.default_scenario
#         self.view_mode = ViewMode.MONTHLY
#         self.first_paycheck = tk.DoubleVar(value=2000.0)  # Default first paycheck
#         self.second_paycheck = tk.DoubleVar(value=1984.94)  # Default second paycheck
#         self.actual_spending = {}  # Dict[str, Dict[ViewMode, tk.DoubleVar]]
        
#         # Initialize UI
#         self.setup_window()
#         self.create_widgets()
#         self.load_data()
#         self.refresh_period_list()
#         self.update_calculations()
    
#     def update_income_label(self):
#         """Update income label - no longer needed with paycheck system but kept for compatibility"""
#         # This method is kept for compatibility but doesn't need to do anything
#         # since we now have separate paycheck input fields
#         pass
    
#     def setup_window(self):
#         """Setup main window"""
#         self.root.title("Personal Budget Manager")
#         self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        
#         # Set up proper window closing
#         self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
#         # Apply theme if available
#         try:
#             import sv_ttk
#             sv_ttk.set_theme(self.config.theme)
#         except ImportError:
#             print("Sun Valley theme not found. Using default theme.")
    
#     def on_closing(self):
#         """Handle window closing - save data and cleanup"""
#         try:
#             # Auto-save current data before closing
#             if self.config.auto_save:
#                 self.auto_save_data()
#                 print("Auto-saved data before closing")
            
#             # Ask user if they want to save if auto-save is disabled
#             elif messagebox.askyesno("Save Before Exit", "Do you want to save your current data before exiting?"):
#                 self.save_data()
            
#             # Close matplotlib figures to prevent warnings
#             try:
#                 import matplotlib.pyplot as plt
#                 plt.close('all')
#             except:
#                 pass
            
#             # Destroy the window
#             self.root.quit()
#             self.root.destroy()
            
#         except Exception as e:
#             print(f"Error during cleanup: {e}")
#             # Force close even if there's an error
#             self.root.quit()
#             self.root.destroy()
    
#     def create_widgets(self):
#         """Create main UI widgets"""
#         # Create notebook for tabs
#         self.notebook = ttk.Notebook(self.root)
#         self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
#         # Budget Overview Tab
#         self.budget_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.budget_frame, text="Budget Overview")
#         self.create_budget_tab()
        
#         # Dashboard Tab
#         self.dashboard_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.dashboard_frame, text="Dashboard")
#         self.dashboard = BudgetDashboard(self.dashboard_frame, self.config)
#         self.dashboard.set_refresh_callback(self.refresh_dashboard)
        
#         # Settings Tab
#         self.settings_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.settings_frame, text="Settings")
#         self.settings = BudgetSettings(self.settings_frame)
#         self.settings.set_theme_change_callback(self.on_theme_change)
#         self.settings.set_display_change_callback(self.update_calculations)
        
#         # History Tab
#         self.history_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.history_frame, text="Budget History")
#         self.history_tab = BudgetHistoryTab(self.history_frame, self.config, self.get_current_budget_data, self.database)
    
#     def create_budget_tab(self):
#         """Create the budget overview tab"""
#         # Controls frame
#         controls_frame = ttk.Frame(self.budget_frame)
#         controls_frame.pack(fill="x", padx=10, pady=5)
        
#         # First row of controls
#         control_row1 = ttk.Frame(controls_frame)
#         control_row1.pack(fill="x", pady=(0, 5))
        
#         # Scenario selection
#         ttk.Label(control_row1, text="Budget Scenario:").pack(side="left", padx=5)
#         self.scenario_var = tk.StringVar(value=self.current_scenario_name)
#         scenario_combo = ttk.Combobox(control_row1, textvariable=self.scenario_var,
#                                      values=self.budget_data.get_scenario_names(),
#                                      state="readonly", width=25)
#         scenario_combo.pack(side="left", padx=5)
#         scenario_combo.bind("<<ComboboxSelected>>", self.on_scenario_change)
        
#         # Period selector
#         ttk.Label(control_row1, text="Period:").pack(side="left", padx=(20, 5))
#         self.period_var = tk.StringVar()
#         self.period_combo = ttk.Combobox(control_row1, textvariable=self.period_var,
#                                         state="readonly", width=20)
#         self.period_combo.pack(side="left", padx=5)
#         self.period_combo.bind("<<ComboboxSelected>>", self.on_period_change)
        
#         # View mode selection
#         ttk.Label(control_row1, text="View:").pack(side="left", padx=(20, 5))
#         self.view_var = tk.StringVar(value=self.view_mode.value)
#         view_combo = ttk.Combobox(control_row1, textvariable=self.view_var,
#                                  values=[mode.value for mode in ViewMode],
#                                  state="readonly", width=15)
#         view_combo.pack(side="left", padx=5)
#         view_combo.bind("<<ComboboxSelected>>", self.on_view_change)
        
#         # Second row of controls - Paycheck inputs
#         control_row2 = ttk.Frame(controls_frame)
#         control_row2.pack(fill="x", pady=(0, 5))
        
#         # First paycheck input
#         ttk.Label(control_row2, text="1st Paycheck (6th): $").pack(side="left", padx=5)
#         first_entry = ttk.Entry(control_row2, textvariable=self.first_paycheck, width=12)
#         first_entry.pack(side="left", padx=5)
#         first_entry.bind("<KeyRelease>", lambda e: self.on_paycheck_change())
        
#         # Second paycheck input
#         ttk.Label(control_row2, text="2nd Paycheck (21st): $").pack(side="left", padx=(20, 5))
#         second_entry = ttk.Entry(control_row2, textvariable=self.second_paycheck, width=12)
#         second_entry.pack(side="left", padx=5)
#         second_entry.bind("<KeyRelease>", lambda e: self.on_paycheck_change())
        
#         # Monthly total display
#         self.monthly_total_label = ttk.Label(control_row2, text="Monthly Total: $3984.94", 
#                                            font=("", 10, "bold"), foreground="cyan")
#         self.monthly_total_label.pack(side="left", padx=(20, 5))
        
#         # Third row of controls - Buttons
#         control_row3 = ttk.Frame(controls_frame)
#         control_row3.pack(fill="x")
        
#         # Buttons
#         button_frame = ttk.Frame(control_row3)
#         button_frame.pack(side="left")
        
#         ttk.Button(button_frame, text="Save Data", command=self.save_data).pack(side="left", padx=2)
        
#         # CSV Backup dropdown (removed separate Export CSV button)
#         csv_menu = ttk.Menubutton(button_frame, text="CSV Backup", direction="below")
#         csv_menu.pack(side="left", padx=2)
        
#         csv_submenu = tk.Menu(csv_menu, tearoff=0)
#         csv_submenu.add_command(label="Export to CSV", command=self.export_csv)
#         csv_submenu.add_command(label="Import from CSV", command=self.import_from_csv)
#         csv_submenu.add_command(label="Create CSV Backup", command=self.manual_csv_backup)
#         csv_submenu.add_separator()
#         csv_submenu.add_command(label="Show Data Location", command=self.show_data_location)
#         csv_menu.config(menu=csv_submenu)
        
#         ttk.Button(button_frame, text="Clear All", command=self.clear_all_spending).pack(side="left", padx=2)
        
#         # Auto-save indicator
#         if self.config.auto_save:
#             ttk.Label(button_frame, text="Auto-save: ON", foreground="green").pack(side="left", padx=10)
        
#         # Categories table
#         self.create_categories_table()
        
#         # Summary
#         self.create_summary_section()
    
#     def create_categories_table(self):
#         """Create the categories table"""
#         # Table frame
#         table_frame = ttk.Frame(self.budget_frame)
#         table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
#         # Headers
#         headers = ["Category", "% of Income", "Budgeted ($)", "Actual Spent ($)", "Difference ($)", "Status"]
#         for i, header in enumerate(headers):
#             label = ttk.Label(table_frame, text=header, font=("", 10, "bold"))
#             label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
#         # Configure grid weights
#         for i in range(len(headers)):
#             table_frame.columnconfigure(i, weight=1)
        
#         # Store references for updating
#         self.category_labels = {}
#         self.spending_entries = {}
#         self.table_frame = table_frame
        
#         self.create_category_rows()
    
#     def create_category_rows(self):
#         """Create rows for each category"""
#         # Clear existing rows (except header)
#         for widget in self.table_frame.winfo_children()[6:]:  # Skip header row
#             widget.destroy()
        
#         # Clear references
#         self.category_labels.clear()
#         self.spending_entries.clear()
#         self.actual_spending.clear()
        
#         # Get current scenario
#         scenario = self.budget_data.get_scenario(self.current_scenario_name)
        
#         # Create rows
#         row = 1
#         for category_name in scenario.get_all_categories().keys():
#             # Initialize spending variables for all view modes
#             self.actual_spending[category_name] = {
#                 ViewMode.FIRST_PAYCHECK: tk.DoubleVar(value=0.0),
#                 ViewMode.SECOND_PAYCHECK: tk.DoubleVar(value=0.0),
#                 ViewMode.MONTHLY: tk.DoubleVar(value=0.0)
#             }
            
#             # Category name
#             cat_label = ttk.Label(self.table_frame, text=category_name)
#             cat_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
#             self.category_labels[f"{category_name}_name"] = cat_label
            
#             # Percentage
#             perc_label = ttk.Label(self.table_frame, text="")
#             perc_label.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category_name}_perc"] = perc_label
            
#             # Budgeted amount
#             budget_label = ttk.Label(self.table_frame, text="")
#             budget_label.grid(row=row, column=2, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category_name}_budget"] = budget_label
            
#             # Actual spent (editable) - uses current view mode
#             actual_entry = ttk.Entry(self.table_frame, textvariable=self.actual_spending[category_name][self.view_mode], width=12)
#             actual_entry.grid(row=row, column=3, padx=5, pady=2, sticky="ew")
#             actual_entry.bind("<KeyRelease>", lambda e, cat=category_name: self.on_spending_change(cat))
#             self.spending_entries[category_name] = actual_entry
            
#             # Difference
#             diff_label = ttk.Label(self.table_frame, text="")
#             diff_label.grid(row=row, column=4, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category_name}_diff"] = diff_label
            
#             # Status
#             status_label = ttk.Label(self.table_frame, text="")
#             status_label.grid(row=row, column=5, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category_name}_status"] = status_label
            
#             row += 1
    
#     def create_summary_section(self):
#         """Create the summary section"""
#         summary_frame = ttk.LabelFrame(self.budget_frame, text="Summary", padding=10)
#         summary_frame.pack(fill="x", padx=10, pady=5)
        
#         self.summary_labels = {}
#         summary_row = ttk.Frame(summary_frame)
#         summary_row.pack(fill="x")
        
#         # Create summary labels
#         labels = ["Total Budgeted:", "Total Spent:", "Remaining:", "Over/Under:"]
#         for i, label in enumerate(labels):
#             ttk.Label(summary_row, text=label).grid(row=0, column=i*2, padx=10, sticky="e")
#             self.summary_labels[label] = ttk.Label(summary_row, text="$0.00", font=("", 11, "bold"))
#             self.summary_labels[label].grid(row=0, column=i*2+1, padx=10, sticky="w")
    
#     def load_period_data(self, period_id=None):
#         """Load budget data for a specific period, defaulting to current month"""
#         if period_id is None:
#             # Default to current month
#             period_id = self.get_current_month_period_id()
        
#         # Check if we have a snapshot for this period
#         time_tracker = self.history_tab.get_time_tracker()
#         snapshot = time_tracker.get_snapshot(period_id)
        
#         if snapshot:
#             # Load data from snapshot
#             self.first_paycheck.set(snapshot.income / 2)  # Assume even split for now
#             self.second_paycheck.set(snapshot.income / 2)
            
#             # Load category spending
#             for category_name, category_data in snapshot.category_data.items():
#                 if category_name in self.actual_spending:
#                     # For now, put all actual spending in monthly view
#                     self.actual_spending[category_name][ViewMode.MONTHLY].set(category_data['actual'])
            
#             self.update_calculations()
#             return True
#         else:
#             # No saved data for this period, try loading from regular database
#             return self.load_data()

#     def get_current_month_period_id(self):
#         """Get period ID for current month"""
#         from datetime import datetime
#         now = datetime.now()
#         return f"monthly_{now.year}_{now.month:02d}"

#     def refresh_period_list(self):
#         """Refresh the list of available periods"""
#         try:
#             time_tracker = self.history_tab.get_time_tracker()
#             available_periods = time_tracker.get_available_periods()
            
#             # Add current month if not in list
#             current_period = time_tracker.get_current_period(PeriodType.MONTHLY)
            
#             period_options = [current_period.display_name + " (Current)"]
#             period_ids = [current_period.period_id]
            
#             for period in available_periods:
#                 if period.period_id != current_period.period_id:
#                     period_options.append(period.display_name)
#                     period_ids.append(period.period_id)
            
#             self.period_combo['values'] = period_options
#             self.period_ids = period_ids
            
#             # Select current month by default
#             if period_options:
#                 self.period_combo.current(0)
#                 self.period_var.set(period_options[0])
#         except Exception as e:
#             print(f"Error refreshing period list: {e}")
#             # Fallback - just show current month
#             self.period_combo['values'] = ["Current Month"]
#             self.period_ids = [self.get_current_month_period_id()]
#             self.period_combo.current(0)

#     def on_period_change(self, event=None):
#         """Handle period selection change"""
#         try:
#             if self.period_combo.current() >= 0:
#                 selected_period_id = self.period_ids[self.period_combo.current()]
                
#                 # Save current data first
#                 self.save_data()
                
#                 # Load data for selected period
#                 success = self.load_period_data(selected_period_id)
                
#                 if not success and selected_period_id != self.get_current_month_period_id():
#                     # No data for this period, clear spending
#                     for category_data in self.actual_spending.values():
#                         for view_mode in ViewMode:
#                             category_data[view_mode].set(0.0)
#                     self.update_calculations()
#         except Exception as e:
#             print(f"Error changing period: {e}")
    
#     def on_scenario_change(self, event=None):
#         """Handle scenario change"""
#         self.save_data()  # Save current data
#         self.current_scenario_name = self.scenario_var.get()
#         self.create_category_rows()  # Recreate rows for new scenario
#         self.load_data()  # Load data for new scenario
#         self.update_calculations()
    
#     def on_view_change(self, event=None):
#         """Handle view mode change"""
#         view_str = self.view_var.get()
#         old_view_mode = self.view_mode
        
#         if view_str == "First Paycheck":
#             self.view_mode = ViewMode.FIRST_PAYCHECK
#         elif view_str == "Second Paycheck":
#             self.view_mode = ViewMode.SECOND_PAYCHECK
#         else:
#             self.view_mode = ViewMode.MONTHLY
        
#         # Update entry widgets to use the new view mode
#         self.update_spending_entries()
#         self.update_calculations()
    
#     def update_spending_entries(self):
#         """Update spending entry widgets to use current view mode"""
#         for category_name, entry in self.spending_entries.items():
#             # Update the textvariable to the current view mode
#             entry.config(textvariable=self.actual_spending[category_name][self.view_mode])
    
#     def on_paycheck_change(self):
#         """Handle paycheck amount change"""
#         self.update_monthly_total()
#         self.root.after(100, self.update_calculations)  # Small delay for smooth typing
        
#         # Auto-save if enabled
#         if self.config.auto_save:
#             self.root.after(1000, self.auto_save_data)
        
#         # Update dashboard
#         self.root.after(200, self.refresh_dashboard)
    
#     def update_monthly_total(self):
#         """Update monthly total display"""
#         try:
#             first = self.first_paycheck.get()
#             second = self.second_paycheck.get()
#             total = first + second
#             self.monthly_total_label.config(text=f"Monthly Total: ${total:.2f}")
#         except (ValueError, tk.TclError):
#             self.monthly_total_label.config(text="Monthly Total: $0.00")
    
#     def on_spending_change(self, category):
#         """Handle spending amount change"""
#         # If we're in monthly view, split the amount between paychecks
#         if self.view_mode == ViewMode.MONTHLY:
#             try:
#                 monthly_amount = self.actual_spending[category][ViewMode.MONTHLY].get()
#                 # Split 50/50 between paychecks
#                 paycheck_amount = monthly_amount / 2
#                 self.actual_spending[category][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
#                 self.actual_spending[category][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
#             except (ValueError, tk.TclError):
#                 pass
#         else:
#             # If we're in paycheck view, update monthly total
#             try:
#                 first_amount = self.actual_spending[category][ViewMode.FIRST_PAYCHECK].get()
#                 second_amount = self.actual_spending[category][ViewMode.SECOND_PAYCHECK].get()
#                 monthly_amount = first_amount + second_amount
#                 self.actual_spending[category][ViewMode.MONTHLY].set(monthly_amount)
#             except (ValueError, tk.TclError):
#                 pass
        
#         self.root.after(100, self.update_calculations)
        
#         # Auto-save if enabled
#         if self.config.auto_save:
#             self.root.after(1000, self.auto_save_data)
        
#         # Update dashboard
#         self.root.after(200, self.refresh_dashboard)
    
#     def get_safe_paychecks(self) -> tuple[float, float]:
#         """Get paycheck amounts with error handling"""
#         try:
#             first = self.first_paycheck.get()
#         except (ValueError, tk.TclError):
#             first = 0.0
        
#         try:
#             second = self.second_paycheck.get()
#         except (ValueError, tk.TclError):
#             second = 0.0
        
#         return first, second
    
#     def get_safe_spending(self) -> dict:
#         """Get spending amounts for current view mode with error handling"""
#         spending = {}
#         for category, view_data in self.actual_spending.items():
#             try:
#                 spending[category] = view_data[self.view_mode].get()
#             except (ValueError, tk.TclError):
#                 spending[category] = 0.0
#         return spending
    
#     def update_calculations(self):
#         """Update all calculations and display"""
#         first_paycheck, second_paycheck = self.get_safe_paychecks()
#         spending = self.get_safe_spending()
        
#         # Update monthly total display
#         self.update_monthly_total()
        
#         # Get current scenario and calculator
#         scenario = self.budget_data.get_scenario(self.current_scenario_name)
#         calculator = BudgetCalculator(scenario)
        
#         # Calculate results
#         category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
#         summary = calculator.calculate_summary(category_results, first_paycheck, second_paycheck, self.view_mode)
        
#         # Update display
#         self.update_category_display(category_results)
#         self.update_summary_display(summary)
    
#     def update_category_display(self, category_results):
#         """Update category display with results"""
#         for category_name, result in category_results.items():
#             # Update category name with fixed indicator if needed
#             display_name = category_name
#             scenario = self.budget_data.get_scenario(self.current_scenario_name)
#             category = scenario.get_category(category_name)
            
#             if self.config.show_fixed_indicators and category.category_type.name == "FIXED_DOLLAR":
#                 display_name = f"{category_name} (Fixed)"
            
#             self.category_labels[f"{category_name}_name"].config(text=display_name)
            
#             # Update percentage
#             if self.config.show_percentages:
#                 self.category_labels[f"{category_name}_perc"].config(text=f"{result.percentage:.1f}%")
#             else:
#                 self.category_labels[f"{category_name}_perc"].config(text="")
            
#             # Format currency
#             currency = self.config.currency_symbol
#             decimal_places = self.config.decimal_places
            
#             # Update amounts
#             self.category_labels[f"{category_name}_budget"].config(
#                 text=f"{currency}{result.budgeted:.{decimal_places}f}")
#             self.category_labels[f"{category_name}_diff"].config(
#                 text=f"{currency}{result.difference:.{decimal_places}f}")
#             self.category_labels[f"{category_name}_status"].config(
#                 text=result.status, foreground=result.color)
    
#     def update_summary_display(self, summary):
#         """Update summary display"""
#         currency = self.config.currency_symbol
#         decimal_places = self.config.decimal_places
        
#         self.summary_labels["Total Budgeted:"].config(
#             text=f"{currency}{summary.total_budgeted:.{decimal_places}f}")
#         self.summary_labels["Total Spent:"].config(
#             text=f"{currency}{summary.total_spent:.{decimal_places}f}")
#         self.summary_labels["Remaining:"].config(
#             text=f"{currency}{summary.remaining:.{decimal_places}f}")
        
#         over_under_text = f"{currency}{summary.over_under:.{decimal_places}f} {summary.over_under_status}"
#         self.summary_labels["Over/Under:"].config(
#             text=over_under_text, foreground=summary.over_under_color)
    
#     def refresh_dashboard(self):
#         """Refresh dashboard charts with current data"""
#         first_paycheck, second_paycheck = self.get_safe_paychecks()
#         spending = self.get_safe_spending()
        
#         # Get data for charts
#         scenario = self.budget_data.get_scenario(self.current_scenario_name)
#         calculator = BudgetCalculator(scenario)
#         category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
        
#         # Update dashboard
#         self.dashboard.update_charts(category_results, self.view_mode)
    
#     def on_theme_change(self, new_theme):
#         """Handle theme change from settings"""
#         self.config = get_config()  # Reload config
#         self.dashboard.update_theme(new_theme)
    
#     def get_current_budget_data(self):
#         """Get current budget data for history tracking"""
#         try:
#             first_paycheck, second_paycheck = self.get_safe_paychecks()
#             spending = self.get_safe_spending()
            
#             # Get current scenario and calculator
#             scenario = self.budget_data.get_scenario(self.current_scenario_name)
#             calculator = BudgetCalculator(scenario)
            
#             # Calculate results
#             category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
#             summary = calculator.calculate_summary(category_results, first_paycheck, second_paycheck, self.view_mode)
            
#             return {
#                 'scenario_name': self.current_scenario_name,
#                 'income': first_paycheck + second_paycheck,  # Monthly total for history
#                 'view_mode': self.view_mode,
#                 'category_results': category_results,
#                 'summary': summary
#             }
#         except Exception as e:
#             print(f"Error getting current budget data: {e}")
#             return None
    
#     def save_data(self):
#         """Save current data to database"""
#         first_paycheck, second_paycheck = self.get_safe_paychecks()
        
#         # Save spending data for all view modes
#         all_spending = {}
#         for category, view_data in self.actual_spending.items():
#             for view_mode in ViewMode:
#                 key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
#                 try:
#                     all_spending[key] = view_data[view_mode].get()
#                 except (ValueError, tk.TclError):
#                     all_spending[key] = 0.0
        
#         # Also save paycheck amounts
#         all_spending['first_paycheck'] = first_paycheck
#         all_spending['second_paycheck'] = second_paycheck
        
#         success = self.database.save_budget_data(
#             self.current_scenario_name, first_paycheck + second_paycheck, all_spending)
        
#         if success:
#             messagebox.showinfo("Success", "Data saved to database!")
            
#             # Create backup if enabled
#             if self.config.auto_backup:
#                 self.database.create_backup(self.config.backup_directory)
#         else:
#             messagebox.showerror("Error", "Failed to save data to database!")
    
#     def auto_save_data(self):
#         """Auto-save data without showing message"""
#         first_paycheck, second_paycheck = self.get_safe_paychecks()
        
#         # Save spending data for all view modes
#         all_spending = {}
#         for category, view_data in self.actual_spending.items():
#             for view_mode in ViewMode:
#                 key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
#                 try:
#                     all_spending[key] = view_data[view_mode].get()
#                 except (ValueError, tk.TclError):
#                     all_spending[key] = 0.0
        
#         # Also save paycheck amounts
#         all_spending['first_paycheck'] = first_paycheck
#         all_spending['second_paycheck'] = second_paycheck
        
#         self.database.save_budget_data(self.current_scenario_name, first_paycheck + second_paycheck, all_spending)
    
#     def load_data(self):
#         """Load data from database"""
#         data = self.database.load_budget_data(self.current_scenario_name)
        
#         if data:
#             income, spending_data = data
            
#             # Load paycheck amounts
#             self.first_paycheck.set(spending_data.get('first_paycheck', income / 2))
#             self.second_paycheck.set(spending_data.get('second_paycheck', income / 2))
            
#             # Load spending amounts for all view modes
#             for category in self.actual_spending.keys():
#                 for view_mode in ViewMode:
#                     key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
#                     amount = spending_data.get(key, 0.0)
#                     self.actual_spending[category][view_mode].set(amount)
        
#         self.update_monthly_total()
#         self.update_calculations()
    
#     def clear_all_spending(self):
#         """Clear all spending data"""
#         if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
#             for category_data in self.actual_spending.values():
#                 for view_mode in ViewMode:
#                     category_data[view_mode].set(0.0)
#             self.update_calculations()
    
#     def export_csv(self):
#         """Export current data to CSV"""
#         filename = filedialog.asksaveasfilename(
#             defaultextension=".csv",
#             filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
#             initialname=f"budget_export_{self.view_mode.value.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         )
        
#         if filename:
#             try:
#                 first_paycheck, second_paycheck = self.get_safe_paychecks()
#                 spending = self.get_safe_spending()
                
#                 # Get data for export
#                 scenario = self.budget_data.get_scenario(self.current_scenario_name)
#                 calculator = BudgetCalculator(scenario)
#                 category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
#                 csv_data = calculator.export_to_csv_data(category_results, self.view_mode, first_paycheck, second_paycheck)
                
#                 # Write CSV
#                 with open(filename, 'w', newline='') as file:
#                     writer = csv.writer(file)
#                     writer.writerows(csv_data)
                
#                 messagebox.showinfo("Success", f"Data exported to {filename}")
                
#             except Exception as e:
#                 messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
#     def manual_csv_backup(self):
#         """Create a manual CSV backup"""
#         success = self.database.create_csv_backup()
#         if success:
#             messagebox.showinfo("Success", "CSV backup created successfully!")
#         else:
#             messagebox.showerror("Error", "Failed to create CSV backup")
    
#     def import_from_csv(self):
#         """Import data from a CSV backup"""
#         # Get available CSV files
#         csv_files = self.database.get_available_csv_backups()
        
#         if not csv_files:
#             messagebox.showinfo("No Backups", "No CSV backup files found.")
#             return
        
#         # Show selection dialog
#         import_dialog = tk.Toplevel(self.root)
#         import_dialog.title("Import from CSV Backup")
#         import_dialog.geometry("400x300")
#         import_dialog.transient(self.root)
#         import_dialog.grab_set()
        
#         ttk.Label(import_dialog, text="Select CSV file to import:").pack(pady=10)
        
#         # Listbox for file selection
#         listbox = tk.Listbox(import_dialog)
#         listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
#         for csv_file in csv_files:
#             listbox.insert(tk.END, csv_file)
        
#         def do_import():
#             selection = listbox.curselection()
#             if not selection:
#                 messagebox.showerror("Error", "Please select a file to import")
#                 return
            
#             selected_file = csv_files[selection[0]]
            
#             if messagebox.askyesno("Confirm Import", 
#                                  f"This will replace all current data with data from {selected_file}. Continue?"):
#                 success = self.database.load_from_csv_backup(selected_file)
#                 if success:
#                     self.load_data()  # Reload current view
#                     messagebox.showinfo("Success", "Data imported successfully!")
#                     import_dialog.destroy()
#                 else:
#                     messagebox.showerror("Error", "Failed to import data")
        
#         button_frame = ttk.Frame(import_dialog)
#         button_frame.pack(pady=10)
        
#         ttk.Button(button_frame, text="Import", command=do_import).pack(side="left", padx=5)
#         ttk.Button(button_frame, text="Cancel", command=import_dialog.destroy).pack(side="left", padx=5)
    
#     def show_data_location(self):
#         """Show where data files are stored"""
#         data_dir = self.database.data_dir
        
#         info_dialog = tk.Toplevel(self.root)
#         info_dialog.title("Data Storage Location")
#         info_dialog.geometry("500x200")
#         info_dialog.transient(self.root)
#         info_dialog.grab_set()
        
#         ttk.Label(info_dialog, text="Your budget data is stored in:", font=("", 12, "bold")).pack(pady=10)
        
#         # Path display
#         path_frame = ttk.Frame(info_dialog)
#         path_frame.pack(fill="x", padx=10, pady=5)
        
#         path_text = tk.Text(path_frame, height=2, wrap=tk.WORD)
#         path_text.insert(1.0, data_dir)
#         path_text.config(state="disabled")
#         path_text.pack(fill="x")
        
#         # Buttons
#         button_frame = ttk.Frame(info_dialog)
#         button_frame.pack(pady=20)
        
#         def open_folder():
#             import subprocess
#             import platform
#             try:
#                 if platform.system() == "Windows":
#                     subprocess.run(["explorer", data_dir])
#                 elif platform.system() == "Darwin":  # macOS
#                     subprocess.run(["open", data_dir])
#                 else:  # Linux
#                     subprocess.run(["xdg-open", data_dir])
#             except Exception as e:
#                 messagebox.showerror("Error", f"Could not open folder: {e}")
        
#         ttk.Button(button_frame, text="Open Folder", command=open_folder).pack(side="left", padx=5)
#         ttk.Button(button_frame, text="Close", command=info_dialog.destroy).pack(side="left", padx=5)

# def main():
#     root = tk.Tk()
#     app = BudgetApp(root)
#     root.mainloop()

# if __name__ == "__main__":
#     main()

# budget_app.py - FINAL COMPLETE FIX
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import csv

# Import our separated modules
from budget_models import BudgetData, ViewMode
from budget_database import BudgetDatabase
from budget_calculator import BudgetCalculator
from budget_dashboard import BudgetDashboard
from budget_settings import BudgetSettings
from budget_history_tab import BudgetHistoryTab
from budget_time_tracker import PeriodType, BudgetSnapshot
from config import get_config

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.config = get_config()
        
        # Initialize data models
        self.budget_data = BudgetData()
        self.database = BudgetDatabase(self.config.database_filename)
        
        # Application state
        self.current_scenario_name = self.config.default_scenario
        self.view_mode = ViewMode.MONTHLY
        
        # Set your EXACT paycheck amounts as defaults
        self.first_paycheck = tk.DoubleVar(value=2164.77)
        self.second_paycheck = tk.DoubleVar(value=2154.42)
        self.actual_spending = {}
        
        # Track loading state and current period
        self._loading_data = False
        self._current_period_id = None  # Track which period we're viewing
        
        # Initialize UI
        self.setup_window()
        self.create_widgets()
        
        # Set initial period to current month
        self._current_period_id = self.get_current_month_period_id()
        
        # Load data AFTER UI is created
        self.load_initial_data()
        self.refresh_period_list()
        self.update_calculations()
        
        print(f"App initialized - Current period: {self._current_period_id}")
    
    def load_initial_data(self):
        """Load initial data on app startup"""
        print("Loading initial data...")
        
        # Try to load from database first
        data = self.database.load_budget_data(self.current_scenario_name)
        
        if data:
            income, spending_data = data
            
            # Load EXACT individual paycheck amounts
            stored_first = spending_data.get('first_paycheck')
            stored_second = spending_data.get('second_paycheck')
            
            if stored_first is not None and stored_second is not None:
                print(f"Loading stored paychecks: ${stored_first:.2f} / ${stored_second:.2f}")
                self.first_paycheck.set(stored_first)
                self.second_paycheck.set(stored_second)
            else:
                print("No stored paychecks found - using defaults")
            
            # Load spending amounts for all view modes
            for category in self.actual_spending.keys():
                for view_mode in ViewMode:
                    key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
                    amount = spending_data.get(key, 0.0)
                    self.actual_spending[category][view_mode].set(amount)
        else:
            print("No database data found - starting fresh")
            # For a completely fresh start, clear all spending
            self.clear_all_spending_silent()
        
        self.update_monthly_total()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("Personal Budget Manager")
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        
        # Set up proper window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Apply theme if available
        try:
            import sv_ttk
            sv_ttk.set_theme(self.config.theme)
        except ImportError:
            print("Sun Valley theme not found. Using default theme.")
    
    def on_closing(self):
        """Handle window closing - save data and cleanup"""
        try:
            # Auto-save current data before closing
            if self.config.auto_save:
                self.auto_save_data()
                print("Auto-saved data before closing")
            
            # Ask user if they want to save if auto-save is disabled
            elif messagebox.askyesno("Save Before Exit", "Do you want to save your current data before exiting?"):
                self.save_data()
            
            # Close matplotlib figures to prevent warnings
            try:
                import matplotlib.pyplot as plt
                plt.close('all')
            except:
                pass
            
            # Destroy the window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Force close even if there's an error
            self.root.quit()
            self.root.destroy()
    
    def create_widgets(self):
        """Create main UI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Budget Overview Tab
        self.budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_frame, text="Budget Overview")
        self.create_budget_tab()
        
        # Dashboard Tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.dashboard = BudgetDashboard(self.dashboard_frame, self.config)
        self.dashboard.set_refresh_callback(self.refresh_dashboard)
        
        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.settings = BudgetSettings(self.settings_frame)
        self.settings.set_theme_change_callback(self.on_theme_change)
        self.settings.set_display_change_callback(self.update_calculations)
        
        # History Tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Budget History")
        self.history_tab = BudgetHistoryTab(self.history_frame, self.config, self.get_current_budget_data, self.database)
    
    def create_budget_tab(self):
        """Create the budget overview tab"""
        # Controls frame
        controls_frame = ttk.Frame(self.budget_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # First row of controls
        control_row1 = ttk.Frame(controls_frame)
        control_row1.pack(fill="x", pady=(0, 5))
        
        # Scenario selection
        ttk.Label(control_row1, text="Budget Scenario:").pack(side="left", padx=5)
        self.scenario_var = tk.StringVar(value=self.current_scenario_name)
        scenario_combo = ttk.Combobox(control_row1, textvariable=self.scenario_var,
                                     values=self.budget_data.get_scenario_names(),
                                     state="readonly", width=25)
        scenario_combo.pack(side="left", padx=5)
        scenario_combo.bind("<<ComboboxSelected>>", self.on_scenario_change)
        
        # Period selector
        ttk.Label(control_row1, text="Period:").pack(side="left", padx=(20, 5))
        self.period_var = tk.StringVar()
        self.period_combo = ttk.Combobox(control_row1, textvariable=self.period_var,
                                        state="readonly", width=20)
        self.period_combo.pack(side="left", padx=5)
        self.period_combo.bind("<<ComboboxSelected>>", self.on_period_change)
        
        # View mode selection
        ttk.Label(control_row1, text="View:").pack(side="left", padx=(20, 5))
        self.view_var = tk.StringVar(value=self.view_mode.value)
        view_combo = ttk.Combobox(control_row1, textvariable=self.view_var,
                                 values=[mode.value for mode in ViewMode],
                                 state="readonly", width=15)
        view_combo.pack(side="left", padx=5)
        view_combo.bind("<<ComboboxSelected>>", self.on_view_change)
        
        # Second row of controls - Paycheck inputs
        control_row2 = ttk.Frame(controls_frame)
        control_row2.pack(fill="x", pady=(0, 5))
        
        # First paycheck input
        ttk.Label(control_row2, text="1st Paycheck (6th): $").pack(side="left", padx=5)
        first_entry = ttk.Entry(control_row2, textvariable=self.first_paycheck, width=12)
        first_entry.pack(side="left", padx=5)
        first_entry.bind("<KeyRelease>", lambda e: self.on_paycheck_change())
        
        # Second paycheck input
        ttk.Label(control_row2, text="2nd Paycheck (21st): $").pack(side="left", padx=(20, 5))
        second_entry = ttk.Entry(control_row2, textvariable=self.second_paycheck, width=12)
        second_entry.pack(side="left", padx=5)
        second_entry.bind("<KeyRelease>", lambda e: self.on_paycheck_change())
        
        # Monthly total display
        self.monthly_total_label = ttk.Label(control_row2, text="Monthly Total: $4319.19", 
                                           font=("", 10, "bold"), foreground="cyan")
        self.monthly_total_label.pack(side="left", padx=(20, 5))
        
        # Third row of controls - Buttons
        control_row3 = ttk.Frame(controls_frame)
        control_row3.pack(fill="x")
        
        # Buttons
        button_frame = ttk.Frame(control_row3)
        button_frame.pack(side="left")
        
        ttk.Button(button_frame, text="Save Data", command=self.save_data).pack(side="left", padx=2)
        
        # CSV Backup dropdown
        csv_menu = ttk.Menubutton(button_frame, text="CSV Backup", direction="below")
        csv_menu.pack(side="left", padx=2)
        
        csv_submenu = tk.Menu(csv_menu, tearoff=0)
        csv_submenu.add_command(label="Export to CSV", command=self.export_csv)
        csv_submenu.add_command(label="Import from CSV", command=self.import_from_csv)
        csv_submenu.add_command(label="Create CSV Backup", command=self.manual_csv_backup)
        csv_submenu.add_separator()
        csv_submenu.add_command(label="Show Data Location", command=self.show_data_location)
        csv_menu.config(menu=csv_submenu)
        
        ttk.Button(button_frame, text="Clear All", command=self.clear_all_spending).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Create Period", command=self.create_manual_period).pack(side="left", padx=2)
        
        # Debug button (remove this in production)
        ttk.Button(button_frame, text="Debug", command=self.debug_paycheck_values).pack(side="left", padx=2)
        
        # Auto-save indicator
        if self.config.auto_save:
            ttk.Label(button_frame, text="Auto-save: ON", foreground="green").pack(side="left", padx=10)
        
        # Categories table
        self.create_categories_table()
        
        # Summary
        self.create_summary_section()
    
    def create_categories_table(self):
        """Create the categories table"""
        # Table frame
        table_frame = ttk.Frame(self.budget_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Headers
        headers = ["Category", "% of Income", "Budgeted ($)", "Actual Spent ($)", "Difference ($)", "Status"]
        for i, header in enumerate(headers):
            label = ttk.Label(table_frame, text=header, font=("", 10, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        for i in range(len(headers)):
            table_frame.columnconfigure(i, weight=1)
        
        # Store references for updating
        self.category_labels = {}
        self.spending_entries = {}
        self.table_frame = table_frame
        
        self.create_category_rows()
    
    def create_category_rows(self):
        """Create rows for each category"""
        # Clear existing rows (except header)
        for widget in self.table_frame.winfo_children()[6:]:  # Skip header row
            widget.destroy()
        
        # Clear references
        self.category_labels.clear()
        self.spending_entries.clear()
        self.actual_spending.clear()
        
        # Get current scenario
        scenario = self.budget_data.get_scenario(self.current_scenario_name)
        
        # Create rows
        row = 1
        for category_name in scenario.get_all_categories().keys():
            # Initialize spending variables for all view modes
            self.actual_spending[category_name] = {
                ViewMode.FIRST_PAYCHECK: tk.DoubleVar(value=0.0),
                ViewMode.SECOND_PAYCHECK: tk.DoubleVar(value=0.0),
                ViewMode.MONTHLY: tk.DoubleVar(value=0.0)
            }
            
            # Category name
            cat_label = ttk.Label(self.table_frame, text=category_name)
            cat_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            self.category_labels[f"{category_name}_name"] = cat_label
            
            # Percentage
            perc_label = ttk.Label(self.table_frame, text="")
            perc_label.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category_name}_perc"] = perc_label
            
            # Budgeted amount
            budget_label = ttk.Label(self.table_frame, text="")
            budget_label.grid(row=row, column=2, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category_name}_budget"] = budget_label
            
            # Actual spent (editable) - uses current view mode
            actual_entry = ttk.Entry(self.table_frame, textvariable=self.actual_spending[category_name][self.view_mode], width=12)
            actual_entry.grid(row=row, column=3, padx=5, pady=2, sticky="ew")
            actual_entry.bind("<KeyRelease>", lambda e, cat=category_name: self.on_spending_change(cat))
            self.spending_entries[category_name] = actual_entry
            
            # Difference
            diff_label = ttk.Label(self.table_frame, text="")
            diff_label.grid(row=row, column=4, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category_name}_diff"] = diff_label
            
            # Status
            status_label = ttk.Label(self.table_frame, text="")
            status_label.grid(row=row, column=5, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category_name}_status"] = status_label
            
            row += 1
    
    def create_summary_section(self):
        """Create the summary section"""
        summary_frame = ttk.LabelFrame(self.budget_frame, text="Summary", padding=10)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.summary_labels = {}
        summary_row = ttk.Frame(summary_frame)
        summary_row.pack(fill="x")
        
        # Create summary labels
        labels = ["Total Budgeted:", "Total Spent:", "Remaining:", "Over/Under:"]
        for i, label in enumerate(labels):
            ttk.Label(summary_row, text=label).grid(row=0, column=i*2, padx=10, sticky="e")
            self.summary_labels[label] = ttk.Label(summary_row, text="$0.00", font=("", 11, "bold"))
            self.summary_labels[label].grid(row=0, column=i*2+1, padx=10, sticky="w")


    def test_period_isolation(self):
        """Test method to verify period data isolation"""
        print("\n=== PERIOD ISOLATION TEST ===")
        
        current_period = getattr(self, '_current_period_id', 'None')
        print(f"Current period: {current_period}")
        
        # Show current spending for first few categories
        for i, (category, view_data) in enumerate(list(self.actual_spending.items())[:3]):
            monthly_amount = view_data[ViewMode.MONTHLY].get()
            print(f"  {category}: ${monthly_amount:.2f}")
        
        print(f"Paychecks: ${self.first_paycheck.get():.2f} / ${self.second_paycheck.get():.2f}")
        print("=== END TEST ===\n")
    
    def get_current_month_period_id(self):
        """Get period ID for current month"""
        now = datetime.now()
        return f"monthly_{now.year}_{now.month:02d}"
    
    def load_period_data(self, period_id=None):
        """Load budget data for a specific period - COMPLETELY REWRITTEN"""
        if self._loading_data:
            return False
            
        if period_id is None:
            period_id = self.get_current_month_period_id()
        
        print(f"Loading period data for: {period_id}")
        
        self._loading_data = True
        try:
            # Check if we have a snapshot for this period
            time_tracker = self.history_tab.get_time_tracker()
            snapshot = time_tracker.get_snapshot(period_id)
            
            if snapshot:
                print(f"Found snapshot with paychecks: ${snapshot.first_paycheck:.2f} / ${snapshot.second_paycheck:.2f}")
                
                # Load EXACT paycheck amounts from snapshot
                self.first_paycheck.set(snapshot.first_paycheck)
                self.second_paycheck.set(snapshot.second_paycheck)
                
                # Load category spending
                for category_name in self.actual_spending.keys():
                    category_data = snapshot.category_data.get(category_name, {'actual': 0.0})
                    monthly_amount = category_data['actual']
                    
                    # Set monthly amount
                    self.actual_spending[category_name][ViewMode.MONTHLY].set(monthly_amount)
                    
                    # Split between paychecks (50/50)
                    paycheck_amount = monthly_amount / 2
                    self.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                    self.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
                
                self.update_calculations()
                return True
            else:
                # No snapshot - check if this is current month
                current_month_id = self.get_current_month_period_id()
                
                if period_id == current_month_id:
                    print("Current month with no snapshot - starting fresh")
                    # Clear spending but keep current paycheck amounts
                    for category_data in self.actual_spending.values():
                        for view_mode in ViewMode:
                            category_data[view_mode].set(0.0)
                    
                    # Check for overage carry-over
                    if time_tracker.should_start_fresh_for_new_month(period_id):
                        self.start_fresh_month()
                    
                    self.update_calculations()
                    return True
                else:
                    print("Historical period with no data - clearing all")
                    # Historical period with no data - clear everything but keep default paychecks
                    self.first_paycheck.set(2164.77)
                    self.second_paycheck.set(2154.42)
                    
                    for category_data in self.actual_spending.values():
                        for view_mode in ViewMode:
                            category_data[view_mode].set(0.0)
                    
                    self.update_calculations()
                    return False
        finally:
            self._loading_data = False
    
    def start_fresh_month(self):
        """Start a fresh month with clean spending data and carry over ONLY 'Over Budget' categories"""
        print("Starting fresh month with overage carry-over...")
        
        # Reset all spending to zero first
        for category_data in self.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        
        # Get time tracker for overage carry-over
        time_tracker = self.history_tab.get_time_tracker()
        current_period_id = self.get_current_month_period_id()
        
        # Get overages from previous month
        overages = time_tracker.get_previous_month_overages(current_period_id)
        
        if overages:
            print(f"Carrying over overages: {overages}")
            
            # Carry over only true overspending
            for category_name, overage_amount in overages.items():
                if category_name in self.actual_spending:
                    # Set the overage amount as starting spent amount for this month
                    self.actual_spending[category_name][ViewMode.MONTHLY].set(overage_amount)
                    
                    # Split between paychecks
                    paycheck_amount = overage_amount / 2
                    self.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                    self.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
            
            # Show user what was carried over
            overage_summary = "\n".join([f"• {cat}: ${amt:.2f}" for cat, amt in overages.items()])
            total_overage = sum(overages.values())
            
            messagebox.showinfo("Over-Budget Categories Carried Forward", 
                f"Starting fresh month with previous 'Over Budget' spending:\n\n{overage_summary}\n\n"
                f"Total overspending carried forward: ${total_overage:.2f}\n\n"
                f"This tracks money that went over budget last month.")
        else:
            print("No overages to carry forward")
        
        self.update_calculations()
    
    def refresh_period_list(self):
        """Refresh the list of available periods"""
        try:
            time_tracker = self.history_tab.get_time_tracker()
            available_periods = time_tracker.get_available_periods()
            
            # Add current month if not in list
            current_period = time_tracker.get_current_period(PeriodType.MONTHLY)
            
            period_options = [current_period.display_name + " (Current)"]
            period_ids = [current_period.period_id]
            
            for period in available_periods:
                if period.period_id != current_period.period_id:
                    period_options.append(period.display_name)
                    period_ids.append(period.period_id)
            
            self.period_combo['values'] = period_options
            self.period_ids = period_ids
            
            # Select current month by default
            if period_options:
                self.period_combo.current(0)
                self.period_var.set(period_options[0])
        except Exception as e:
            print(f"Error refreshing period list: {e}")
            # Fallback - just show current month
            self.period_combo['values'] = ["Current Month"]
            self.period_ids = [self.get_current_month_period_id()]
            self.period_combo.current(0)
    
    def on_scenario_change(self, event=None):
        """Handle scenario change"""
        if self._loading_data:
            return
            
        print(f"Scenario changed to: {self.scenario_var.get()}")
        self.save_data()  # Save current data
        self.current_scenario_name = self.scenario_var.get()
        self.create_category_rows()  # Recreate rows for new scenario
        self.load_initial_data()  # Load data for new scenario
        self.update_calculations()
    
    def on_view_change(self, event=None):
        """Handle view mode change"""
        view_str = self.view_var.get()
        
        if view_str == "First Paycheck":
            self.view_mode = ViewMode.FIRST_PAYCHECK
        elif view_str == "Second Paycheck":
            self.view_mode = ViewMode.SECOND_PAYCHECK
        else:
            self.view_mode = ViewMode.MONTHLY
        
        # Update entry widgets to use the new view mode
        self.update_spending_entries()
        self.update_calculations()
    
    def on_period_change(self, event=None):
        """Handle period selection change - COMPLETELY FIXED VERSION"""
        if self._loading_data:
            return
            
        try:
            if self.period_combo.current() >= 0:
                selected_period_id = self.period_ids[self.period_combo.current()]
                current_month_id = self.get_current_month_period_id()
                
                print(f"=== PERIOD CHANGE ===")
                print(f"Switching from current period to: {selected_period_id}")
                print(f"Current month ID: {current_month_id}")
                
                # CRITICAL: Save current data ONLY if we're leaving the current month
                # Don't save when switching TO current month
                current_selection = getattr(self, '_current_period_id', None)
                if current_selection and current_selection != selected_period_id:
                    if current_selection == current_month_id:
                        print(f"Saving current month data before switching")
                        self.save_current_period_data()
                    else:
                        print(f"Switching between historical periods - not saving")
                
                # Store the new selection
                self._current_period_id = selected_period_id
                
                # Load data for selected period with complete isolation
                self.load_period_data_isolated(selected_period_id)
                        
        except Exception as e:
            print(f"Error changing period: {e}")

    def load_period_data_isolated(self, period_id):
        """Load period data with complete isolation between periods"""
        if self._loading_data:
            return False
            
        print(f"Loading isolated data for period: {period_id}")
        
        self._loading_data = True
        try:
            # Get time tracker
            time_tracker = self.history_tab.get_time_tracker()
            snapshot = time_tracker.get_snapshot(period_id)
            current_month_id = self.get_current_month_period_id()
            
            if snapshot:
                print(f"Found snapshot for {period_id}")
                print(f"Snapshot paychecks: ${snapshot.first_paycheck:.2f} / ${snapshot.second_paycheck:.2f}")
                
                # Load EXACT paycheck amounts from snapshot
                self.first_paycheck.set(snapshot.first_paycheck)
                self.second_paycheck.set(snapshot.second_paycheck)
                
                # Load category spending with complete isolation
                for category_name in self.actual_spending.keys():
                    category_data = snapshot.category_data.get(category_name, {'actual': 0.0})
                    monthly_amount = category_data.get('actual', 0.0)
                    
                    print(f"Loading {category_name}: ${monthly_amount:.2f}")
                    
                    # Set monthly amount
                    self.actual_spending[category_name][ViewMode.MONTHLY].set(monthly_amount)
                    
                    # Split between paychecks (50/50)
                    paycheck_amount = monthly_amount / 2
                    self.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                    self.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
                
                self.update_calculations()
                return True
                
            else:
                print(f"No snapshot found for {period_id}")
                
                if period_id == current_month_id:
                    print("This is current month - starting fresh")
                    # Current month with no data - check for overage carry-over
                    self.start_fresh_current_month()
                    return True
                else:
                    print("This is historical period with no data - showing blank")
                    # Historical period with no data - show completely blank
                    self.show_blank_historical_period()
                    return False
                    
        finally:
            self._loading_data = False

    def show_blank_historical_period(self):
        """Show blank data for historical period with no snapshot"""
        print("Showing blank historical period")
        
        # Set default paycheck amounts for historical periods
        self.first_paycheck.set(2164.77)
        self.second_paycheck.set(2154.42)
        
        # Clear all spending
        for category_data in self.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        
        self.update_calculations()

    def save_current_period_data(self):
        """Save data for the current period being viewed"""
        if not hasattr(self, '_current_period_id'):
            return
            
        period_id = self._current_period_id
        current_month_id = self.get_current_month_period_id()
        
        # Only save snapshots for current month or when explicitly saving
        if period_id != current_month_id:
            print(f"Not saving snapshot for historical period: {period_id}")
            return
        
        print(f"Saving current period data for: {period_id}")
        
        try:
            time_tracker = self.history_tab.get_time_tracker()
            
            # Get current period object
            if period_id == current_month_id:
                period = time_tracker.get_current_period(PeriodType.MONTHLY)
            else:
                # For historical periods, we need to recreate the period
                # This should only happen for manually created periods
                existing_snapshot = time_tracker.get_snapshot(period_id)
                if existing_snapshot:
                    period = existing_snapshot.period
                else:
                    print(f"Cannot save - no existing period found for {period_id}")
                    return
            
            # Get current budget data
            budget_data = self.get_current_budget_data()
            if not budget_data:
                print("No budget data to save")
                return
            
            # Create category data for snapshot
            category_data = {}
            for category_name, result in budget_data['category_results'].items():
                category_data[category_name] = {
                    'budgeted': result.budgeted,
                    'actual': result.actual,
                    'notes': ''
                }
            
            # Create snapshot with current data
            snapshot = BudgetSnapshot(
                period=period,
                scenario_name=budget_data['scenario_name'],
                first_paycheck=budget_data['first_paycheck'],
                second_paycheck=budget_data['second_paycheck'],
                total_income=budget_data['total_income'],
                view_mode=budget_data['view_mode'].value,
                category_data=category_data,
                total_budgeted=budget_data['summary'].total_budgeted,
                total_spent=budget_data['summary'].total_spent,
                saved_date=datetime.now()
            )
            
            # Save the snapshot
            time_tracker.save_snapshot(snapshot)
            print(f"Saved snapshot for {period_id}")
            
        except Exception as e:
            print(f"Error saving current period data: {e}")

    def start_fresh_current_month(self):
        """Start fresh for current month with overage carry-over"""
        print("Starting fresh current month")
        
        # Keep current paycheck amounts (don't reset them)
        current_first = self.first_paycheck.get()
        current_second = self.second_paycheck.get()
        
        # Clear all spending first
        for category_data in self.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        
        # Check for overage carry-over from previous month
        time_tracker = self.history_tab.get_time_tracker()
        current_period_id = self.get_current_month_period_id()
        
        try:
            overages = time_tracker.get_previous_month_overages(current_period_id)
            
            if overages:
                print(f"Carrying over overages: {overages}")
                
                # Apply overages
                for category_name, overage_amount in overages.items():
                    if category_name in self.actual_spending:
                        self.actual_spending[category_name][ViewMode.MONTHLY].set(overage_amount)
                        paycheck_amount = overage_amount / 2
                        self.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                        self.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
                
                # Show user what was carried over
                overage_summary = "\n".join([f"• {cat}: ${amt:.2f}" for cat, amt in overages.items()])
                total_overage = sum(overages.values())
                
                messagebox.showinfo("Over-Budget Categories Carried Forward", 
                    f"Starting fresh month with previous 'Over Budget' spending:\n\n{overage_summary}\n\n"
                    f"Total overspending carried forward: ${total_overage:.2f}")
            else:
                print("No overages to carry forward")
                
        except Exception as e:
            print(f"Error checking overages: {e}")
        
        # Restore paycheck amounts
        self.first_paycheck.set(current_first)
        self.second_paycheck.set(current_second)
        
        self.update_calculations()
    
    def on_paycheck_change(self):
        """Handle paycheck amount change"""
        if self._loading_data:
            return
            
        self.update_monthly_total()
        self.root.after(100, self.update_calculations)  # Small delay for smooth typing
        
        # Auto-save if enabled
        if self.config.auto_save:
            self.root.after(1000, self.auto_save_data)
        
        # Update dashboard
        self.root.after(200, self.refresh_dashboard)
    
    def update_monthly_total(self):
        """Update monthly total display"""
        try:
            first = self.first_paycheck.get()
            second = self.second_paycheck.get()
            total = first + second
            self.monthly_total_label.config(text=f"Monthly Total: ${total:.2f}")
        except (ValueError, tk.TclError):
            self.monthly_total_label.config(text="Monthly Total: $0.00")
    
    def on_spending_change(self, category):
        """Handle spending amount change"""
        if self._loading_data:
            return
            
        # If we're in monthly view, split the amount between paychecks
        if self.view_mode == ViewMode.MONTHLY:
            try:
                monthly_amount = self.actual_spending[category][ViewMode.MONTHLY].get()
                # Split 50/50 between paychecks
                paycheck_amount = monthly_amount / 2
                self.actual_spending[category][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                self.actual_spending[category][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
            except (ValueError, tk.TclError):
                pass
        else:
            # If we're in paycheck view, update monthly total
            try:
                first_amount = self.actual_spending[category][ViewMode.FIRST_PAYCHECK].get()
                second_amount = self.actual_spending[category][ViewMode.SECOND_PAYCHECK].get()
                monthly_amount = first_amount + second_amount
                self.actual_spending[category][ViewMode.MONTHLY].set(monthly_amount)
            except (ValueError, tk.TclError):
                pass
        
        self.root.after(100, self.update_calculations)
        
        # Auto-save if enabled
        if self.config.auto_save:
            self.root.after(1000, self.auto_save_data)
        
        # Update dashboard
        self.root.after(200, self.refresh_dashboard)
    
    def update_spending_entries(self):
        """Update spending entry widgets to use current view mode"""
        for category_name, entry in self.spending_entries.items():
            # Update the textvariable to the current view mode
            entry.config(textvariable=self.actual_spending[category_name][self.view_mode])
    
    def get_safe_paychecks(self) -> tuple[float, float]:
        """Get paycheck amounts with error handling"""
        try:
            first = self.first_paycheck.get()
        except (ValueError, tk.TclError):
            first = 2164.77  # Your default
        
        try:
            second = self.second_paycheck.get()
        except (ValueError, tk.TclError):
            second = 2154.42  # Your default
        
        return first, second
    
    def get_safe_spending(self) -> dict:
        """Get spending amounts for current view mode with error handling"""
        spending = {}
        for category, view_data in self.actual_spending.items():
            try:
                spending[category] = view_data[self.view_mode].get()
            except (ValueError, tk.TclError):
                spending[category] = 0.0
        return spending
    
    def update_calculations(self):
        """Update all calculations and display"""
        if self._loading_data:
            return
            
        first_paycheck, second_paycheck = self.get_safe_paychecks()
        spending = self.get_safe_spending()
        
        # Update monthly total display
        self.update_monthly_total()
        
        # Get current scenario and calculator
        scenario = self.budget_data.get_scenario(self.current_scenario_name)
        calculator = BudgetCalculator(scenario)
        
        # Calculate results
        category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
        summary = calculator.calculate_summary(category_results, first_paycheck, second_paycheck, self.view_mode)
        
        # Update display
        self.update_category_display(category_results)
        self.update_summary_display(summary)
    
    def update_category_display(self, category_results):
        """Update category display with results"""
        for category_name, result in category_results.items():
            # Update category name with fixed indicator if needed
            display_name = category_name
            scenario = self.budget_data.get_scenario(self.current_scenario_name)
            category = scenario.get_category(category_name)
            
            if self.config.show_fixed_indicators and category.category_type.name == "FIXED_DOLLAR":
                display_name = f"{category_name} (Fixed)"
            
            self.category_labels[f"{category_name}_name"].config(text=display_name)
            
            # Update percentage
            if self.config.show_percentages:
                self.category_labels[f"{category_name}_perc"].config(text=f"{result.percentage:.1f}%")
            else:
                self.category_labels[f"{category_name}_perc"].config(text="")
            
            # Format currency
            currency = self.config.currency_symbol
            decimal_places = self.config.decimal_places
            
            # Update amounts
            self.category_labels[f"{category_name}_budget"].config(
                text=f"{currency}{result.budgeted:.{decimal_places}f}")
            self.category_labels[f"{category_name}_diff"].config(
                text=f"{currency}{result.difference:.{decimal_places}f}")
            self.category_labels[f"{category_name}_status"].config(
                text=result.status, foreground=result.color)
    
    def update_summary_display(self, summary):
        """Update summary display"""
        currency = self.config.currency_symbol
        decimal_places = self.config.decimal_places
        
        self.summary_labels["Total Budgeted:"].config(
            text=f"{currency}{summary.total_budgeted:.{decimal_places}f}")
        self.summary_labels["Total Spent:"].config(
            text=f"{currency}{summary.total_spent:.{decimal_places}f}")
        self.summary_labels["Remaining:"].config(
            text=f"{currency}{summary.remaining:.{decimal_places}f}")
        
        over_under_text = f"{currency}{summary.over_under:.{decimal_places}f} {summary.over_under_status}"
        self.summary_labels["Over/Under:"].config(
            text=over_under_text, foreground=summary.over_under_color)
    
    def refresh_dashboard(self):
        """Refresh dashboard charts with current data"""
        first_paycheck, second_paycheck = self.get_safe_paychecks()
        spending = self.get_safe_spending()
        
        # Get data for charts
        scenario = self.budget_data.get_scenario(self.current_scenario_name)
        calculator = BudgetCalculator(scenario)
        category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
        
        # Update dashboard
        self.dashboard.update_charts(category_results, self.view_mode)
    
    def on_theme_change(self, new_theme):
        """Handle theme change from settings"""
        self.config = get_config()  # Reload config
        self.dashboard.update_theme(new_theme)
    
    def get_current_budget_data(self):
        """Get current budget data for history tracking"""
        try:
            first_paycheck, second_paycheck = self.get_safe_paychecks()
            spending = self.get_safe_spending()
            
            # Get current scenario and calculator
            scenario = self.budget_data.get_scenario(self.current_scenario_name)
            calculator = BudgetCalculator(scenario)
            
            # Calculate results
            category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
            summary = calculator.calculate_summary(category_results, first_paycheck, second_paycheck, self.view_mode)
            
            return {
                'scenario_name': self.current_scenario_name,
                'first_paycheck': first_paycheck,  # Store individual amounts
                'second_paycheck': second_paycheck,
                'total_income': first_paycheck + second_paycheck,  # Monthly total
                'view_mode': self.view_mode,
                'category_results': category_results,
                'summary': summary
            }
        except Exception as e:
            print(f"Error getting current budget data: {e}")
            return None
    
    def save_current_period_snapshot(self):
        """Save a snapshot of current period to history"""
        try:
            time_tracker = self.history_tab.get_time_tracker()
            current_period = time_tracker.get_current_period(PeriodType.MONTHLY)
            
            # Get current budget data
            budget_data = self.get_current_budget_data()
            if not budget_data:
                return
            
            # Create category data for snapshot
            category_data = {}
            for category_name, result in budget_data['category_results'].items():
                category_data[category_name] = {
                    'budgeted': result.budgeted,
                    'actual': result.actual,
                    'notes': ''
                }
            
            # Create snapshot with individual paycheck amounts
            snapshot = BudgetSnapshot(
                period=current_period,
                scenario_name=budget_data['scenario_name'],
                first_paycheck=budget_data['first_paycheck'],
                second_paycheck=budget_data['second_paycheck'],
                total_income=budget_data['total_income'],
                view_mode=budget_data['view_mode'].value,
                category_data=category_data,
                total_budgeted=budget_data['summary'].total_budgeted,
                total_spent=budget_data['summary'].total_spent,
                saved_date=datetime.now()
            )
            
            time_tracker.save_snapshot(snapshot)
            
        except Exception as e:
            print(f"Error saving snapshot: {e}")
    
    def save_data(self):
        """Save current data to database - ENHANCED for period isolation"""
        if self._loading_data:
            return False
            
        first_paycheck, second_paycheck = self.get_safe_paychecks()
        
        print(f"=== SAVING DATA ===")
        print(f"Paychecks: ${first_paycheck:.2f} / ${second_paycheck:.2f}")
        print(f"Current period: {getattr(self, '_current_period_id', 'None')}")
        
        # Save to database (regular scenario data)
        all_spending = {}
        for category, view_data in self.actual_spending.items():
            for view_mode in ViewMode:
                key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
                try:
                    all_spending[key] = view_data[view_mode].get()
                except (ValueError, tk.TclError):
                    all_spending[key] = 0.0
        
        # Save paycheck amounts
        all_spending['first_paycheck'] = first_paycheck
        all_spending['second_paycheck'] = second_paycheck
        
        success = self.database.save_budget_data(
            self.current_scenario_name, first_paycheck + second_paycheck, all_spending)
        
        if success:
            print("Database save successful")
            
            # CRITICAL: Also save as period snapshot if this is current month
            current_month_id = self.get_current_month_period_id()
            current_period = getattr(self, '_current_period_id', current_month_id)
            
            if current_period == current_month_id:
                print("Saving current month snapshot")
                self.save_current_period_snapshot()
            else:
                print("Saving historical period snapshot")
                self.save_historical_period_snapshot(current_period)
            
            messagebox.showinfo("Success", "Data saved to database!")
            
            # Create backup if enabled
            if self.config.auto_backup:
                self.database.create_backup(self.config.backup_directory)
        else:
            messagebox.showerror("Error", "Failed to save data to database!")
        
        return success
    
    def save_historical_period_snapshot(self, period_id):
        """Save snapshot for historical period being edited"""
        try:
            time_tracker = self.history_tab.get_time_tracker()
            
            # Get existing snapshot to preserve period info
            existing_snapshot = time_tracker.get_snapshot(period_id)
            if not existing_snapshot:
                print(f"Cannot save historical period {period_id} - no existing snapshot")
                return
            
            period = existing_snapshot.period
            
            # Get current budget data
            budget_data = self.get_current_budget_data()
            if not budget_data:
                return
            
            # Create category data for snapshot
            category_data = {}
            for category_name, result in budget_data['category_results'].items():
                category_data[category_name] = {
                    'budgeted': result.budgeted,
                    'actual': result.actual,
                    'notes': ''
                }
            
            # Create updated snapshot
            snapshot = BudgetSnapshot(
                period=period,
                scenario_name=budget_data['scenario_name'],
                first_paycheck=budget_data['first_paycheck'],
                second_paycheck=budget_data['second_paycheck'],
                total_income=budget_data['total_income'],
                view_mode=budget_data['view_mode'].value,
                category_data=category_data,
                total_budgeted=budget_data['summary'].total_budgeted,
                total_spent=budget_data['summary'].total_spent,
                saved_date=datetime.now()
            )
            
            # Save the updated snapshot
            time_tracker.save_snapshot(snapshot)
            print(f"Saved historical snapshot for {period_id}")
            
        except Exception as e:
            print(f"Error saving historical period snapshot: {e}")
    
    def auto_save_data(self):
        """Auto-save data without showing message"""
        if self._loading_data:
            return
            
        first_paycheck, second_paycheck = self.get_safe_paychecks()
        
        # Save spending data for all view modes
        all_spending = {}
        for category, view_data in self.actual_spending.items():
            for view_mode in ViewMode:
                key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
                try:
                    all_spending[key] = view_data[view_mode].get()
                except (ValueError, tk.TclError):
                    all_spending[key] = 0.0
        
        # Save paycheck amounts SEPARATELY
        all_spending['first_paycheck'] = first_paycheck
        all_spending['second_paycheck'] = second_paycheck
        
        success = self.database.save_budget_data(
            self.current_scenario_name, first_paycheck + second_paycheck, all_spending)
        
        # Also auto-save snapshot if save was successful
        if success:
            self.save_current_period_snapshot()
    
    def clear_all_spending(self):
        """Clear all spending data"""
        if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
            self.clear_all_spending_silent()
            
    def clear_all_spending_silent(self):
        """Clear all spending data without confirmation"""
        for category_data in self.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        self.update_calculations()
    
    def export_csv(self):
        """Export current data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"budget_export_{self.view_mode.value.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                first_paycheck, second_paycheck = self.get_safe_paychecks()
                spending = self.get_safe_spending()
                
                # Get data for export
                scenario = self.budget_data.get_scenario(self.current_scenario_name)
                calculator = BudgetCalculator(scenario)
                category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
                csv_data = calculator.export_to_csv_data(category_results, self.view_mode, first_paycheck, second_paycheck)
                
                # Write CSV
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(csv_data)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def manual_csv_backup(self):
        """Create a manual CSV backup"""
        success = self.database.create_csv_backup()
        if success:
            messagebox.showinfo("Success", "CSV backup created successfully!")
        else:
            messagebox.showerror("Error", "Failed to create CSV backup")
    
    def import_from_csv(self):
        """Import data from a CSV backup"""
        # Get available CSV files
        csv_files = self.database.get_available_csv_backups()
        
        if not csv_files:
            messagebox.showinfo("No Backups", "No CSV backup files found.")
            return
        
        # Show selection dialog
        import_dialog = tk.Toplevel(self.root)
        import_dialog.title("Import from CSV Backup")
        import_dialog.geometry("400x300")
        import_dialog.transient(self.root)
        import_dialog.grab_set()
        
        ttk.Label(import_dialog, text="Select CSV file to import:").pack(pady=10)
        
        # Listbox for file selection
        listbox = tk.Listbox(import_dialog)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        for csv_file in csv_files:
            listbox.insert(tk.END, csv_file)
        
        def do_import():
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Error", "Please select a file to import")
                return
            
            selected_file = csv_files[selection[0]]
            
            if messagebox.askyesno("Confirm Import", 
                                 f"This will replace all current data with data from {selected_file}. Continue?"):
                success = self.database.load_from_csv_backup(selected_file)
                if success:
                    self.load_initial_data()  # Reload current view
                    messagebox.showinfo("Success", "Data imported successfully!")
                    import_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to import data")
        
        button_frame = ttk.Frame(import_dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Import", command=do_import).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=import_dialog.destroy).pack(side="left", padx=5)
    
    def show_data_location(self):
        """Show where data files are stored"""
        data_dir = self.database.data_dir
        
        info_dialog = tk.Toplevel(self.root)
        info_dialog.title("Data Storage Location")
        info_dialog.geometry("500x200")
        info_dialog.transient(self.root)
        info_dialog.grab_set()
        
        ttk.Label(info_dialog, text="Your budget data is stored in:", font=("", 12, "bold")).pack(pady=10)
        
        # Path display
        path_frame = ttk.Frame(info_dialog)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        path_text = tk.Text(path_frame, height=2, wrap=tk.WORD)
        path_text.insert(1.0, data_dir)
        path_text.config(state="disabled")
        path_text.pack(fill="x")
        
        # Buttons
        button_frame = ttk.Frame(info_dialog)
        button_frame.pack(pady=20)
        
        def open_folder():
            import subprocess
            import platform
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", data_dir])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", data_dir])
                else:  # Linux
                    subprocess.run(["xdg-open", data_dir])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")
        
        ttk.Button(button_frame, text="Open Folder", command=open_folder).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=info_dialog.destroy).pack(side="left", padx=5)
    
    def debug_paycheck_values(self):
        """Debug method to check paycheck values"""
        try:
            first = self.first_paycheck.get()
            second = self.second_paycheck.get()
            total = first + second
            
            print(f"=== PAYCHECK DEBUG ===")
            print(f"  UI First Paycheck: {first}")
            print(f"  UI Second Paycheck: {second}")
            print(f"  UI Total: {total}")
            
            # Check what's in database
            data = self.database.load_budget_data(self.current_scenario_name)
            if data:
                income, spending_data = data
                db_first = spending_data.get('first_paycheck')
                db_second = spending_data.get('second_paycheck')
                print(f"  Database First: {db_first}")
                print(f"  Database Second: {db_second}")
                print(f"  Database Total: {income}")
                
                # Check for corruption
                if db_first is not None and abs(db_first - first) > 0.01:
                    print(f"  WARNING: Database value differs from UI!")
            else:
                print(f"  No database data found")
            
            # Check current period snapshot
            time_tracker = self.history_tab.get_time_tracker()
            current_period_id = self.get_current_month_period_id()
            snapshot = time_tracker.get_snapshot(current_period_id)
            if snapshot:
                print(f"  Snapshot First: {snapshot.first_paycheck}")
                print(f"  Snapshot Second: {snapshot.second_paycheck}")
                print(f"  Snapshot Total: {snapshot.total_income}")
            else:
                print(f"  No snapshot for current period: {current_period_id}")
            
            print(f"=== END DEBUG ===")
            
            # Show in UI as well
            messagebox.showinfo("Debug Info", 
                f"UI: ${first:.2f} / ${second:.2f}\n"
                f"DB: ${db_first or 'None'} / ${db_second or 'None'}\n"
                f"See console for full details")
        
        except Exception as e:
            print(f"Debug error: {e}")

    
    def create_manual_period(self):
        """Create a manual period for data entry"""
        # Create dialog for manual period creation
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Historical Period")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Create Historical Period", font=("", 14, "bold")).pack(pady=10)
        ttk.Label(dialog, text="This will create a period you can fill with data").pack(pady=5)
        
        # Month/Year selection
        date_frame = ttk.Frame(dialog)
        date_frame.pack(pady=20)
        
        ttk.Label(date_frame, text="Month:").grid(row=0, column=0, padx=5)
        month_var = tk.StringVar(value="July")
        month_combo = ttk.Combobox(date_frame, textvariable=month_var, 
                                values=["January", "February", "March", "April", "May", "June",
                                        "July", "August", "September", "October", "November", "December"],
                                state="readonly", width=15)
        month_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(date_frame, text="Year:").grid(row=0, column=2, padx=5)
        year_var = tk.StringVar(value="2025")
        year_entry = ttk.Entry(date_frame, textvariable=year_var, width=8)
        year_entry.grid(row=0, column=3, padx=5)
        
        # Paycheck amounts for this period
        paycheck_frame = ttk.LabelFrame(dialog, text="Paycheck Amounts for This Period", padding=10)
        paycheck_frame.pack(fill="x", padx=20, pady=10)
        
        first_var = tk.DoubleVar(value=2164.77)
        second_var = tk.DoubleVar(value=2154.42)
        
        ttk.Label(paycheck_frame, text="1st Paycheck: $").grid(row=0, column=0, sticky="w")
        ttk.Entry(paycheck_frame, textvariable=first_var, width=12).grid(row=0, column=1, padx=5)
        
        ttk.Label(paycheck_frame, text="2nd Paycheck: $").grid(row=1, column=0, sticky="w")
        ttk.Entry(paycheck_frame, textvariable=second_var, width=12).grid(row=1, column=1, padx=5)
    
        def create_period():
            try:
                # Get month number
                month_names = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"]
                month_num = month_names.index(month_var.get()) + 1
                year = int(year_var.get())
                
                # Create the period
                from budget_time_tracker import BudgetPeriod, BudgetSnapshot, PeriodType
                import calendar
                from datetime import date
                
                # Create period dates
                start_date = date(year, month_num, 1)
                last_day = calendar.monthrange(year, month_num)[1]
                end_date = date(year, month_num, last_day)
                
                # Create period
                period_id = f"monthly_{year}_{month_num:02d}"
                display_name = f"{month_var.get()} {year}"
                
                period = BudgetPeriod(
                    period_id=period_id,
                    period_type=PeriodType.MONTHLY,
                    start_date=start_date,
                    end_date=end_date,
                    display_name=display_name
                )
                
                # Create empty snapshot with the specified paycheck amounts
                time_tracker = self.history_tab.get_time_tracker()
                
                # Create empty category data (all zeros)
                category_data = {}
                scenario = self.budget_data.get_scenario(self.current_scenario_name)
                for category_name in scenario.get_all_categories().keys():
                    category_data[category_name] = {
                        'budgeted': 0.0,  # Will be calculated when user enters spending
                        'actual': 0.0,
                        'notes': ''
                    }
                
                # Create snapshot
                snapshot = BudgetSnapshot(
                    period=period,
                    scenario_name=self.current_scenario_name,
                    first_paycheck=first_var.get(),
                    second_paycheck=second_var.get(),
                    total_income=first_var.get() + second_var.get(),
                    view_mode=ViewMode.MONTHLY.value,
                    category_data=category_data,
                    total_budgeted=0.0,
                    total_spent=0.0,
                    saved_date=datetime.now(),
                    notes=f"Created manually for data entry"
                )
                
                # Save the snapshot
                time_tracker.save_snapshot(snapshot)
                
                # Refresh the period list
                self.refresh_period_list()
                
                # Switch to the new period
                for i, period_id_check in enumerate(self.period_ids):
                    if period_id_check == period_id:
                        self.period_combo.current(i)
                        self.period_var.set(self.period_combo.get())
                        self.on_period_change()
                        break
                
                messagebox.showinfo("Success", f"Created {display_name} period!\n\nYou can now enter your spending data for this month.")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create period: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Create Period", command=create_period).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

def main():
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()