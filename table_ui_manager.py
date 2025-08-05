# budget_ui_table.py - Manages the categories table UI
import tkinter as tk
from tkinter import ttk
from budget_models import ViewMode

class TableManager:
    """Manages the categories table display"""
    
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
        self.table_frame = None
        self.category_labels = {}
        self.spending_entries = {}
    
    def create_categories_table(self):
        """Create the categories table"""
        # Table frame
        self.table_frame = ttk.Frame(self.parent_frame)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create headers
        self._create_table_headers()
        
        # Create category rows
        self.create_category_rows()
    
    def _create_table_headers(self):
        """Create table headers"""
        headers = ["Category", "% of Income", "Budgeted ($)", "Actual Spent ($)", "Difference ($)", "Status"]
        for i, header in enumerate(headers):
            label = ttk.Label(self.table_frame, text=header, font=("", 10, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        for i in range(len(headers)):
            self.table_frame.columnconfigure(i, weight=1)
    
    def create_category_rows(self):
        """Create rows for each category"""
        # Clear existing rows (except header)
        for widget in self.table_frame.winfo_children()[6:]:  # Skip header row
            widget.destroy()
        
        # Clear references
        self.category_labels.clear()
        self.spending_entries.clear()
        self.app.actual_spending.clear()
        
        # Get current scenario
        scenario = self.app.budget_data.get_scenario(self.app.current_scenario_name)
        
        # Create rows
        row = 1
        for category_name in scenario.get_all_categories().keys():
            self._create_category_row(category_name, row)
            row += 1
    
    def _create_category_row(self, category_name, row):
        """Create a single category row"""
        # Initialize spending variables for all view modes
        self.app.actual_spending[category_name] = {
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
        
        # Actual spent (editable)
        actual_entry = ttk.Entry(self.table_frame, 
                               textvariable=self.app.actual_spending[category_name][self.app.view_mode], 
                               width=12)
        actual_entry.grid(row=row, column=3, padx=5, pady=2, sticky="ew")
        actual_entry.bind("<KeyRelease>", lambda e, cat=category_name: self.app.on_spending_change(cat))
        self.spending_entries[category_name] = actual_entry
        
        # Difference
        diff_label = ttk.Label(self.table_frame, text="")
        diff_label.grid(row=row, column=4, padx=5, pady=2, sticky="ew")
        self.category_labels[f"{category_name}_diff"] = diff_label
        
        # Status
        status_label = ttk.Label(self.table_frame, text="")
        status_label.grid(row=row, column=5, padx=5, pady=2, sticky="ew")
        self.category_labels[f"{category_name}_status"] = status_label
    
    def update_spending_entries(self):
        """Update spending entry widgets to use current view mode"""
        for category_name, entry in self.spending_entries.items():
            # Update the textvariable to the current view mode
            entry.config(textvariable=self.app.actual_spending[category_name][self.app.view_mode])
    
    def update_category_display(self, category_results):
        """Update category display with calculation results"""
        for category_name, result in category_results.items():
            # Update category name with fixed indicator if needed
            display_name = category_name
            scenario = self.app.budget_data.get_scenario(self.app.current_scenario_name)
            category = scenario.get_category(category_name)
            
            if self.app.config.show_fixed_indicators and category.category_type.name == "FIXED_DOLLAR":
                display_name = f"{category_name} (Fixed)"
            
            self.category_labels[f"{category_name}_name"].config(text=display_name)
            
            # Update percentage
            if self.app.config.show_percentages:
                self.category_labels[f"{category_name}_perc"].config(text=f"{result.percentage:.1f}%")
            else:
                self.category_labels[f"{category_name}_perc"].config(text="")
            
            # Format currency
            currency = self.app.config.currency_symbol
            decimal_places = self.app.config.decimal_places
            
            # Update amounts
            self.category_labels[f"{category_name}_budget"].config(
                text=f"{currency}{result.budgeted:.{decimal_places}f}")
            self.category_labels[f"{category_name}_diff"].config(
                text=f"{currency}{result.difference:.{decimal_places}f}")
            self.category_labels[f"{category_name}_status"].config(
                text=result.status, foreground=result.color)