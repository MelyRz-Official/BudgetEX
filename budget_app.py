# import tkinter as tk
# from tkinter import ttk, messagebox, filedialog
# import sqlite3
# import os
# from datetime import datetime, date
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.style as mplstyle

# class BudgetApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Personal Budget Manager")
#         self.root.geometry("1400x900")
        
#         # Apply Sun Valley theme
#         try:
#             import sv_ttk
#             sv_ttk.set_theme("dark")
#         except ImportError:
#             print("Sun Valley theme not found. Using default theme.")
#             print("Install with: pip install sv-ttk")
        
#         # Budget scenarios data
#         # Note: fixed_amount=True means the dollar amount stays constant, percentage adjusts
#         # Note: fixed_amount=False means percentage stays constant, dollar amount adjusts
#         self.budget_scenarios = {
#             "July-December 2025": {
#                 "Roth IRA": {"amount": 333.33, "percentage": 8.4, "fixed_amount": False},
#                 "General Savings": {"amount": 769.23, "percentage": 19.3, "fixed_amount": False},
#                 "Vacation Fund": {"amount": 500.00, "percentage": 12.5, "fixed_amount": False},
#                 "HOA": {"amount": 1078.81, "percentage": 27.1, "fixed_amount": True},
#                 "Utilities": {"amount": 60.00, "percentage": 1.5, "fixed_amount": True},
#                 "Subscriptions": {"amount": 90.00, "percentage": 2.3, "fixed_amount": True},
#                 "Groceries": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
#                 "Uber/Lyft": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
#                 "Therapy": {"amount": 44.00, "percentage": 1.1, "fixed_amount": True},
#                 "Dining/Entertainment": {"amount": 150.00, "percentage": 3.8, "fixed_amount": False},
#                 "Flex/Buffer": {"amount": 657.38, "percentage": 16.5, "fixed_amount": False}
#             },
#             "Fresh New Year (Jan-May)": {
#                 "Roth IRA": {"amount": 1400.00, "percentage": 35.2, "fixed_amount": False},
#                 "General Savings": {"amount": 250.00, "percentage": 6.3, "fixed_amount": False},
#                 "Vacation Fund": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
#                 "HOA": {"amount": 1078.81, "percentage": 27.1, "fixed_amount": True},
#                 "Utilities": {"amount": 60.00, "percentage": 1.5, "fixed_amount": True},
#                 "Subscriptions": {"amount": 90.00, "percentage": 2.3, "fixed_amount": True},
#                 "Groceries": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
#                 "Uber/Lyft": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
#                 "Dining/Entertainment": {"amount": 150.00, "percentage": 3.8, "fixed_amount": False},
#                 "Therapy": {"amount": 44.00, "percentage": 1.1, "fixed_amount": True},
#                 "Flex/Buffer": {"amount": 90.94, "percentage": 2.3, "fixed_amount": False}
#             },
#             "Fresh New Year (June-Dec)": {
#                 "Roth IRA": {"amount": 0.00, "percentage": 0.0, "fixed_amount": False},
#                 "General Savings": {"amount": 833.33, "percentage": 20.9, "fixed_amount": False},
#                 "Vacation Fund": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
#                 "HOA": {"amount": 1078.81, "percentage": 27.1, "fixed_amount": True},
#                 "Utilities": {"amount": 60.00, "percentage": 1.5, "fixed_amount": True},
#                 "Subscriptions": {"amount": 90.00, "percentage": 2.3, "fixed_amount": True},
#                 "Groceries": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
#                 "Uber/Lyft": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
#                 "Dining/Entertainment": {"amount": 150.00, "percentage": 3.8, "fixed_amount": False},
#                 "Therapy": {"amount": 44.00, "percentage": 1.1, "fixed_amount": True},
#                 "Flex/Buffer": {"amount": 857.61, "percentage": 21.5, "fixed_amount": False}
#             }
#         }
        
#         self.current_scenario = "July-December 2025"
#         self.paycheck_amount = tk.DoubleVar(value=3984.94)
#         self.actual_spending = {}
#         self.db_filename = "budget_data.db"
        
#         # Initialize database
#         self.init_database()
        
#         # Initialize actual spending data
#         for category in self.budget_scenarios[self.current_scenario]:
#             self.actual_spending[category] = tk.DoubleVar(value=0.0)
        
#         self.create_widgets()
#         self.load_data()
#         self.update_calculations()
        
#     def init_database(self):
#         """Initialize SQLite database"""
#         try:
#             # Use absolute path for better security and clarity
#             db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.db_filename)
#             conn = sqlite3.connect(db_path)
#             cursor = conn.cursor()
            
#             # Create tables
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS budget_data (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     scenario TEXT NOT NULL,
#                     paycheck_amount REAL NOT NULL,
#                     category TEXT NOT NULL,
#                     actual_spent REAL NOT NULL DEFAULT 0.0,
#                     date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                     UNIQUE(scenario, category)
#                 )
#             ''')
            
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS spending_history (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     scenario TEXT NOT NULL,
#                     category TEXT NOT NULL,
#                     amount REAL NOT NULL,
#                     description TEXT,
#                     date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                 )
#             ''')
            
#             conn.commit()
#             conn.close()
            
#             # Store the full path for later use
#             self.db_path = db_path
            
#         except Exception as e:
#             messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
#             self.db_path = self.db_filename  # Fallback to relative path
        
#     def create_widgets(self):
#         # Create notebook for tabs
#         self.notebook = ttk.Notebook(self.root)
#         self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
#         # Main Budget Tab
#         self.budget_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.budget_frame, text="Budget Overview")
        
#         # Dashboard Tab
#         self.dashboard_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.dashboard_frame, text="Dashboard")
        
#         self.create_budget_tab()
#         self.create_dashboard_tab()
        
#     def create_budget_tab(self):
#         # Top frame for controls
#         top_frame = ttk.Frame(self.budget_frame)
#         top_frame.pack(fill="x", padx=10, pady=5)
        
#         # Scenario selection
#         ttk.Label(top_frame, text="Budget Scenario:").pack(side="left", padx=5)
#         self.scenario_var = tk.StringVar(value=self.current_scenario)
#         scenario_combo = ttk.Combobox(top_frame, textvariable=self.scenario_var, 
#                                     values=list(self.budget_scenarios.keys()), 
#                                     state="readonly", width=25)
#         scenario_combo.pack(side="left", padx=5)
#         scenario_combo.bind("<<ComboboxSelected>>", self.change_scenario)
        
#         # Paycheck amount
#         ttk.Label(top_frame, text="Paycheck Amount: $").pack(side="left", padx=(20, 5))
#         paycheck_entry = ttk.Entry(top_frame, textvariable=self.paycheck_amount, width=12)
#         paycheck_entry.pack(side="left", padx=5)
#         paycheck_entry.bind("<KeyRelease>", lambda e: self.update_calculations())
        
#         # Buttons
#         button_frame = ttk.Frame(top_frame)
#         button_frame.pack(side="right", padx=10)
        
#         ttk.Button(button_frame, text="Save Data", command=self.save_data).pack(side="left", padx=2)
#         ttk.Button(button_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=2)
#         ttk.Button(button_frame, text="Clear All Spending", command=self.clear_all_spending).pack(side="left", padx=2)
        
#         # Main content frame with grid
#         content_frame = ttk.Frame(self.budget_frame)
#         content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
#         # Create frame for the editable grid
#         grid_frame = ttk.Frame(content_frame)
#         grid_frame.pack(fill="both", expand=True)
        
#         # Headers
#         headers = ["Category", "% of Income", "Budgeted ($)", "Actual Spent ($)", "Difference ($)", "Status"]
#         for i, header in enumerate(headers):
#             label = ttk.Label(grid_frame, text=header, font=("", 10, "bold"))
#             label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
#         # Configure grid weights
#         for i in range(len(headers)):
#             grid_frame.columnconfigure(i, weight=1)
        
#         # Store entry widgets for actual spending
#         self.spending_entries = {}
#         self.category_labels = {}
        
#         # Create rows for each category
#         self.create_budget_rows(grid_frame)
        
#         # Summary frame
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
    
#     def create_budget_rows(self, parent):
#         """Create editable budget rows"""
#         row = 1
#         for category in self.budget_scenarios[self.current_scenario]:
#             # Category name
#             cat_label = ttk.Label(parent, text=category)
#             cat_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
#             self.category_labels[category] = cat_label
            
#             # Percentage
#             perc_label = ttk.Label(parent, text="")
#             perc_label.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category}_perc"] = perc_label
            
#             # Budgeted amount
#             budget_label = ttk.Label(parent, text="")
#             budget_label.grid(row=row, column=2, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category}_budget"] = budget_label
            
#             # Actual spent (editable entry)
#             actual_var = tk.DoubleVar(value=0.0)
#             self.actual_spending[category] = actual_var
#             actual_entry = ttk.Entry(parent, textvariable=actual_var, width=12)
#             actual_entry.grid(row=row, column=3, padx=5, pady=2, sticky="ew")
#             actual_entry.bind("<KeyRelease>", lambda e, cat=category: self.on_spending_change(cat))
#             self.spending_entries[category] = actual_entry
            
#             # Difference
#             diff_label = ttk.Label(parent, text="")
#             diff_label.grid(row=row, column=4, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category}_diff"] = diff_label
            
#             # Status
#             status_label = ttk.Label(parent, text="")
#             status_label.grid(row=row, column=5, padx=5, pady=2, sticky="ew")
#             self.category_labels[f"{category}_status"] = status_label
            
#             row += 1
    
#     def on_spending_change(self, category):
#         """Handle changes to spending entries"""
#         self.root.after(100, self.update_calculations)  # Small delay for smooth typing
    
#     def create_dashboard_tab(self):
#         # Set matplotlib to use dark style
#         plt.style.use('dark_background')
        
#         # Create matplotlib figure
#         self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 7))
#         self.fig.patch.set_facecolor('#1c1c1c')
        
#         # Create canvas
#         self.canvas = FigureCanvasTkAgg(self.fig, self.dashboard_frame)
#         self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
#         # Refresh button
#         ttk.Button(self.dashboard_frame, text="Refresh Charts", 
#                   command=self.update_charts).pack(pady=5)
    
#     def change_scenario(self, event=None):
#         self.current_scenario = self.scenario_var.get()
        
#         # Save current data before switching
#         self.save_data()
        
#         # Update actual spending variables for new scenario
#         old_spending = {}
#         for category, var in self.actual_spending.items():
#             old_spending[category] = var.get()
        
#         self.actual_spending = {}
        
#         # Recreate the budget rows for new scenario
#         for widget in self.category_labels.values():
#             widget.destroy()
#         for widget in self.spending_entries.values():
#             widget.destroy()
            
#         self.category_labels = {}
#         self.spending_entries = {}
        
#         # Find the grid frame and recreate rows
#         content_frame = self.budget_frame.winfo_children()[1]  # Second child is content_frame
#         grid_frame = content_frame.winfo_children()[0]  # First child is grid_frame
        
#         self.create_budget_rows(grid_frame)
#         self.load_data()
#         self.update_calculations()
#         self.update_charts()
    
#     def update_calculations(self):
#         paycheck = self.paycheck_amount.get()
#         total_budgeted = 0
#         total_spent = 0
        
#         # Update each row
#         for category, data in self.budget_scenarios[self.current_scenario].items():
#             if data["fixed_amount"]:
#                 # Fixed amount: dollar amount stays same, percentage adjusts
#                 budgeted = data["amount"]
#                 percentage = (budgeted / paycheck * 100) if paycheck > 0 else 0
#             else:
#                 # Percentage-based: percentage stays same, dollar amount adjusts
#                 percentage = data["percentage"]
#                 budgeted = (percentage / 100) * paycheck
            
#             try:
#                 actual = self.actual_spending[category].get()
#             except:
#                 actual = 0.0
                
#             difference = budgeted - actual
            
#             total_budgeted += budgeted
#             total_spent += actual
            
#             # Determine status and color
#             if actual == 0:
#                 status = "Not Set"
#                 color = "gray"
#             elif difference > 0:
#                 status = "Under Budget"
#                 color = "green"
#             elif difference < 0:
#                 status = "Over Budget"
#                 color = "red"
#             else:
#                 status = "On Target"
#                 color = "blue"
            
#             # Update labels with indicator for fixed amounts
#             category_display = f"{category} (Fixed)" if data["fixed_amount"] else category
#             self.category_labels[category].config(text=category_display)
#             self.category_labels[f"{category}_perc"].config(text=f"{percentage:.1f}%")
#             self.category_labels[f"{category}_budget"].config(text=f"${budgeted:.2f}")
#             self.category_labels[f"{category}_diff"].config(text=f"${difference:.2f}")
#             self.category_labels[f"{category}_status"].config(text=status, foreground=color)
        
#         # Update summary
#         remaining = paycheck - total_spent
#         over_under = total_spent - total_budgeted
        
#         self.summary_labels["Total Budgeted:"].config(text=f"${total_budgeted:.2f}")
#         self.summary_labels["Total Spent:"].config(text=f"${total_spent:.2f}")
#         self.summary_labels["Remaining:"].config(text=f"${remaining:.2f}")
        
#         if over_under > 0:
#             self.summary_labels["Over/Under:"].config(text=f"${over_under:.2f} OVER", foreground="red")
#         elif over_under < 0:
#             self.summary_labels["Over/Under:"].config(text=f"${abs(over_under):.2f} UNDER", foreground="green")
#         else:
#             self.summary_labels["Over/Under:"].config(text="$0.00 ON TARGET", foreground="blue")
    
#     def update_charts(self):
#         self.ax1.clear()
#         self.ax2.clear()
        
#         paycheck = self.paycheck_amount.get()
#         categories = []
#         budgeted_amounts = []
#         actual_amounts = []
        
#         for category, data in self.budget_scenarios[self.current_scenario].items():
#             categories.append(category.replace(' ', '\n'))  # Line breaks for better display
            
#             if data["fixed_amount"]:
#                 # Fixed amount: dollar amount stays same
#                 budgeted_amounts.append(data["amount"])
#             else:
#                 # Percentage-based: calculate from percentage
#                 budgeted_amounts.append((data["percentage"] / 100) * paycheck)
            
#             try:
#                 actual_amounts.append(self.actual_spending[category].get())
#             except:
#                 actual_amounts.append(0.0)
        
#         # Pie chart of budgeted amounts
#         colors = plt.cm.Set3(range(len(categories)))
#         self.ax1.pie(budgeted_amounts, labels=categories, autopct='%1.1f%%', 
#                     startangle=90, colors=colors)
#         self.ax1.set_title("Budget Allocation", fontsize=14, fontweight='bold')
        
#         # Bar chart comparison
#         x_pos = range(len(categories))
#         width = 0.35
        
#         bars1 = self.ax2.bar([x - width/2 for x in x_pos], budgeted_amounts, width, 
#                     label='Budgeted', alpha=0.8, color='#4CAF50')
#         bars2 = self.ax2.bar([x + width/2 for x in x_pos], actual_amounts, width, 
#                     label='Actual', alpha=0.8, color='#FF6B6B')
        
#         self.ax2.set_xlabel('Categories', fontweight='bold')
#         self.ax2.set_ylabel('Amount ($)', fontweight='bold')
#         self.ax2.set_title('Budgeted vs Actual Spending', fontsize=14, fontweight='bold')
#         self.ax2.set_xticks(x_pos)
#         self.ax2.set_xticklabels(categories, rotation=45, ha='right')
#         self.ax2.legend()
#         self.ax2.grid(True, alpha=0.3)
        
#         # Add value labels on bars
#         for bar in bars1:
#             height = bar.get_height()
#             self.ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
#                          f'${height:.0f}', ha='center', va='bottom', fontsize=8)
        
#         for bar in bars2:
#             height = bar.get_height()
#             if height > 0:
#                 self.ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
#                              f'${height:.0f}', ha='center', va='bottom', fontsize=8)
        
#         self.fig.tight_layout()
#         self.canvas.draw()
    
#     def save_data(self):
#         """Save data to SQLite database"""
#         try:
#             conn = sqlite3.connect(getattr(self, 'db_path', self.db_filename))
#             cursor = conn.cursor()
            
#             for category in self.budget_scenarios[self.current_scenario]:
#                 try:
#                     actual_spent = float(self.actual_spending[category].get())
#                 except (ValueError, TypeError):
#                     actual_spent = 0.0
                
#                 # Use parameterized queries to prevent SQL injection
#                 cursor.execute('''
#                     INSERT OR REPLACE INTO budget_data 
#                     (scenario, paycheck_amount, category, actual_spent, date_updated)
#                     VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
#                 ''', (self.current_scenario, self.paycheck_amount.get(), category, actual_spent))
            
#             conn.commit()
#             conn.close()
#             messagebox.showinfo("Success", "Data saved to database!")
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
#     def load_data(self):
#         """Load data from SQLite database"""
#         try:
#             conn = sqlite3.connect(getattr(self, 'db_path', self.db_filename))
#             cursor = conn.cursor()
            
#             cursor.execute('''
#                 SELECT category, actual_spent, paycheck_amount 
#                 FROM budget_data 
#                 WHERE scenario = ?
#             ''', (self.current_scenario,))
            
#             results = cursor.fetchall()
            
#             if results:
#                 # Load paycheck amount from first record
#                 try:
#                     paycheck_amount = float(results[0][2])
#                     self.paycheck_amount.set(paycheck_amount)
#                 except (ValueError, TypeError):
#                     pass
                
#                 # Load actual spending
#                 for category, actual_spent, _ in results:
#                     if category in self.actual_spending:
#                         try:
#                             self.actual_spending[category].set(float(actual_spent))
#                         except (ValueError, TypeError):
#                             self.actual_spending[category].set(0.0)
            
#             conn.close()
#             self.update_calculations()
#             self.update_charts()
#         except Exception as e:
#             print(f"Note: Could not load data - {str(e)}")
    
#     def clear_all_spending(self):
#         """Clear all actual spending entries"""
#         if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
#             for category in self.actual_spending:
#                 self.actual_spending[category].set(0.0)
#             self.update_calculations()
#             self.update_charts()
    
#     def export_csv(self):
#         """Export current budget data to CSV"""
#         filename = filedialog.asksaveasfilename(
#             defaultextension=".csv",
#             filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
#             initialname=f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         )
        
#         if filename:
#             try:
#                 import csv
#                 with open(filename, 'w', newline='') as file:
#                     writer = csv.writer(file)
#                     writer.writerow(['Scenario', 'Category', 'Percentage', 'Budgeted Amount', 
#                                    'Actual Spent', 'Difference', 'Status'])
                    
#                     paycheck = self.paycheck_amount.get()
#                     for category, data in self.budget_scenarios[self.current_scenario].items():
#                         percentage = data["percentage"]
#                         budgeted = (percentage / 100) * paycheck
#                         actual = self.actual_spending[category].get()
#                         difference = budgeted - actual
                        
#                         if actual == 0:
#                             status = "Not Set"
#                         elif difference > 0:
#                             status = "Under Budget"
#                         elif difference < 0:
#                             status = "Over Budget"
#                         else:
#                             status = "On Target"
                        
#                         writer.writerow([
#                             self.current_scenario, category, f"{percentage:.1f}%", 
#                             f"{budgeted:.2f}", f"{actual:.2f}", f"{difference:.2f}", status
#                         ])
                
#                 messagebox.showinfo("Success", f"Data exported to {filename}")
#             except Exception as e:
#                 messagebox.showerror("Error", f"Failed to export data: {str(e)}")

# def main():
#     root = tk.Tk()
#     app = BudgetApp(root)
#     root.mainloop()

# if __name__ == "__main__":
#     main()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as mplstyle
from config import ConfigManager, get_config, save_config, update_config

class BudgetApp:
    def __init__(self, root):
        self.root = root
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = get_config()
        
        # Apply configuration to window
        self.root.title("Personal Budget Manager")
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        
        # Apply Sun Valley theme from config
        try:
            import sv_ttk
            sv_ttk.set_theme(self.config.theme)
        except ImportError:
            print("Sun Valley theme not found. Using default theme.")
            print("Install with: pip install sv-ttk")
        
        # Budget scenarios data
        # Note: fixed_amount=True means the dollar amount stays constant, percentage adjusts
        # Note: fixed_amount=False means percentage stays constant, dollar amount adjusts
        self.budget_scenarios = {
            "July-December 2025": {
                "Roth IRA": {"amount": 333.33, "percentage": 8.4, "fixed_amount": False},
                "General Savings": {"amount": 769.23, "percentage": 19.3, "fixed_amount": False},
                "Vacation Fund": {"amount": 500.00, "percentage": 12.5, "fixed_amount": False},
                "HOA": {"amount": 1078.81, "percentage": 27.1, "fixed_amount": True},
                "Utilities": {"amount": 60.00, "percentage": 1.5, "fixed_amount": True},
                "Subscriptions": {"amount": 90.00, "percentage": 2.3, "fixed_amount": True},
                "Groceries": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
                "Uber/Lyft": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
                "Therapy": {"amount": 44.00, "percentage": 1.1, "fixed_amount": True},
                "Dining/Entertainment": {"amount": 150.00, "percentage": 3.8, "fixed_amount": False},
                "Flex/Buffer": {"amount": 657.38, "percentage": 16.5, "fixed_amount": False}
            },
            "Fresh New Year (Jan-May)": {
                "Roth IRA": {"amount": 1400.00, "percentage": 35.2, "fixed_amount": False},
                "General Savings": {"amount": 250.00, "percentage": 6.3, "fixed_amount": False},
                "Vacation Fund": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
                "HOA": {"amount": 1078.81, "percentage": 27.1, "fixed_amount": True},
                "Utilities": {"amount": 60.00, "percentage": 1.5, "fixed_amount": True},
                "Subscriptions": {"amount": 90.00, "percentage": 2.3, "fixed_amount": True},
                "Groceries": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
                "Uber/Lyft": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
                "Dining/Entertainment": {"amount": 150.00, "percentage": 3.8, "fixed_amount": False},
                "Therapy": {"amount": 44.00, "percentage": 1.1, "fixed_amount": True},
                "Flex/Buffer": {"amount": 90.94, "percentage": 2.3, "fixed_amount": False}
            },
            "Fresh New Year (June-Dec)": {
                "Roth IRA": {"amount": 0.00, "percentage": 0.0, "fixed_amount": False},
                "General Savings": {"amount": 833.33, "percentage": 20.9, "fixed_amount": False},
                "Vacation Fund": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
                "HOA": {"amount": 1078.81, "percentage": 27.1, "fixed_amount": True},
                "Utilities": {"amount": 60.00, "percentage": 1.5, "fixed_amount": True},
                "Subscriptions": {"amount": 90.00, "percentage": 2.3, "fixed_amount": True},
                "Groceries": {"amount": 300.00, "percentage": 7.5, "fixed_amount": False},
                "Uber/Lyft": {"amount": 50.00, "percentage": 1.3, "fixed_amount": False},
                "Dining/Entertainment": {"amount": 150.00, "percentage": 3.8, "fixed_amount": False},
                "Therapy": {"amount": 44.00, "percentage": 1.1, "fixed_amount": True},
                "Flex/Buffer": {"amount": 857.61, "percentage": 21.5, "fixed_amount": False}
            }
        }
        
        self.current_scenario = self.config.default_scenario
        self.paycheck_amount = tk.DoubleVar(value=self.config.default_paycheck)
        self.actual_spending = {}
        self.db_filename = self.config.database_filename
        
        # Initialize database
        self.init_database()
        
        # Initialize actual spending data
        for category in self.budget_scenarios[self.current_scenario]:
            self.actual_spending[category] = tk.DoubleVar(value=0.0)
        
        self.create_widgets()
        self.load_data()
        self.update_calculations()
        
    def init_database(self):
        """Initialize SQLite database"""
        try:
            # Use absolute path for better security and clarity
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.db_filename)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budget_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT NOT NULL,
                    paycheck_amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    actual_spent REAL NOT NULL DEFAULT 0.0,
                    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(scenario, category)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spending_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Store the full path for later use
            self.db_path = db_path
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            self.db_path = self.db_filename  # Fallback to relative path
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main Budget Tab
        self.budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_frame, text="Budget Overview")
        
        # Dashboard Tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        self.create_budget_tab()
        self.create_dashboard_tab()
        self.create_settings_tab()
        
    def create_budget_tab(self):
        # Top frame for controls
        top_frame = ttk.Frame(self.budget_frame)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Scenario selection
        ttk.Label(top_frame, text="Budget Scenario:").pack(side="left", padx=5)
        self.scenario_var = tk.StringVar(value=self.current_scenario)
        scenario_combo = ttk.Combobox(top_frame, textvariable=self.scenario_var, 
                                    values=list(self.budget_scenarios.keys()), 
                                    state="readonly", width=25)
        scenario_combo.pack(side="left", padx=5)
        scenario_combo.bind("<<ComboboxSelected>>", self.change_scenario)
        
        # Paycheck amount
        ttk.Label(top_frame, text="Paycheck Amount: $").pack(side="left", padx=(20, 5))
        paycheck_entry = ttk.Entry(top_frame, textvariable=self.paycheck_amount, width=12)
        paycheck_entry.pack(side="left", padx=5)
        paycheck_entry.bind("<KeyRelease>", lambda e: self.update_calculations())
        
        # Buttons
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side="right", padx=10)
        
        ttk.Button(button_frame, text="Save Data", command=self.save_data).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Clear All Spending", command=self.clear_all_spending).pack(side="left", padx=2)
        
        # Auto-save indicator
        if self.config.auto_save:
            ttk.Label(button_frame, text="Auto-save: ON", foreground="green").pack(side="left", padx=10)
        
        # Main content frame with grid
        content_frame = ttk.Frame(self.budget_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create frame for the editable grid
        grid_frame = ttk.Frame(content_frame)
        grid_frame.pack(fill="both", expand=True)
        
        # Headers
        headers = ["Category", "% of Income", "Budgeted ($)", "Actual Spent ($)", "Difference ($)", "Status"]
        for i, header in enumerate(headers):
            label = ttk.Label(grid_frame, text=header, font=("", 10, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        for i in range(len(headers)):
            grid_frame.columnconfigure(i, weight=1)
        
        # Store entry widgets for actual spending
        self.spending_entries = {}
        self.category_labels = {}
        
        # Create rows for each category
        self.create_budget_rows(grid_frame)
        
        # Summary frame
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
    
    def create_budget_rows(self, parent):
        """Create editable budget rows"""
        row = 1
        for category in self.budget_scenarios[self.current_scenario]:
            # Category name
            cat_label = ttk.Label(parent, text=category)
            cat_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            self.category_labels[category] = cat_label
            
            # Percentage
            perc_label = ttk.Label(parent, text="")
            perc_label.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category}_perc"] = perc_label
            
            # Budgeted amount
            budget_label = ttk.Label(parent, text="")
            budget_label.grid(row=row, column=2, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category}_budget"] = budget_label
            
            # Actual spent (editable entry)
            actual_var = tk.DoubleVar(value=0.0)
            self.actual_spending[category] = actual_var
            actual_entry = ttk.Entry(parent, textvariable=actual_var, width=12)
            actual_entry.grid(row=row, column=3, padx=5, pady=2, sticky="ew")
            actual_entry.bind("<KeyRelease>", lambda e, cat=category: self.on_spending_change(cat))
            self.spending_entries[category] = actual_entry
            
            # Difference
            diff_label = ttk.Label(parent, text="")
            diff_label.grid(row=row, column=4, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category}_diff"] = diff_label
            
            # Status
            status_label = ttk.Label(parent, text="")
            status_label.grid(row=row, column=5, padx=5, pady=2, sticky="ew")
            self.category_labels[f"{category}_status"] = status_label
            
            row += 1
    
    def on_spending_change(self, category):
        """Handle changes to spending entries"""
        self.root.after(100, self.update_calculations)  # Small delay for smooth typing
        
        # Auto-save if enabled
        if self.config.auto_save:
            self.root.after(1000, self.auto_save_data)  # Auto-save after 1 second of no typing
    
    def auto_save_data(self):
        """Auto-save data without showing message."""
        try:
            conn = sqlite3.connect(getattr(self, 'db_path', self.db_filename))
            cursor = conn.cursor()
            
            for category in self.budget_scenarios[self.current_scenario]:
                try:
                    actual_spent = float(self.actual_spending[category].get())
                except (ValueError, TypeError):
                    actual_spent = 0.0
                
                cursor.execute('''
                    INSERT OR REPLACE INTO budget_data 
                    (scenario, paycheck_amount, category, actual_spent, date_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (self.current_scenario, self.paycheck_amount.get(), category, actual_spent))
            
            conn.commit()
            conn.close()
            # Silent save - no popup message for auto-save
        except Exception as e:
            print(f"Auto-save failed: {str(e)}")
    
    def create_dashboard_tab(self):
        # Set matplotlib to use style from config
        plt.style.use(self.config.chart_style)
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 7))
        self.fig.patch.set_facecolor('#1c1c1c' if self.config.theme == 'dark' else '#ffffff')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.dashboard_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(self.dashboard_frame, text="Refresh Charts", 
                  command=self.update_charts).pack(pady=5)
    
    def create_settings_tab(self):
        """Create settings configuration tab."""
        # Main settings frame
        main_frame = ttk.Frame(self.settings_frame, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Theme settings
        theme_frame = ttk.LabelFrame(main_frame, text="Appearance", padding=10)
        theme_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(theme_frame, text="Theme:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                  values=["light", "dark"], state="readonly", width=10)
        theme_combo.grid(row=0, column=1, sticky="w")
        theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        # Behavior settings
        behavior_frame = ttk.LabelFrame(main_frame, text="Behavior", padding=10)
        behavior_frame.pack(fill="x", pady=(0, 10))
        
        self.auto_save_var = tk.BooleanVar(value=self.config.auto_save)
        ttk.Checkbutton(behavior_frame, text="Auto-save changes", 
                       variable=self.auto_save_var, 
                       command=self.on_auto_save_change).pack(anchor="w")
        
        self.auto_backup_var = tk.BooleanVar(value=self.config.auto_backup)
        ttk.Checkbutton(behavior_frame, text="Auto-backup database", 
                       variable=self.auto_backup_var,
                       command=self.on_auto_backup_change).pack(anchor="w")
        
        # Display settings
        display_frame = ttk.LabelFrame(main_frame, text="Display", padding=10)
        display_frame.pack(fill="x", pady=(0, 10))
        
        self.show_percentages_var = tk.BooleanVar(value=self.config.show_percentages)
        ttk.Checkbutton(display_frame, text="Show percentages", 
                       variable=self.show_percentages_var,
                       command=self.on_display_change).pack(anchor="w")
        
        self.show_fixed_var = tk.BooleanVar(value=self.config.show_fixed_indicators)
        ttk.Checkbutton(display_frame, text="Show fixed amount indicators", 
                       variable=self.show_fixed_var,
                       command=self.on_display_change).pack(anchor="w")
        
        # Currency settings
        currency_frame = ttk.Frame(display_frame)
        currency_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(currency_frame, text="Currency symbol:").pack(side="left")
        self.currency_var = tk.StringVar(value=self.config.currency_symbol)
        currency_entry = ttk.Entry(currency_frame, textvariable=self.currency_var, width=5)
        currency_entry.pack(side="left", padx=(5, 10))
        currency_entry.bind("<KeyRelease>", self.on_currency_change)
        
        ttk.Label(currency_frame, text="Decimal places:").pack(side="left")
        self.decimal_var = tk.IntVar(value=self.config.decimal_places)
        decimal_spin = ttk.Spinbox(currency_frame, from_=0, to=4, 
                                  textvariable=self.decimal_var, width=5,
                                  command=self.on_decimal_change)
        decimal_spin.pack(side="left", padx=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="Save Settings", 
                  command=self.save_settings).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.reset_settings).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Apply Preset", 
                  command=self.show_preset_dialog).pack(side="left")
    
    def on_theme_change(self, event=None):
        """Handle theme change."""
        new_theme = self.theme_var.get()
        update_config(theme=new_theme)
        messagebox.showinfo("Theme Changed", 
                           f"Theme changed to {new_theme}. Restart the application to see changes.")
    
    def on_auto_save_change(self):
        """Handle auto-save setting change."""
        update_config(auto_save=self.auto_save_var.get())
        # Refresh the budget tab to show/hide auto-save indicator
        self.refresh_budget_tab()
    
    def on_auto_backup_change(self):
        """Handle auto-backup setting change."""
        update_config(auto_backup=self.auto_backup_var.get())
    
    def on_display_change(self):
        """Handle display setting changes."""
        update_config(
            show_percentages=self.show_percentages_var.get(),
            show_fixed_indicators=self.show_fixed_var.get()
        )
        self.update_calculations()
    
    def on_currency_change(self, event=None):
        """Handle currency symbol change."""
        update_config(currency_symbol=self.currency_var.get())
        self.update_calculations()
    
    def on_decimal_change(self):
        """Handle decimal places change."""
        update_config(decimal_places=self.decimal_var.get())
        self.update_calculations()
    
    def save_settings(self):
        """Save all settings to config file."""
        if save_config():
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save settings.")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.config_manager.reset_to_defaults()
            self.refresh_settings_tab()
            messagebox.showinfo("Settings Reset", "Settings have been reset to defaults.")
    
    def show_preset_dialog(self):
        """Show preset selection dialog."""
        from config import PRESET_CONFIGS, apply_preset
        
        preset_window = tk.Toplevel(self.root)
        preset_window.title("Apply Preset")
        preset_window.geometry("300x200")
        preset_window.transient(self.root)
        preset_window.grab_set()
        
        ttk.Label(preset_window, text="Choose a preset configuration:").pack(pady=10)
        
        preset_var = tk.StringVar()
        for preset_name in PRESET_CONFIGS.keys():
            ttk.Radiobutton(preset_window, text=preset_name.title(), 
                           variable=preset_var, value=preset_name).pack(anchor="w", padx=20)
        
        button_frame = ttk.Frame(preset_window)
        button_frame.pack(pady=20)
        
        def apply_selected_preset():
            if preset_var.get():
                apply_preset(preset_var.get())
                self.refresh_settings_tab()
                preset_window.destroy()
                messagebox.showinfo("Preset Applied", f"'{preset_var.get()}' preset has been applied!")
        
        ttk.Button(button_frame, text="Apply", command=apply_selected_preset).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=preset_window.destroy).pack(side="left", padx=5)
    
    def refresh_settings_tab(self):
        """Refresh settings tab with current config values."""
        self.config = get_config()  # Reload config
        self.theme_var.set(self.config.theme)
        self.auto_save_var.set(self.config.auto_save)
        self.auto_backup_var.set(self.config.auto_backup)
        self.show_percentages_var.set(self.config.show_percentages)
        self.show_fixed_var.set(self.config.show_fixed_indicators)
        self.currency_var.set(self.config.currency_symbol)
        self.decimal_var.set(self.config.decimal_places)
    
    def refresh_budget_tab(self):
        """Refresh budget tab to reflect config changes."""
        # This would recreate the budget tab - simplified for now
        self.update_calculations()
    
    def change_scenario(self, event=None):
        self.current_scenario = self.scenario_var.get()
        
        # Save current data before switching
        self.save_data()
        
        # Update actual spending variables for new scenario
        old_spending = {}
        for category, var in self.actual_spending.items():
            old_spending[category] = var.get()
        
        self.actual_spending = {}
        
        # Recreate the budget rows for new scenario
        for widget in self.category_labels.values():
            widget.destroy()
        for widget in self.spending_entries.values():
            widget.destroy()
            
        self.category_labels = {}
        self.spending_entries = {}
        
        # Find the grid frame and recreate rows
        content_frame = self.budget_frame.winfo_children()[1]  # Second child is content_frame
        grid_frame = content_frame.winfo_children()[0]  # First child is grid_frame
        
        self.create_budget_rows(grid_frame)
        self.load_data()
        self.update_calculations()
        self.update_charts()
    
    def update_calculations(self):
        paycheck = self.paycheck_amount.get()
        total_budgeted = 0
        total_spent = 0
        
        # Update each row
        for category, data in self.budget_scenarios[self.current_scenario].items():
            if data["fixed_amount"]:
                # Fixed amount: dollar amount stays same, percentage adjusts
                budgeted = data["amount"]
                percentage = (budgeted / paycheck * 100) if paycheck > 0 else 0
            else:
                # Percentage-based: percentage stays same, dollar amount adjusts
                percentage = data["percentage"]
                budgeted = (percentage / 100) * paycheck
            
            try:
                actual = self.actual_spending[category].get()
            except:
                actual = 0.0
                
            difference = budgeted - actual
            
            total_budgeted += budgeted
            total_spent += actual
            
            # Determine status and color
            if actual == 0:
                status = "Not Set"
                color = "gray"
            elif difference > 0:
                status = "Under Budget"
                color = "green"
            elif difference < 0:
                status = "Over Budget"
                color = "red"
            else:
                status = "On Target"
                color = "blue"
            
            # Update labels with indicator for fixed amounts
            if self.config.show_fixed_indicators and data["fixed_amount"]:
                category_display = f"{category} (Fixed)"
            else:
                category_display = category
                
            self.category_labels[category].config(text=category_display)
            
            if self.config.show_percentages:
                self.category_labels[f"{category}_perc"].config(text=f"{percentage:.1f}%")
            else:
                self.category_labels[f"{category}_perc"].config(text="")
            
            # Format currency with config settings
            currency = self.config.currency_symbol
            decimal_places = self.config.decimal_places
            
            self.category_labels[f"{category}_budget"].config(
                text=f"{currency}{budgeted:.{decimal_places}f}")
            self.category_labels[f"{category}_diff"].config(
                text=f"{currency}{difference:.{decimal_places}f}")
            self.category_labels[f"{category}_status"].config(text=status, foreground=color)
        
        # Update summary with config formatting
        remaining = paycheck - total_spent
        over_under = total_spent - total_budgeted
        
        currency = self.config.currency_symbol
        decimal_places = self.config.decimal_places
        
        self.summary_labels["Total Budgeted:"].config(
            text=f"{currency}{total_budgeted:.{decimal_places}f}")
        self.summary_labels["Total Spent:"].config(
            text=f"{currency}{total_spent:.{decimal_places}f}")
        self.summary_labels["Remaining:"].config(
            text=f"{currency}{remaining:.{decimal_places}f}")
        
        if over_under > 0:
            self.summary_labels["Over/Under:"].config(
                text=f"{currency}{over_under:.{decimal_places}f} OVER", foreground="red")
        elif over_under < 0:
            self.summary_labels["Over/Under:"].config(
                text=f"{currency}{abs(over_under):.{decimal_places}f} UNDER", foreground="green")
        else:
            self.summary_labels["Over/Under:"].config(
                text=f"{currency}0.00 ON TARGET", foreground="blue")
    
    def update_charts(self):
        self.ax1.clear()
        self.ax2.clear()
        
        paycheck = self.paycheck_amount.get()
        categories = []
        budgeted_amounts = []
        actual_amounts = []
        
        for category, data in self.budget_scenarios[self.current_scenario].items():
            categories.append(category.replace(' ', '\n'))  # Line breaks for better display
            
            if data["fixed_amount"]:
                # Fixed amount: dollar amount stays same
                budgeted_amounts.append(data["amount"])
            else:
                # Percentage-based: calculate from percentage
                budgeted_amounts.append((data["percentage"] / 100) * paycheck)
            
            try:
                actual_amounts.append(self.actual_spending[category].get())
            except:
                actual_amounts.append(0.0)
        
        # Pie chart of budgeted amounts
        colors = plt.cm.Set3(range(len(categories)))
        self.ax1.pie(budgeted_amounts, labels=categories, autopct='%1.1f%%', 
                    startangle=90, colors=colors)
        self.ax1.set_title("Budget Allocation", fontsize=14, fontweight='bold')
        
        # Bar chart comparison
        x_pos = range(len(categories))
        width = 0.35
        
        bars1 = self.ax2.bar([x - width/2 for x in x_pos], budgeted_amounts, width, 
                    label='Budgeted', alpha=0.8, color=self.config.chart_colors["budgeted"])
        bars2 = self.ax2.bar([x + width/2 for x in x_pos], actual_amounts, width, 
                    label='Actual', alpha=0.8, color=self.config.chart_colors["actual"])
        
        self.ax2.set_xlabel('Categories', fontweight='bold')
        self.ax2.set_ylabel('Amount ($)', fontweight='bold')
        self.ax2.set_title('Budgeted vs Actual Spending', fontsize=14, fontweight='bold')
        self.ax2.set_xticks(x_pos)
        self.ax2.set_xticklabels(categories, rotation=45, ha='right')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            self.ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                         f'${height:.0f}', ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                self.ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                             f'${height:.0f}', ha='center', va='bottom', fontsize=8)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def save_data(self):
        """Save data to SQLite database"""
        try:
            conn = sqlite3.connect(getattr(self, 'db_path', self.db_filename))
            cursor = conn.cursor()
            
            for category in self.budget_scenarios[self.current_scenario]:
                try:
                    actual_spent = float(self.actual_spending[category].get())
                except (ValueError, TypeError):
                    actual_spent = 0.0
                
                # Use parameterized queries to prevent SQL injection
                cursor.execute('''
                    INSERT OR REPLACE INTO budget_data 
                    (scenario, paycheck_amount, category, actual_spent, date_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (self.current_scenario, self.paycheck_amount.get(), category, actual_spent))
            
            conn.commit()
            conn.close()
            
            # Show success message only for manual saves
            messagebox.showinfo("Success", "Data saved to database!")
            
            # Create backup if enabled
            if self.config.auto_backup:
                self.create_backup()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def create_backup(self):
        """Create a backup of the database."""
        try:
            import shutil
            from pathlib import Path
            
            # Create backup directory
            backup_dir = Path(self.config.backup_directory)
            backup_dir.mkdir(exist_ok=True)
            
            # Create timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"budget_backup_{timestamp}.db"
            backup_path = backup_dir / backup_filename
            
            # Copy database file
            shutil.copy2(self.db_filename, backup_path)
            print(f"Backup created: {backup_path}")
            
        except Exception as e:
            print(f"Backup failed: {str(e)}")
    
    def load_data(self):
        """Load data from SQLite database"""
        try:
            conn = sqlite3.connect(getattr(self, 'db_path', self.db_filename))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, actual_spent, paycheck_amount 
                FROM budget_data 
                WHERE scenario = ?
            ''', (self.current_scenario,))
            
            results = cursor.fetchall()
            
            if results:
                # Load paycheck amount from first record
                try:
                    paycheck_amount = float(results[0][2])
                    self.paycheck_amount.set(paycheck_amount)
                except (ValueError, TypeError):
                    pass
                
                # Load actual spending
                for category, actual_spent, _ in results:
                    if category in self.actual_spending:
                        try:
                            self.actual_spending[category].set(float(actual_spent))
                        except (ValueError, TypeError):
                            self.actual_spending[category].set(0.0)
            
            conn.close()
            self.update_calculations()
            self.update_charts()
        except Exception as e:
            print(f"Note: Could not load data - {str(e)}")
    
    def clear_all_spending(self):
        """Clear all actual spending entries"""
        if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
            for category in self.actual_spending:
                self.actual_spending[category].set(0.0)
            self.update_calculations()
            self.update_charts()
    
    def export_csv(self):
        """Export current budget data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                import csv
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Scenario', 'Category', 'Percentage', 'Budgeted Amount', 
                                   'Actual Spent', 'Difference', 'Status'])
                    
                    paycheck = self.paycheck_amount.get()
                    for category, data in self.budget_scenarios[self.current_scenario].items():
                        percentage = data["percentage"]
                        budgeted = (percentage / 100) * paycheck
                        actual = self.actual_spending[category].get()
                        difference = budgeted - actual
                        
                        if actual == 0:
                            status = "Not Set"
                        elif difference > 0:
                            status = "Under Budget"
                        elif difference < 0:
                            status = "Over Budget"
                        else:
                            status = "On Target"
                        
                        writer.writerow([
                            self.current_scenario, category, f"{percentage:.1f}%", 
                            f"{budgeted:.2f}", f"{actual:.2f}", f"{difference:.2f}", status
                        ])
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")

def main():
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()