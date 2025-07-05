# budget_history_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from budget_time_tracker import TimeTracker, PeriodType, BudgetSnapshot, SpendingAnalyzer
from budget_models import ViewMode

class BudgetHistoryTab:
    """Handles the historical budget tracking and analysis tab"""
    
    def __init__(self, parent_frame, config, get_current_data_callback, database):
        self.parent_frame = parent_frame
        self.config = config
        self.get_current_data_callback = get_current_data_callback  # Function to get current budget data
        self.database = database  # BudgetDatabase instance
        
        # Initialize time tracking components
        self.time_tracker = TimeTracker(database)  # Pass database for persistence
        self.analyzer = SpendingAnalyzer(self.time_tracker)
        
        # Current selections
        self.current_period_type = PeriodType.MONTHLY
        self.selected_period = None
        
        self.setup_history_tab()
    
    def setup_history_tab(self):
        """Setup the history tracking interface"""
        # Create main container with notebook for sub-tabs
        self.history_notebook = ttk.Notebook(self.parent_frame)
        self.history_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Period Selection & Saving Tab
        self.period_frame = ttk.Frame(self.history_notebook)
        self.history_notebook.add(self.period_frame, text="Time Periods")
        self.create_period_tab()
        
        # Historical View Tab
        self.history_frame = ttk.Frame(self.history_notebook)
        self.history_notebook.add(self.history_frame, text="Historical Data")
        self.create_history_view_tab()
        
        # Analytics Tab
        self.analytics_frame = ttk.Frame(self.history_notebook)
        self.history_notebook.add(self.analytics_frame, text="Spending Analytics")
        self.create_analytics_tab()
    
    def create_period_tab(self):
        """Create the period selection and saving interface"""
        # Period Type Selection
        type_frame = ttk.LabelFrame(self.period_frame, text="Select Period Type", padding=10)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        self.period_type_var = tk.StringVar(value=self.current_period_type.value)
        for period_type in PeriodType:
            ttk.Radiobutton(
                type_frame, 
                text=period_type.value, 
                variable=self.period_type_var,
                value=period_type.value,
                command=self.on_period_type_change
            ).pack(side="left", padx=10)
        
        # Period Selection
        selection_frame = ttk.LabelFrame(self.period_frame, text="Select Specific Period", padding=10)
        selection_frame.pack(fill="x", padx=10, pady=5)
        
        # Period dropdown
        ttk.Label(selection_frame, text="Choose Period:").pack(side="left", padx=5)
        self.period_var = tk.StringVar()
        self.period_combo = ttk.Combobox(selection_frame, textvariable=self.period_var, 
                                        state="readonly", width=30)
        self.period_combo.pack(side="left", padx=5)
        self.period_combo.bind("<<ComboboxSelected>>", self.on_period_selected)
        
        # Custom date range (for custom periods)
        self.custom_frame = ttk.Frame(selection_frame)
        
        ttk.Label(self.custom_frame, text="From:").pack(side="left", padx=5)
        self.start_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        start_entry = ttk.Entry(self.custom_frame, textvariable=self.start_date_var, width=12)
        start_entry.pack(side="left", padx=2)
        
        ttk.Label(self.custom_frame, text="To:").pack(side="left", padx=5)
        self.end_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        end_entry = ttk.Entry(self.custom_frame, textvariable=self.end_date_var, width=12)
        end_entry.pack(side="left", padx=2)
        
        ttk.Button(self.custom_frame, text="Create Custom Period", 
                  command=self.create_custom_period).pack(side="left", padx=5)
        
        # Current Period Info
        info_frame = ttk.LabelFrame(self.period_frame, text="Current Period Information", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.period_info_label = ttk.Label(info_frame, text="No period selected", font=("", 10))
        self.period_info_label.pack(anchor="w")
        
        # Action Buttons
        action_frame = ttk.Frame(self.period_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(action_frame, text="Save Current Budget to Period", 
                  command=self.save_current_budget, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="Load Period Data", 
                  command=self.load_period_data).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Delete Period", 
                  command=self.delete_period).pack(side="left", padx=5)
        
        # Notes section
        notes_frame = ttk.LabelFrame(self.period_frame, text="Period Notes", padding=10)
        notes_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD)
        notes_scrollbar = ttk.Scrollbar(notes_frame, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)
        
        self.notes_text.pack(side="left", fill="both", expand=True)
        notes_scrollbar.pack(side="right", fill="y")
        
        # Initialize with current period
        self.update_period_list()
        self.select_current_period()
    
    def create_history_view_tab(self):
        """Create the historical data viewing interface"""
        # Controls
        controls_frame = ttk.Frame(self.history_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(controls_frame, text="View Historical Period:").pack(side="left", padx=5)
        self.history_period_var = tk.StringVar()
        self.history_combo = ttk.Combobox(controls_frame, textvariable=self.history_period_var,
                                         state="readonly", width=30)
        self.history_combo.pack(side="left", padx=5)
        self.history_combo.bind("<<ComboboxSelected>>", self.on_history_period_selected)
        
        ttk.Button(controls_frame, text="Refresh", 
                  command=self.refresh_history_list).pack(side="left", padx=10)
        
        # Historical data display
        self.create_history_table()
        
        # Comparison section
        compare_frame = ttk.LabelFrame(self.history_frame, text="Compare Periods", padding=10)
        compare_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(compare_frame, text="Period 1:").grid(row=0, column=0, padx=5, sticky="w")
        self.compare1_var = tk.StringVar()
        compare1_combo = ttk.Combobox(compare_frame, textvariable=self.compare1_var,
                                     state="readonly", width=25)
        compare1_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(compare_frame, text="Period 2:").grid(row=0, column=2, padx=5, sticky="w")
        self.compare2_var = tk.StringVar()
        compare2_combo = ttk.Combobox(compare_frame, textvariable=self.compare2_var,
                                     state="readonly", width=25)
        compare2_combo.grid(row=0, column=3, padx=5)
        
        ttk.Button(compare_frame, text="Compare", 
                  command=self.compare_periods).grid(row=0, column=4, padx=10)
        
        # Update comparison dropdowns
        self.compare1_combo = compare1_combo
        self.compare2_combo = compare2_combo
        
        self.refresh_history_list()
    
    def create_history_table(self):
        """Create table for displaying historical budget data"""
        table_frame = ttk.Frame(self.history_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview for historical data
        columns = ("Category", "Budgeted", "Actual", "Difference", "Status")
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def create_analytics_tab(self):
        """Create the spending analytics and trends interface"""
        # Analytics controls
        controls_frame = ttk.Frame(self.analytics_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Analyze last").pack(side="left", padx=5)
        self.periods_to_analyze_var = tk.IntVar(value=6)
        periods_spin = ttk.Spinbox(controls_frame, from_=2, to=24, width=5,
                                  textvariable=self.periods_to_analyze_var)
        periods_spin.pack(side="left", padx=2)
        ttk.Label(controls_frame, text="periods").pack(side="left", padx=2)
        
        ttk.Button(controls_frame, text="Generate Analytics", 
                  command=self.generate_analytics).pack(side="left", padx=10)
        
        # Analytics display area
        self.analytics_notebook = ttk.Notebook(self.analytics_frame)
        self.analytics_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Trends tab
        self.trends_frame = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(self.trends_frame, text="Spending Trends")
        self.create_trends_chart()
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(self.summary_frame, text="Summary Report")
        self.create_summary_display()
    
    def create_trends_chart(self):
        """Create matplotlib chart for spending trends"""
        # Create matplotlib figure
        self.trends_fig, self.trends_ax = plt.subplots(figsize=(12, 6))
        self.trends_fig.patch.set_facecolor('#1c1c1c' if self.config.theme == 'dark' else '#ffffff')
        
        # Create canvas
        self.trends_canvas = FigureCanvasTkAgg(self.trends_fig, self.trends_frame)
        self.trends_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initial empty chart
        self.trends_ax.text(0.5, 0.5, 'Generate analytics to see spending trends', 
                           ha='center', va='center', transform=self.trends_ax.transAxes, fontsize=12)
        self.trends_canvas.draw()
    
    def create_summary_display(self):
        """Create text display for analytics summary"""
        # Create text widget with scrollbar
        text_frame = ttk.Frame(self.summary_frame)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.summary_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        summary_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)
        
        self.summary_text.pack(side="left", fill="both", expand=True)
        summary_scrollbar.pack(side="right", fill="y")
    
    # Event Handlers
    def on_period_type_change(self):
        """Handle period type selection change"""
        type_str = self.period_type_var.get()
        self.current_period_type = PeriodType(type_str)
        
        # Show/hide custom date controls
        if self.current_period_type == PeriodType.CUSTOM:
            self.custom_frame.pack(side="left", padx=10)
            self.period_combo.pack_forget()
        else:
            self.custom_frame.pack_forget()
            self.period_combo.pack(side="left", padx=5)
            self.update_period_list()
            self.select_current_period()
    
    def on_period_selected(self, event=None):
        """Handle period selection from dropdown"""
        if self.period_combo.current() >= 0:
            periods = self.get_periods_for_type()
            self.selected_period = periods[self.period_combo.current()]
            self.update_period_info()
    
    def on_history_period_selected(self, event=None):
        """Handle historical period selection"""
        if self.history_combo.current() >= 0:
            available_periods = self.time_tracker.get_available_periods()
            if available_periods:
                selected_period = available_periods[self.history_combo.current()]
                self.display_historical_data(selected_period.period_id)
    
    def update_period_list(self):
        """Update the period dropdown list"""
        periods = self.get_periods_for_type()
        period_names = [period.display_name for period in periods]
        self.period_combo['values'] = period_names
    
    def get_periods_for_type(self):
        """Get periods based on current period type"""
        if self.current_period_type == PeriodType.MONTHLY:
            return self.time_tracker.generate_monthly_periods(datetime.now().year, 24)
        elif self.current_period_type == PeriodType.BIWEEKLY:
            return self.time_tracker.generate_biweekly_periods(num_periods=26)
        elif self.current_period_type == PeriodType.WEEKLY:
            return self.time_tracker.generate_weekly_periods(num_weeks=52)
        else:  # CUSTOM
            return []
    
    def select_current_period(self):
        """Select the period that contains today's date"""
        if self.current_period_type != PeriodType.CUSTOM:
            current_period = self.time_tracker.get_current_period(self.current_period_type)
            periods = self.get_periods_for_type()
            
            for i, period in enumerate(periods):
                if period.period_id == current_period.period_id:
                    self.period_combo.current(i)
                    self.selected_period = period
                    self.update_period_info()
                    break
    
    def update_period_info(self):
        """Update the period information display"""
        if self.selected_period:
            info_text = (f"Period: {self.selected_period.display_name}\n"
                        f"Dates: {self.selected_period.start_date} to {self.selected_period.end_date}\n"
                        f"Duration: {self.selected_period.days_in_period()} days\n"
                        f"Type: {self.selected_period.period_type.value}")
            
            # Check if snapshot exists
            snapshot = self.time_tracker.get_snapshot(self.selected_period.period_id)
            if snapshot:
                info_text += f"\nSaved: {snapshot.saved_date.strftime('%Y-%m-%d %H:%M')}"
                self.notes_text.delete(1.0, tk.END)
                self.notes_text.insert(1.0, snapshot.notes)
            else:
                info_text += "\nStatus: Not saved"
                self.notes_text.delete(1.0, tk.END)
            
            self.period_info_label.config(text=info_text)
    
    def create_custom_period(self):
        """Create a custom date range period"""
        try:
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date()
            
            if start_date > end_date:
                messagebox.showerror("Error", "Start date must be before end date")
                return
            
            custom_period = self.time_tracker.create_custom_period(start_date, end_date)
            self.selected_period = custom_period
            self.update_period_info()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
    
    def save_current_budget(self):
        """Save current budget data to the selected period"""
        if not self.selected_period:
            messagebox.showerror("Error", "Please select a period first")
            return
        
        try:
            # Get current budget data from main app
            current_data = self.get_current_data_callback()
            
            if not current_data:
                messagebox.showerror("Error", "No current budget data available")
                return
            
            # Create category data dictionary
            category_data = {}
            for category_name, result in current_data['category_results'].items():
                category_data[category_name] = {
                    'budgeted': result.budgeted,
                    'actual': result.actual,
                    'notes': ''
                }
            
            # Get notes from text widget
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            # Create snapshot
            snapshot = BudgetSnapshot(
                period=self.selected_period,
                scenario_name=current_data['scenario_name'],
                income=current_data['income'],
                view_mode=current_data['view_mode'].value,
                category_data=category_data,
                total_budgeted=current_data['summary'].total_budgeted,
                total_spent=current_data['summary'].total_spent,
                saved_date=datetime.now(),
                notes=notes
            )
            
            # Save snapshot
            self.time_tracker.save_snapshot(snapshot)
            
            # Update display
            self.update_period_info()
            self.refresh_history_list()
            
            messagebox.showinfo("Success", f"Budget data saved for {self.selected_period.display_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save budget data: {str(e)}")
    
    def load_period_data(self):
        """Load data from selected period"""
        if not self.selected_period:
            messagebox.showerror("Error", "Please select a period first")
            return
        
        snapshot = self.time_tracker.get_snapshot(self.selected_period.period_id)
        if not snapshot:
            messagebox.showerror("Error", "No saved data for this period")
            return
        
        # Show data in a popup window
        self.show_period_data_popup(snapshot)
    
    def show_period_data_popup(self, snapshot):
        """Show period data in a popup window"""
        popup = tk.Toplevel(self.parent_frame)
        popup.title(f"Budget Data - {snapshot.period.display_name}")
        popup.geometry("600x500")
        popup.transient(self.parent_frame.winfo_toplevel())
        popup.grab_set()
        
        # Create treeview for data
        columns = ("Category", "Budgeted", "Actual", "Difference")
        tree = ttk.Treeview(popup, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Populate data
        for category, data in snapshot.category_data.items():
            budgeted = data['budgeted']
            actual = data['actual']
            difference = budgeted - actual
            
            tree.insert("", "end", values=(
                category,
                f"${budgeted:.2f}",
                f"${actual:.2f}",
                f"${difference:.2f}"
            ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Summary info
        info_frame = ttk.Frame(popup)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Total Budgeted: ${snapshot.total_budgeted:.2f}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Total Spent: ${snapshot.total_spent:.2f}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Remaining: ${snapshot.total_budgeted - snapshot.total_spent:.2f}").pack(anchor="w")
        
        # Notes
        if snapshot.notes:
            notes_frame = ttk.LabelFrame(popup, text="Notes")
            notes_frame.pack(fill="x", padx=10, pady=5)
            ttk.Label(notes_frame, text=snapshot.notes, wraplength=500).pack(padx=5, pady=5)
        
        # Close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
    
    def delete_period(self):
        """Delete the selected period's data"""
        if not self.selected_period:
            messagebox.showerror("Error", "Please select a period first")
            return
        
        snapshot = self.time_tracker.get_snapshot(self.selected_period.period_id)
        if not snapshot:
            messagebox.showerror("Error", "No saved data for this period")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the budget data for {self.selected_period.display_name}?"):
            self.time_tracker.delete_snapshot(self.selected_period.period_id)
            self.update_period_info()
            self.refresh_history_list()
            messagebox.showinfo("Success", "Period data deleted")
    
    def refresh_history_list(self):
        """Refresh the historical periods dropdown"""
        available_periods = self.time_tracker.get_available_periods()
        period_names = [period.display_name for period in available_periods]
        
        self.history_combo['values'] = period_names
        self.compare1_combo['values'] = period_names
        self.compare2_combo['values'] = period_names
    
    def display_historical_data(self, period_id):
        """Display historical data for a specific period"""
        snapshot = self.time_tracker.get_snapshot(period_id)
        if not snapshot:
            return
        
        # Clear existing data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Populate historical data
        for category, data in snapshot.category_data.items():
            budgeted = data['budgeted']
            actual = data['actual']
            difference = budgeted - actual
            
            # Determine status
            if actual == 0:
                status = "Not Set"
            elif difference > 0:
                status = "Under Budget"
            elif difference < 0:
                status = "Over Budget"
            else:
                status = "On Target"
            
            self.history_tree.insert("", "end", values=(
                category,
                f"${budgeted:.2f}",
                f"${actual:.2f}",
                f"${difference:.2f}",
                status
            ))
    
    def compare_periods(self):
        """Compare two selected periods"""
        period1_name = self.compare1_var.get()
        period2_name = self.compare2_var.get()
        
        if not period1_name or not period2_name:
            messagebox.showerror("Error", "Please select both periods to compare")
            return
        
        if period1_name == period2_name:
            messagebox.showerror("Error", "Please select different periods to compare")
            return
        
        # Find period IDs
        available_periods = self.time_tracker.get_available_periods()
        period1_id = None
        period2_id = None
        
        for period in available_periods:
            if period.display_name == period1_name:
                period1_id = period.period_id
            if period.display_name == period2_name:
                period2_id = period.period_id
        
        if not period1_id or not period2_id:
            messagebox.showerror("Error", "Could not find selected periods")
            return
        
        # Generate comparison
        comparison = self.analyzer.compare_periods(period1_id, period2_id)
        
        if "error" in comparison:
            messagebox.showerror("Error", comparison["error"])
            return
        
        # Show comparison in popup
        self.show_comparison_popup(comparison)
    
    def show_comparison_popup(self, comparison):
        """Show period comparison in a popup window"""
        popup = tk.Toplevel(self.parent_frame)
        popup.title(f"Period Comparison")
        popup.geometry("700x500")
        popup.transient(self.parent_frame.winfo_toplevel())
        popup.grab_set()
        
        # Summary info
        summary_frame = ttk.LabelFrame(popup, text="Comparison Summary")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(summary_frame, text=f"Comparing: {comparison['period1']} vs {comparison['period2']}").pack(anchor="w")
        ttk.Label(summary_frame, text=f"Total Change: ${comparison['total_change']:.2f} ({comparison['total_percent_change']:.1f}%)").pack(anchor="w")
        
        # Category comparison table
        columns = ("Category", comparison['period1'], comparison['period2'], "Change", "% Change")
        tree = ttk.Treeview(popup, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Populate comparison data
        for category, data in comparison['categories'].items():
            period1_key = f"{comparison['period1']}_actual"
            period2_key = f"{comparison['period2']}_actual"
            
            tree.insert("", "end", values=(
                category,
                f"${data[period1_key]:.2f}",
                f"${data[period2_key]:.2f}",
                f"${data['change']:.2f}",
                f"{data['percent_change']:.1f}%"
            ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
    
    def generate_analytics(self):
        """Generate spending analytics and trends"""
        num_periods = self.periods_to_analyze_var.get()
        
        # Generate summary
        summary = self.analyzer.get_spending_summary(num_periods)
        
        if "error" in summary:
            messagebox.showerror("Error", summary["error"])
            return
        
        # Update summary text
        self.update_summary_display_text(summary)
        
        # Update trends chart
        self.update_trends_chart(num_periods)
    
    def update_summary_display_text(self, summary):
        """Update the summary text display"""
        self.summary_text.delete(1.0, tk.END)
        
        report = f"""SPENDING ANALYTICS REPORT
{'='*50}

OVERVIEW
Periods Analyzed: {summary['periods_analyzed']}
Total Budgeted: ${summary['total_budgeted']:.2f}
Total Spent: ${summary['total_spent']:.2f}
Average per Period: ${summary['average_spent_per_period']:.2f}
Overall Savings Rate: {summary['overall_savings_rate']:.1f}%

CATEGORY BREAKDOWN
{'-'*50}
"""
        
        for category, data in summary['categories'].items():
            report += f"""
{category}:
  Total Spent: ${data['total_spent']:.2f}
  Average per Period: ${data['average_spent']:.2f}
  Total Budgeted: ${data['total_budgeted']:.2f}
  Variance: ${data['total_spent'] - data['total_budgeted']:.2f}
"""
        
        self.summary_text.insert(1.0, report)
    
    def update_trends_chart(self, num_periods):
        """Update the trends chart with spending data"""
        self.trends_ax.clear()
        
        # Get recent snapshots
        snapshots = list(self.time_tracker.snapshots.values())
        snapshots.sort(key=lambda s: s.period.start_date)
        recent_snapshots = snapshots[-num_periods:] if len(snapshots) >= num_periods else snapshots
        
        if len(recent_snapshots) < 2:
            self.trends_ax.text(0.5, 0.5, 'Need at least 2 periods for trends', 
                               ha='center', va='center', transform=self.trends_ax.transAxes, fontsize=12)
            self.trends_canvas.draw()
            return
        
        # Get period names and dates
        period_names = [s.period.display_name for s in recent_snapshots]
        dates = [s.period.start_date for s in recent_snapshots]
        
        # Get all categories
        all_categories = set()
        for snapshot in recent_snapshots:
            all_categories.update(snapshot.category_data.keys())
        
        # Plot spending trends for top categories by total spending
        category_totals = {}
        for category in all_categories:
            total = sum(s.get_category_actual(category) for s in recent_snapshots)
            category_totals[category] = total
        
        # Get top 5 categories
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Plot lines for each category
        for category, _ in top_categories:
            amounts = [s.get_category_actual(category) for s in recent_snapshots]
            self.trends_ax.plot(dates, amounts, marker='o', label=category[:15], linewidth=2)
        
        self.trends_ax.set_xlabel('Period')
        self.trends_ax.set_ylabel('Amount Spent ($)')
        self.trends_ax.set_title('Spending Trends Over Time')
        self.trends_ax.legend()
        self.trends_ax.grid(True, alpha=0.3)
        
        # Format x-axis
        self.trends_ax.tick_params(axis='x', rotation=45)
        
        self.trends_fig.tight_layout()
        self.trends_canvas.draw()
    
    def get_current_month_period(self):
        """Get the current month period for default loading"""
        return self.time_tracker.get_current_period(PeriodType.MONTHLY)

    def load_latest_or_current_month(self):
        """Load the most recent saved data or current month"""
        available_periods = self.time_tracker.get_available_periods()
        
        if available_periods:
            # Load most recent period
            latest_period = available_periods[0]  # Already sorted by most recent
            return latest_period.period_id
        else:
            # No saved periods, return current month
            current_period = self.get_current_month_period()
            return current_period.period_id
    
    def get_time_tracker(self):
        """Get the time tracker instance for external access"""
        return self.time_tracker