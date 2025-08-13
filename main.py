"""
Main Budget App
Multi-Month Budget Tracker with Charts and Dark Mode Support
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import calendar

# Import our modules
from budget_categories import create_real_categories, ViewMode, CategoryType, CategoryGroup
from budget_database import BudgetDatabase
from budget_charts import BudgetCharts

# Try to import sv-ttk for dark theme
try:
    import sv_ttk
    SV_TTK_AVAILABLE = True
except ImportError:
    SV_TTK_AVAILABLE = False
    print("sv-ttk not found. Install with: pip install sv-ttk")

class MultiBudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Month Budget Tracker")
        self.root.geometry("1000x800")
        
        # Set up proper window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Apply sv-ttk dark theme
        self.setup_theme()
        
        # Initialize components
        self.database = BudgetDatabase("budget_multi.db")
        
        # Current state
        today = date.today()
        self.current_month = today.month
        self.current_year = today.year
        self.view_mode = ViewMode.MONTHLY
        
        # Variables
        self.first_paycheck = tk.DoubleVar(value=2164.77)
        self.second_paycheck = tk.DoubleVar(value=2154.42)
        
        # Categories
        self.categories = create_real_categories()
        
        # Create UI
        self.create_widgets()
        self.populate_month_selector()
        self.load_month_data()
        self.update_calculations()
    
    def on_closing(self):
        """Handle window closing - clean shutdown"""
        try:
            # Close any matplotlib figures to prevent memory leaks
            import matplotlib.pyplot as plt
            plt.close('all')
            
            # Destroy the window and quit the application
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Force close even if there's an error
            self.root.quit()
            self.root.destroy()
    
    def setup_theme(self):
        """Apply sv-ttk dark theme"""
        if SV_TTK_AVAILABLE:
            sv_ttk.set_theme("dark")
            print("✅ Applied sv-ttk dark theme")
        else:
            print("⚠️ sv-ttk not available - using default theme")
    
    def create_widgets(self):
        """Create the main UI with tabs"""
        # Title
        title_label = ttk.Label(self.root, text="Multi-Month Budget Tracker", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Budget tab
        self.budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_frame, text="📊 Budget")
        self.create_budget_tab()
        
        # Charts tab
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="📈 Charts")
        self.create_charts_tab()
    
    def create_budget_tab(self):
        """Create the budget tab"""
        # Month selection frame
        month_frame = ttk.LabelFrame(self.budget_frame, text="Select Month", padding=10)
        month_frame.pack(fill="x", padx=20, pady=5)
        
        # Month selector
        month_row = ttk.Frame(month_frame)
        month_row.pack()
        
        ttk.Label(month_row, text="Month:").pack(side="left", padx=5)
        self.month_var = tk.StringVar()
        self.month_combo = ttk.Combobox(month_row, textvariable=self.month_var,
                                       values=list(calendar.month_name)[1:],
                                       state="readonly", width=15)
        self.month_combo.pack(side="left", padx=5)
        self.month_combo.bind("<<ComboboxSelected>>", self.on_month_change)
        
        ttk.Label(month_row, text="Year:").pack(side="left", padx=(20, 5))
        self.year_var = tk.StringVar()
        self.year_combo = ttk.Combobox(month_row, textvariable=self.year_var,
                                      state="readonly", width=8)
        self.year_combo.pack(side="left", padx=5)
        self.year_combo.bind("<<ComboboxSelected>>", self.on_month_change)
        
        # View mode selection
        ttk.Label(month_row, text="View:").pack(side="left", padx=(20, 5))
        self.view_var = tk.StringVar(value=self.view_mode.value)
        view_combo = ttk.Combobox(month_row, textvariable=self.view_var,
                                 values=[mode.value for mode in ViewMode],
                                 state="readonly", width=15)
        view_combo.pack(side="left", padx=5)
        view_combo.bind("<<ComboboxSelected>>", self.on_view_change)
        
        # Current month indicator
        self.current_month_label = ttk.Label(month_row, text="", 
                                           font=("Arial", 10, "bold"))
        self.current_month_label.pack(side="left", padx=20)
        
        # Paycheck inputs frame
        paycheck_frame = ttk.LabelFrame(self.budget_frame, text="Monthly Paychecks", padding=10)
        paycheck_frame.pack(fill="x", padx=20, pady=10)
        
        # First paycheck
        ttk.Label(paycheck_frame, text="1st Paycheck (6th): $").grid(row=0, column=0, sticky="w", padx=5)
        first_entry = ttk.Entry(paycheck_frame, textvariable=self.first_paycheck, width=15)
        first_entry.grid(row=0, column=1, padx=5)
        first_entry.bind("<KeyRelease>", self.on_paycheck_change)
        
        # Second paycheck
        ttk.Label(paycheck_frame, text="2nd Paycheck (21st): $").grid(row=0, column=2, sticky="w", padx=5)
        second_entry = ttk.Entry(paycheck_frame, textvariable=self.second_paycheck, width=15)
        second_entry.grid(row=0, column=3, padx=5)
        second_entry.bind("<KeyRelease>", self.on_paycheck_change)
        
        # Monthly total
        self.total_label = ttk.Label(paycheck_frame, text="Monthly Total: $4,319.19", 
                                    font=("Arial", 12, "bold"))
        self.total_label.grid(row=0, column=4, padx=20)
        
        # Categories frame - Smart expansion that leaves room for summary and buttons
        categories_frame = ttk.LabelFrame(self.budget_frame, text="Budget Categories", padding=10)
        categories_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Headers
        headers = ["Category", "% of Income", "Budgeted ($)", "Actual Spent ($)", "Difference ($)", "Status"]
        for i, header in enumerate(headers):
            label = ttk.Label(categories_frame, text=header, font=("Arial", 10, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        for i in range(len(headers)):
            categories_frame.columnconfigure(i, weight=1)
        
        # Category rows
        self.category_widgets = {}
        self.spending_entries = {}
        row = 1
        for category_name, data in self.categories.items():
            # Category name
            cat_label = ttk.Label(categories_frame, text=category_name)
            cat_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # Percentage
            perc_label = ttk.Label(categories_frame, text="")
            perc_label.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            
            # Budgeted amount
            budget_label = ttk.Label(categories_frame, text="$0.00")
            budget_label.grid(row=row, column=2, padx=5, pady=2, sticky="ew")
            
            # Actual spent (editable)
            actual_entry = ttk.Entry(categories_frame, textvariable=data['spending'], width=12)
            actual_entry.grid(row=row, column=3, padx=5, pady=2, sticky="ew")
            actual_entry.bind("<KeyRelease>", self.on_spending_change)
            self.spending_entries[category_name] = actual_entry
            
            # Difference
            diff_label = ttk.Label(categories_frame, text="$0.00")
            diff_label.grid(row=row, column=4, padx=5, pady=2, sticky="ew")
            
            # Status
            status_label = ttk.Label(categories_frame, text="Not Set")
            status_label.grid(row=row, column=5, padx=5, pady=2, sticky="ew")
            
            # Store widget references
            self.category_widgets[category_name] = {
                'perc_label': perc_label,
                'budget_label': budget_label,
                'diff_label': diff_label,
                'status_label': status_label
            }
            
            row += 1
        
        # Summary section - Don't expand, fixed size
        summary_frame = ttk.LabelFrame(self.budget_frame, text="Summary", padding=10)
        summary_frame.pack(fill="x", padx=20, pady=(5, 10))  # Added bottom padding
        
        self.summary_labels = {}
        summary_row = ttk.Frame(summary_frame)
        summary_row.pack(fill="x")
        
        # Create summary labels
        labels = ["Total Budgeted:", "Total Spent:", "Remaining:", "Over/Under:"]
        for i, label in enumerate(labels):
            ttk.Label(summary_row, text=label).grid(row=0, column=i*2, padx=10, sticky="e")
            self.summary_labels[label] = ttk.Label(summary_row, text="$0.00", font=("Arial", 11, "bold"))
            self.summary_labels[label].grid(row=0, column=i*2+1, padx=10, sticky="w")
        
        # Buttons frame - Don't expand, fixed size at bottom
        button_frame = ttk.Frame(self.budget_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 10))  # No expansion, just fill width
        
        # Create buttons with proper spacing - centered
        buttons_container = ttk.Frame(button_frame)
        buttons_container.pack(anchor="center")  # Center the buttons
        
        ttk.Button(buttons_container, text="Save Month", command=self.save_month_data).pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Clear Month", command=self.clear_month).pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Copy from Month", command=self.copy_from_month).pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Delete Month", command=self.delete_month).pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Show Database", command=self.show_database).pack(side="left", padx=5)
    
    def create_charts_tab(self):
        """Create the charts tab"""
        # Chart controls frame
        controls_frame = ttk.LabelFrame(self.charts_frame, text="Chart Options", padding=10)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Chart type selection
        ttk.Label(controls_frame, text="Chart Type:").pack(side="left", padx=5)
        self.chart_type_var = tk.StringVar(value="Monthly Spending Trends")
        chart_combo = ttk.Combobox(controls_frame, textvariable=self.chart_type_var,
                                  values=["Monthly Spending Trends", "Category Breakdown", "Budget vs Actual", 
                                         "Savings Progress", "Income vs Expenses"],
                                  state="readonly", width=25)
        chart_combo.pack(side="left", padx=5)
        chart_combo.bind("<<ComboboxSelected>>", self.on_chart_change)
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh Charts", command=self.refresh_charts).pack(side="left", padx=20)
        
        # Chart display frame
        self.chart_frame = ttk.Frame(self.charts_frame)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initialize charts component
        self.charts = BudgetCharts(self.chart_frame, SV_TTK_AVAILABLE)
        self.refresh_charts()
    
    def populate_month_selector(self):
        """Populate month and year selectors"""
        # Set current month
        self.month_var.set(calendar.month_name[self.current_month])
        
        # Populate years (current year ± 2)
        current_year = date.today().year
        years = [str(year) for year in range(current_year - 2, current_year + 3)]
        self.year_combo['values'] = years
        self.year_var.set(str(self.current_year))
        
        # Update current month indicator
        self.update_current_month_indicator()
    
    def update_current_month_indicator(self):
        """Update current month indicator"""
        today = date.today()
        if self.current_month == today.month and self.current_year == today.year:
            self.current_month_label.config(text="(Current Month)")
        else:
            self.current_month_label.config(text="")
    
    def on_month_change(self, event=None):
        """Handle month/year selection change"""
        try:
            # Get selected month number
            month_name = self.month_var.get()
            if month_name:
                self.current_month = list(calendar.month_name).index(month_name)
            
            # Get selected year
            year_str = self.year_var.get()
            if year_str:
                self.current_year = int(year_str)
            
            # Update current month indicator
            self.update_current_month_indicator()
            
            # Load data for selected month
            self.load_month_data()
            self.update_calculations()
            
        except Exception as e:
            print(f"Error changing month: {e}")
    
    def on_view_change(self, event=None):
        """Handle view mode change"""
        view_str = self.view_var.get()
        
        if view_str == "First Paycheck":
            self.view_mode = ViewMode.FIRST_PAYCHECK
        elif view_str == "Second Paycheck":
            self.view_mode = ViewMode.SECOND_PAYCHECK
        else:
            self.view_mode = ViewMode.MONTHLY
        
        self.update_calculations()
    
    def load_month_data(self):
        """Load data for the currently selected month"""
        first, second, spending_data = self.database.load_month_data(self.current_month, self.current_year)
        
        if first is not None and second is not None:
            self.first_paycheck.set(first)
            self.second_paycheck.set(second)
        else:
            # No data for this month - use defaults
            self.first_paycheck.set(2164.77)
            self.second_paycheck.set(2154.42)
        
        # Clear current spending
        for data in self.categories.values():
            data['spending'].set(0)
        
        # Load spending amounts
        for category, amount in spending_data.items():
            if category in self.categories:
                self.categories[category]['spending'].set(amount)
    
    def save_month_data(self):
        """Save current data for the selected month"""
        # Get current spending data
        categories_data = {}
        for category_name, data in self.categories.items():
            try:
                amount = data['spending'].get()
            except:
                amount = 0
            categories_data[category_name] = amount
        
        # Save to database
        success = self.database.save_month_data(
            self.current_month, 
            self.current_year, 
            self.first_paycheck.get(), 
            self.second_paycheck.get(), 
            categories_data
        )
        
        if success:
            month_name = calendar.month_name[self.current_month]
            messagebox.showinfo("Success", f"Data saved for {month_name} {self.current_year}!")
            
            # Refresh charts if we're on charts tab
            if hasattr(self, 'notebook') and self.notebook.index(self.notebook.select()) == 1:
                self.refresh_charts()
        else:
            messagebox.showerror("Error", "Failed to save data!")
    
    def clear_month(self):
        """Clear spending data for current month"""
        month_name = calendar.month_name[self.current_month]
        if messagebox.askyesno("Confirm", f"Clear all spending data for {month_name} {self.current_year}?"):
            for data in self.categories.values():
                data['spending'].set(0)
            self.update_calculations()
    
    def copy_from_month(self):
        """Copy data from another month - placeholder for now"""
        messagebox.showinfo("Feature", "Copy from Month feature - Coming soon!")
    
    def delete_month(self):
        """Delete data for current month"""
        month_name = calendar.month_name[self.current_month]
        
        if messagebox.askyesno("Confirm Delete", 
            f"Permanently delete ALL data for {month_name} {self.current_year}?\n\n"
            f"This cannot be undone."):
            
            success = self.database.delete_month_data(self.current_month, self.current_year)
            
            if success:
                # Clear UI
                for data in self.categories.values():
                    data['spending'].set(0)
                self.first_paycheck.set(2164.77)
                self.second_paycheck.set(2154.42)
                
                self.update_calculations()
                messagebox.showinfo("Success", f"Deleted data for {month_name} {self.current_year}")
                
                # Refresh charts if we're on charts tab
                if hasattr(self, 'notebook') and self.notebook.index(self.notebook.select()) == 1:
                    self.refresh_charts()
            else:
                messagebox.showerror("Error", "Failed to delete data!")
    
    def on_paycheck_change(self, event=None):
        """Handle paycheck amount changes"""
        self.update_calculations()
        # Refresh charts if we're on the charts tab
        if hasattr(self, 'notebook') and self.notebook.index(self.notebook.select()) == 1:
            self.refresh_charts()
    
    def on_spending_change(self, event=None):
        """Handle spending amount changes"""
        self.root.after(100, self.update_calculations)
        # Refresh charts if we're on the charts tab
        if hasattr(self, 'notebook') and self.notebook.index(self.notebook.select()) == 1:
            self.root.after(200, self.refresh_charts)
    
    def update_calculations(self):
        """Update all budget calculations and display with auto-adjusting Flex/Buffer"""
        try:
            # Get paycheck amounts
            first = self.first_paycheck.get()
            second = self.second_paycheck.get()
            total_income = first + second
            
            # Update monthly total display
            self.total_label.config(text=f"Monthly Total: ${total_income:,.2f}")
            
            # Calculate total percentage used by fixed dollar categories
            fixed_dollar_total = 0
            for category_name, data in self.categories.items():
                category = data['category']
                if category.category_type == CategoryType.FIXED_DOLLAR:
                    if total_income > 0:
                        fixed_dollar_total += (category.monthly_amount / total_income) * 100
            
            # Calculate total of fixed percentage categories (excluding Flex/Buffer)
            fixed_percentage_total = 0
            for category_name, data in self.categories.items():
                category = data['category']
                if category.category_type == CategoryType.FIXED_PERCENTAGE and category_name != "Flex/Buffer":
                    fixed_percentage_total += category.percentage
            
            # Auto-adjust Flex/Buffer to make total = 100%
            remaining_percentage = 100 - fixed_dollar_total - fixed_percentage_total
            
            total_budgeted = 0
            total_spent = 0
            
            # Update each category
            for category_name, data in self.categories.items():
                category = data['category']
                
                # Auto-adjust Flex/Buffer percentage
                if category_name == "Flex/Buffer":
                    category.percentage = max(0, remaining_percentage)
                
                # Calculate budgeted amount
                budgeted, percentage = category.calculate_budgeted_amount(first, second, self.view_mode)
                total_budgeted += budgeted
                
                # Get actual spent
                try:
                    spent = data['spending'].get()
                except:
                    spent = 0
                total_spent += spent
                
                # Calculate remaining
                remaining = budgeted - spent
                
                # Update labels
                widgets = self.category_widgets[category_name]
                widgets['perc_label'].config(text=f"{percentage:.1f}%")
                widgets['budget_label'].config(text=f"${budgeted:.2f}")
                widgets['diff_label'].config(text=f"${remaining:.2f}")
                
                # Update status and color
                status, color = category.get_status_and_color(budgeted, spent)
                widgets['status_label'].config(text=status, foreground=color)
            
            # Update summary
            total_remaining = total_income - total_spent
            over_under = total_spent - total_budgeted
            
            self.summary_labels["Total Budgeted:"].config(text=f"${total_budgeted:.2f}")
            self.summary_labels["Total Spent:"].config(text=f"${total_spent:.2f}")
            self.summary_labels["Remaining:"].config(text=f"${total_remaining:.2f}")
            
            # Over/Under with color
            if over_under > 0:
                over_under_text = f"${over_under:.2f} Over"
                over_under_color = "red"
            elif over_under < 0:
                over_under_text = f"${abs(over_under):.2f} Under"
                over_under_color = "green"
            else:
                over_under_text = "$0.00 On Target"
                over_under_color = "blue"
            
            self.summary_labels["Over/Under:"].config(text=over_under_text, foreground=over_under_color)
                
        except Exception as e:
            print(f"Error in calculations: {e}")
    
    def refresh_charts(self):
        """Refresh charts based on current selection"""
        chart_type = self.chart_type_var.get()
        
        # Clear existing charts
        self.charts.clear_charts()
        
        if chart_type == "Monthly Spending Trends":
            data = self.database.get_all_chart_data()
            self.charts.create_monthly_trends_chart(data)
        elif chart_type == "Category Breakdown":
            self.charts.create_category_breakdown_chart(self.categories, self.current_month, self.current_year)
        elif chart_type == "Budget vs Actual":
            self.charts.create_budget_vs_actual_chart(
                self.categories, 
                self.first_paycheck.get(), 
                self.second_paycheck.get(), 
                self.view_mode, 
                self.current_month, 
                self.current_year
            )
        elif chart_type == "Savings Progress":
            data = self.database.get_all_chart_data()
            self.charts.create_savings_progress_chart(data)
        elif chart_type == "Income vs Expenses":
            data = self.database.get_all_chart_data()
            self.charts.create_income_vs_expenses_chart(data)
    
    def on_chart_change(self, event=None):
        """Handle chart type change"""
        self.refresh_charts()
    
    def show_database(self):
        """Show current database contents"""
        try:
            paychecks, spending = self.database.get_database_contents()
            
            # Create window
            db_window = tk.Toplevel(self.root)
            db_window.title("Database Contents")
            db_window.geometry("800x600")
            
            # Apply sv-ttk theme to popup
            if SV_TTK_AVAILABLE:
                sv_ttk.set_theme("dark")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(db_window)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Paychecks tab
            paycheck_frame = ttk.Frame(notebook)
            notebook.add(paycheck_frame, text="Paychecks")
            
            paycheck_text = tk.Text(paycheck_frame, wrap=tk.WORD)
            paycheck_scroll = ttk.Scrollbar(paycheck_frame, orient="vertical", command=paycheck_text.yview)
            paycheck_text.configure(yscrollcommand=paycheck_scroll.set)
            
            paycheck_text.pack(side="left", fill="both", expand=True)
            paycheck_scroll.pack(side="right", fill="y")
            
            # Spending tab
            spending_frame = ttk.Frame(notebook)
            notebook.add(spending_frame, text="Spending")
            
            spending_text = tk.Text(spending_frame, wrap=tk.WORD)
            spending_scroll = ttk.Scrollbar(spending_frame, orient="vertical", command=spending_text.yview)
            spending_text.configure(yscrollcommand=spending_scroll.set)
            
            spending_text.pack(side="left", fill="both", expand=True)
            spending_scroll.pack(side="right", fill="y")
            
            # Format and display paycheck data
            output = "=== PAYCHECKS DATABASE ===\n\n"
            if paychecks:
                output += "Month/Year | First Paycheck | Second Paycheck | Total Income | Date Saved\n"
                output += "-" * 80 + "\n"
                for row in paychecks:
                    month_name = calendar.month_name[row[1]][:3]
                    output += f"{month_name} {row[2]} | ${row[3]:.2f} | ${row[4]:.2f} | ${row[5]:.2f} | {row[6]}\n"
            else:
                output += "No paycheck data found.\n"
            
            paycheck_text.insert("1.0", output)
            paycheck_text.config(state="disabled")
            
            # Format and display spending data
            output = "=== SPENDING DATABASE ===\n\n"
            if spending:
                current_month_year = None
                for row in spending:
                    month_year = f"{calendar.month_name[row[1]]} {row[2]}"
                    if month_year != current_month_year:
                        output += f"\n=== {month_year} ===\n"
                        current_month_year = month_year
                    
                    output += f"{row[3]}: ${row[4]:.2f}\n"
            else:
                output += "No spending data found.\n"
            
            spending_text.insert("1.0", output)
            spending_text.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show database: {str(e)}")

def main():
    root = tk.Tk()
    
    # Check for sv-ttk and warn if missing
    if not SV_TTK_AVAILABLE:
        messagebox.showwarning("Theme Notice", 
                             "sv-ttk not found!\n\n"
                             "For dark mode, install it:\n"
                             "pip install sv-ttk\n\n"
                             "The app will work with default theme.")
    
    app = MultiBudgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()