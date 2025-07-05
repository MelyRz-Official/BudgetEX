# budget_app_main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv

# Import our separated modules
from budget_models import BudgetData, ViewMode
from budget_database import BudgetDatabase
from budget_calculator import BudgetCalculator
from budget_dashboard import BudgetDashboard
from budget_settings import BudgetSettings
from budget_history_tab import BudgetHistoryTab
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
        self.income_amount = tk.DoubleVar(value=self.config.default_paycheck)
        self.actual_spending = {}  # Dict[str, tk.DoubleVar]
        
        # Initialize UI
        self.setup_window()
        self.create_widgets()
        self.load_data()
        self.update_calculations()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("Personal Budget Manager")
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        
        # Apply theme if available
        try:
            import sv_ttk
            sv_ttk.set_theme(self.config.theme)
        except ImportError:
            print("Sun Valley theme not found. Using default theme.")
    
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
        
        # View mode selection
        ttk.Label(control_row1, text="View:").pack(side="left", padx=(20, 5))
        self.view_var = tk.StringVar(value=self.view_mode.value)
        view_combo = ttk.Combobox(control_row1, textvariable=self.view_var,
                                 values=[mode.value for mode in ViewMode],
                                 state="readonly", width=12)
        view_combo.pack(side="left", padx=5)
        view_combo.bind("<<ComboboxSelected>>", self.on_view_change)
        
        # Second row of controls
        control_row2 = ttk.Frame(controls_frame)
        control_row2.pack(fill="x")
        
        # Income input
        self.income_label = ttk.Label(control_row2, text="Monthly Income: $")
        self.income_label.pack(side="left", padx=5)
        income_entry = ttk.Entry(control_row2, textvariable=self.income_amount, width=12)
        income_entry.pack(side="left", padx=5)
        income_entry.bind("<KeyRelease>", lambda e: self.on_income_change())
        
        # Buttons
        button_frame = ttk.Frame(control_row2)
        button_frame.pack(side="right", padx=10)
        
        ttk.Button(button_frame, text="Save Data", command=self.save_data).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all_spending).pack(side="left", padx=2)
        
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
            
            # Actual spent (editable)
            actual_var = tk.DoubleVar(value=0.0)
            self.actual_spending[category_name] = actual_var
            actual_entry = ttk.Entry(self.table_frame, textvariable=actual_var, width=12)
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
    
    def on_scenario_change(self, event=None):
        """Handle scenario change"""
        self.save_data()  # Save current data
        self.current_scenario_name = self.scenario_var.get()
        self.create_category_rows()  # Recreate rows for new scenario
        self.load_data()  # Load data for new scenario
        self.update_calculations()
    
    def on_view_change(self, event=None):
        """Handle view mode change"""
        view_str = self.view_var.get()
        self.view_mode = ViewMode.MONTHLY if view_str == "Monthly" else ViewMode.PER_PAYCHECK
        self.update_income_label()
        self.update_calculations()
    
    def on_income_change(self):
        """Handle income amount change"""
        self.root.after(100, self.update_calculations)  # Small delay for smooth typing
        
        # Auto-save if enabled
        if self.config.auto_save:
            self.root.after(1000, self.auto_save_data)
        
        # Update dashboard
        self.root.after(200, self.refresh_dashboard)
    
    def on_spending_change(self, category):
        """Handle spending amount change"""
        self.root.after(100, self.update_calculations)
        
        # Auto-save if enabled
        if self.config.auto_save:
            self.root.after(1000, self.auto_save_data)
        
        # Update dashboard
        self.root.after(200, self.refresh_dashboard)
    
    def update_income_label(self):
        """Update income label based on view mode"""
        if self.view_mode == ViewMode.MONTHLY:
            self.income_label.config(text="Monthly Income: $")
        else:
            self.income_label.config(text="Paycheck Amount: $")
    
    def get_safe_income(self) -> float:
        """Get income amount with error handling"""
        try:
            return self.income_amount.get()
        except (ValueError, tk.TclError):
            return 0.0
    
    def get_safe_spending(self) -> dict:
        """Get spending amounts with error handling"""
        spending = {}
        for category, var in self.actual_spending.items():
            try:
                spending[category] = var.get()
            except (ValueError, tk.TclError):
                spending[category] = 0.0
        return spending
    
    def update_calculations(self):
        """Update all calculations and display"""
        income = self.get_safe_income()
        spending = self.get_safe_spending()
        
        # Get current scenario and calculator
        scenario = self.budget_data.get_scenario(self.current_scenario_name)
        calculator = BudgetCalculator(scenario)
        
        # Calculate results
        category_results = calculator.calculate_all_categories(income, self.view_mode, spending)
        summary = calculator.calculate_summary(category_results, income)
        
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
        income = self.get_safe_income()
        spending = self.get_safe_spending()
        
        # Get data for charts
        scenario = self.budget_data.get_scenario(self.current_scenario_name)
        calculator = BudgetCalculator(scenario)
        category_results = calculator.calculate_all_categories(income, self.view_mode, spending)
        
        # Update dashboard
        self.dashboard.update_charts(category_results, self.view_mode)
    
    def on_theme_change(self, new_theme):
        """Handle theme change from settings"""
        self.config = get_config()  # Reload config
        self.dashboard.update_theme(new_theme)
    
    def get_current_budget_data(self):
        """Get current budget data for history tracking"""
        try:
            income = self.get_safe_income()
            spending = self.get_safe_spending()
            
            # Get current scenario and calculator
            scenario = self.budget_data.get_scenario(self.current_scenario_name)
            calculator = BudgetCalculator(scenario)
            
            # Calculate results
            category_results = calculator.calculate_all_categories(income, self.view_mode, spending)
            summary = calculator.calculate_summary(category_results, income)
            
            return {
                'scenario_name': self.current_scenario_name,
                'income': income,
                'view_mode': self.view_mode,
                'category_results': category_results,
                'summary': summary
            }
        except Exception as e:
            print(f"Error getting current budget data: {e}")
            return None
    
    def save_data(self):
        """Save current data to database"""
        income = self.get_safe_income()
        spending = self.get_safe_spending()
        
        success = self.database.save_budget_data(
            self.current_scenario_name, income, spending)
        
        if success:
            messagebox.showinfo("Success", "Data saved to database!")
            
            # Create backup if enabled
            if self.config.auto_backup:
                self.database.create_backup(self.config.backup_directory)
        else:
            messagebox.showerror("Error", "Failed to save data to database!")
    
    def auto_save_data(self):
        """Auto-save data without showing message"""
        income = self.get_safe_income()
        spending = self.get_safe_spending()
        self.database.save_budget_data(self.current_scenario_name, income, spending)
    
    def load_data(self):
        """Load data from database"""
        data = self.database.load_budget_data(self.current_scenario_name)
        
        if data:
            income, spending = data
            
            # Set income
            self.income_amount.set(income)
            
            # Set spending amounts
            for category, amount in spending.items():
                if category in self.actual_spending:
                    self.actual_spending[category].set(amount)
        
        self.update_income_label()
        self.update_calculations()
    
    def clear_all_spending(self):
        """Clear all spending data"""
        if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
            for var in self.actual_spending.values():
                var.set(0.0)
            self.update_calculations()
    
    def export_csv(self):
        """Export current data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"budget_export_{self.view_mode.value.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                income = self.get_safe_income()
                spending = self.get_safe_spending()
                
                # Get data for export
                scenario = self.budget_data.get_scenario(self.current_scenario_name)
                calculator = BudgetCalculator(scenario)
                category_results = calculator.calculate_all_categories(income, self.view_mode, spending)
                csv_data = calculator.export_to_csv_data(category_results, self.view_mode)
                
                # Write CSV
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(csv_data)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")

def main():
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()