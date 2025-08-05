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
            
    # Add this method to your TableManager class in budget_ui_table.py

    def update_spending_entries(self):
        """Update spending entry widgets to use current view mode - ENHANCED"""
        print(f"🔄 Updating spending entries for view mode: {self.app.view_mode.value}")
        
        for category_name, entry in self.spending_entries.items():
            try:
                # Get the current view mode variable
                current_var = self.app.actual_spending[category_name][self.app.view_mode]
                
                # Update the textvariable to the current view mode
                entry.config(textvariable=current_var)
                
                # Force the entry to display the current value
                entry.update()
                
                print(f"📝 Updated {category_name} entry: ${current_var.get():.2f}")
                
            except Exception as e:
                print(f"❌ Error updating entry for {category_name}: {e}")

    def recreate_spending_entries_if_needed(self):
        """Recreate spending entries if categories have changed"""
        try:
            # Get current scenario categories
            scenario = self.app.budget_data.get_scenario(self.app.current_scenario_name)
            current_categories = set(scenario.get_all_categories().keys())
            existing_categories = set(self.spending_entries.keys())
            
            # Check if categories have changed
            if current_categories != existing_categories:
                print(f"🔄 Categories changed - recreating table")
                self.create_category_rows()
            else:
                # Just update existing entries
                self.update_spending_entries()
                
        except Exception as e:
            print(f"❌ Error checking/updating spending entries: {e}")

    def force_entry_refresh(self):
        """Force all entry widgets to refresh their displayed values"""
        print(f"🔄 Force refreshing all entry widgets")
        
        for category_name, entry in self.spending_entries.items():
            try:
                # Get current value from the active view mode
                current_value = self.app.actual_spending[category_name][self.app.view_mode].get()
                
                # Temporarily clear and reset the entry to force refresh
                entry.delete(0, 'end')
                entry.insert(0, f"{current_value:.2f}")
                
                print(f"🔄 Force refreshed {category_name}: ${current_value:.2f}")
                
            except Exception as e:
                print(f"❌ Error force refreshing {category_name}: {e}")

    def debug_spending_entries(self):
        """Debug method to check spending entry states"""
        print(f"🔍 === SPENDING ENTRIES DEBUG ===")
        print(f"Current view mode: {self.app.view_mode.value}")
        
        for category_name, entry in self.spending_entries.items():
            try:
                # Get values from all view modes
                monthly_val = self.app.actual_spending[category_name][ViewMode.MONTHLY].get()
                first_val = self.app.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].get()
                second_val = self.app.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].get()
                
                # Get current entry value
                entry_var = entry.cget('textvariable')
                entry_val = entry.get()
                
                print(f"📊 {category_name}:")
                print(f"   Monthly: ${monthly_val:.2f}")
                print(f"   First PC: ${first_val:.2f}")
                print(f"   Second PC: ${second_val:.2f}")
                print(f"   Entry shows: '{entry_val}'")
                print(f"   Entry var: {entry_var}")
                
            except Exception as e:
                print(f"❌ Error debugging {category_name}: {e}")
        
        print(f"🔍 === END DEBUG ===")

    # Also add this method to handle view mode changes properly
    def on_view_mode_change(self):
        """Handle when user changes view mode - updates all entries"""
        print(f"🔄 View mode changed to: {self.app.view_mode.value}")
        
        # Update all spending entries to use new view mode
        self.update_spending_entries()
        
        # Force UI refresh
        self.app.root.update_idletasks()
        
        print(f"✅ View mode change complete")