# budget_period_manager.py - Manages period operations and time tracking
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import calendar
from budget_time_tracker import BudgetPeriod, BudgetSnapshot, PeriodType
from budget_models import ViewMode


class PeriodManager:
    """Manages period operations including switching, creating, and data isolation"""
    
    def __init__(self, app):
        self.app = app
    
    def get_current_month_period_id(self):
        """Get period ID for current month"""
        now = datetime.now()
        return f"monthly_{now.year}_{now.month:02d}"
    
    def refresh_period_list(self):
        """Refresh the list of available periods"""
        try:
            time_tracker = self.app.history_tab.get_time_tracker()
            available_periods = time_tracker.get_available_periods()
            
            # Add current month if not in list
            current_period = time_tracker.get_current_period(PeriodType.MONTHLY)
            
            period_options = [current_period.display_name + " (Current)"]
            period_ids = [current_period.period_id]
            
            for period in available_periods:
                if period.period_id != current_period.period_id:
                    period_options.append(period.display_name)
                    period_ids.append(period.period_id)
            
            self.app.period_combo['values'] = period_options
            self.app.period_ids = period_ids
            
            # Select current month by default
            if period_options:
                self.app.period_combo.current(0)
                self.app.period_var.set(period_options[0])
        except Exception as e:
            print(f"Error refreshing period list: {e}")
            # Fallback - just show current month
            self.app.period_combo['values'] = ["Current Month"]
            self.app.period_ids = [self.get_current_month_period_id()]
            self.app.period_combo.current(0)
    
    def on_period_change(self, event=None):
        """Handle period selection change - ENHANCED VERSION"""
        if self.app._loading_data:
            return
            
        try:
            if self.app.period_combo.current() >= 0:
                selected_period_id = self.app.period_ids[self.app.period_combo.current()]
                current_month_id = self.get_current_month_period_id()
                
                print(f"🔄 === PERIOD CHANGE START ===")
                print(f"Switching TO: {selected_period_id}")
                print(f"Current month ID: {current_month_id}")
                
                # Save current data ONLY if we're leaving the current month
                current_selection = getattr(self.app, '_current_period_id', None)
                if current_selection and current_selection != selected_period_id:
                    if current_selection == current_month_id:
                        print(f"💾 Saving current month data before switching")
                        self.save_current_period_data()
                    else:
                        print(f"📂 Switching between historical periods - not saving")
                
                # Store the new selection
                self.app._current_period_id = selected_period_id
                
                # Load data for selected period with COMPLETE isolation and UI update
                success = self.load_period_data_complete(selected_period_id)
                
                # Force UI update after loading is complete
                if success:
                    # Make sure _loading_data is False, then trigger updates
                    self.app._loading_data = False
                    
                    # Call methods through the correct objects
                    self.app.controls_manager.update_monthly_total()  # ← Fixed this line
                    self.app.update_calculations()
                    self.app.refresh_dashboard()
                    
                    print(f"✅ Period change completed successfully")
                else:
                    print(f"⚠️ Period change completed with warnings")
                    
            else:
                print("❌ No period selected in combo box")
                            
        except Exception as e:
            print(f"❌ Error changing period: {e}")
            import traceback
            traceback.print_exc()

    def load_period_data_complete(self, period_id):
        """Load period data with COMPLETE UI synchronization"""
        if self.app._loading_data:
            return False
            
        print(f"🔄 Loading COMPLETE data for period: {period_id}")
        
        # Set loading flag
        self.app._loading_data = True
        print(f"🔍 Set loading flag to: {self.app._loading_data}")
        
        success = False  # ← ADD THIS LINE
        
        try:
            # Get time tracker and snapshot
            time_tracker = self.app.history_tab.get_time_tracker()
            snapshot = time_tracker.get_snapshot(period_id)
            current_month_id = self.get_current_month_period_id()
            
            if snapshot:
                print(f"📸 Found snapshot for {period_id}")
                self._load_from_snapshot(snapshot, period_id)
                success = True
                
            elif period_id == current_month_id:
                print(f"📅 Current month - loading fresh or from database")
                self._load_current_month_fresh()
                success = True
                
            else:
                print(f"📂 Historical period with no data - showing blank")
                self._load_blank_historical_period()
                success = False
            
            return success
            
        except Exception as e:
            print(f"❌ Error loading period data: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Always clear loading flag
            self.app._loading_data = False
            print(f"🔍 Cleared loading flag to: {self.app._loading_data}")

    def _load_from_snapshot(self, snapshot, period_id):
        """Load data from snapshot with complete UI update"""
        print(f"📸 Loading from snapshot for {period_id}")
        print(f"📸 Snapshot paychecks: ${snapshot.first_paycheck:.2f} / ${snapshot.second_paycheck:.2f}")
        
        # 1. Load paycheck amounts FIRST
        self.app.first_paycheck.set(snapshot.first_paycheck)
        self.app.second_paycheck.set(snapshot.second_paycheck)
        print(f"💰 Set UI paychecks: ${snapshot.first_paycheck:.2f} / ${snapshot.second_paycheck:.2f}")
        
        # 2. Load all category spending data
        for category_name in self.app.actual_spending.keys():
            category_data = snapshot.category_data.get(category_name, {'actual': 0.0})
            monthly_amount = category_data.get('actual', 0.0)
            
            print(f"📥 Loading {category_name}: ${monthly_amount:.2f}")
            
            # Set monthly amount
            self.app.actual_spending[category_name][ViewMode.MONTHLY].set(monthly_amount)
            
            # Split between paychecks (50/50 split)
            paycheck_amount = monthly_amount / 2
            self.app.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
            self.app.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
        
        # 3. Update spending entry widgets to use current view mode
        self.app.table_manager.update_spending_entries()

    def _load_current_month_fresh(self):
        """Load current month data from database or start fresh"""
        print(f"📅 Loading current month fresh")
        
        # Try to load from regular database first
        db_data = self.app.database.load_budget_data(self.app.current_scenario_name)
        
        if db_data:
            total_income, spending_data = db_data
            
            # Extract paycheck amounts
            first_paycheck = spending_data.get('first_paycheck', 2164.77)
            second_paycheck = spending_data.get('second_paycheck', 2154.42)
            
            print(f"💰 Found database paychecks: ${first_paycheck:.2f} / ${second_paycheck:.2f}")
            
            # Set paycheck amounts
            self.app.first_paycheck.set(first_paycheck)
            self.app.second_paycheck.set(second_paycheck)
            
            # Load spending for each category
            for category_name in self.app.actual_spending.keys():
                monthly_amount = spending_data.get(category_name, 0.0)
                
                print(f"📥 Database {category_name}: ${monthly_amount:.2f}")
                
                # Set amounts for all view modes
                self.app.actual_spending[category_name][ViewMode.MONTHLY].set(monthly_amount)
                paycheck_amount = monthly_amount / 2
                self.app.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                self.app.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
        
        else:
            print(f"📅 No database data - starting with defaults")
            # Set default paycheck amounts
            self.app.first_paycheck.set(2164.77)
            self.app.second_paycheck.set(2154.42)
            
            # Clear all spending
            for category_name in self.app.actual_spending.keys():
                for view_mode in ViewMode:
                    self.app.actual_spending[category_name][view_mode].set(0.0)
        
        # Check for overage carry-over from previous month
        self._check_and_apply_overages()
        
        # Update spending entry widgets
        self.app.table_manager.update_spending_entries()

    def _load_blank_historical_period(self):
        """Load blank data for historical period with no snapshot"""
        print(f"📂 Loading blank historical period")
        
        # Set default paycheck amounts
        self.app.first_paycheck.set(2164.77)
        self.app.second_paycheck.set(2154.42)
        
        # Clear all spending
        for category_name in self.app.actual_spending.keys():
            for view_mode in ViewMode:
                self.app.actual_spending[category_name][view_mode].set(0.0)
        
        # Update spending entry widgets
        self.app.table_manager.update_spending_entries()

    def _check_and_apply_overages(self):
        """Check for and apply overage carry-over from previous month"""
        try:
            time_tracker = self.app.history_tab.get_time_tracker()
            current_period_id = self.get_current_month_period_id()
            
            overages = time_tracker.get_previous_month_overages(current_period_id)
            
            if overages:
                print(f"💰 Applying overages: {overages}")
                
                # Apply overages to spending
                for category_name, overage_amount in overages.items():
                    if category_name in self.app.actual_spending:
                        self.app.actual_spending[category_name][ViewMode.MONTHLY].set(overage_amount)
                        paycheck_amount = overage_amount / 2
                        self.app.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                        self.app.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
                
                # Show user notification
                from tkinter import messagebox
                overage_summary = "\n".join([f"• {cat}: ${amt:.2f}" for cat, amt in overages.items()])
                total_overage = sum(overages.values())
                
                messagebox.showinfo("Over-Budget Categories Carried Forward", 
                    f"Applied previous over-budget spending:\n\n{overage_summary}\n\n"
                    f"Total carried forward: ${total_overage:.2f}")
            else:
                print(f"✅ No overages to apply")
                
        except Exception as e:
            print(f"⚠️ Error checking overages: {e}")

    def _force_complete_ui_refresh(self):
        """Force COMPLETE UI refresh - with loading flag debug"""
        print(f"🔄 Forcing COMPLETE UI refresh...")
        print(f"🔍 Loading flag status: {self.app._loading_data}")
        
        try:
            # 1. Update monthly total display
            self.app.controls_manager.update_monthly_total()
            
            # 2. Update spending entry widgets
            self.app.table_manager.update_spending_entries()
            
            # 3. Force UI update
            self.app.root.update_idletasks()
            
            # 4. Check loading flag before calculations
            print(f"🔍 Loading flag before calculations: {self.app._loading_data}")
            
            # 5. Run calculations
            self.app.update_calculations()
            
            # 6. Refresh dashboard
            self.app.refresh_dashboard()
            
            print(f"✅ COMPLETE UI refresh finished")
            
        except Exception as e:
            print(f"❌ Error during UI refresh: {e}")

    def on_paycheck_change(self):
        """Handle paycheck amount changes - triggers UI update"""
        if self.app._loading_data:
            return
            
        try:
            # Update monthly total display
            self.app.controls_manager.update_monthly_total()
            
            # Update calculations (this will cascade to the table)
            self.app.update_calculations()
            
            # If this is the current month, save the changes
            current_month_id = self.app.period_manager.get_current_month_period_id()
            if getattr(self.app, '_current_period_id', None) == current_month_id:
                # Auto-save if enabled
                if self.app.config.auto_save:
                    self.app.data_manager.auto_save_data()
                    
        except Exception as e:
            print(f"Error handling paycheck change: {e}")
    
    def start_fresh_current_month(self):
        """Start fresh for current month with overage carry-over - ENHANCED"""
        print("🆕 Starting fresh current month")
        
        # Keep current paycheck amounts (don't reset them)
        current_first = self.app.first_paycheck.get()
        current_second = self.app.second_paycheck.get()
        
        # Clear all spending first
        for category_data in self.app.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        
        # Check for overage carry-over from previous month
        time_tracker = self.app.history_tab.get_time_tracker()
        current_period_id = self.get_current_month_period_id()
        
        try:
            overages = time_tracker.get_previous_month_overages(current_period_id)
            
            if overages:
                print(f"💰 Carrying over overages: {overages}")
                
                # Apply overages
                for category_name, overage_amount in overages.items():
                    if category_name in self.app.actual_spending:
                        self.app.actual_spending[category_name][ViewMode.MONTHLY].set(overage_amount)
                        paycheck_amount = overage_amount / 2
                        self.app.actual_spending[category_name][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                        self.app.actual_spending[category_name][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
                
                # Show user what was carried over
                overage_summary = "\n".join([f"• {cat}: ${amt:.2f}" for cat, amt in overages.items()])
                total_overage = sum(overages.values())
                
                messagebox.showinfo("Over-Budget Categories Carried Forward", 
                    f"Starting fresh month with previous 'Over Budget' spending:\n\n{overage_summary}\n\n"
                    f"Total overspending carried forward: ${total_overage:.2f}")
            else:
                print("✅ No overages to carry forward")
                
        except Exception as e:
            print(f"⚠️ Error checking overages: {e}")
        
        # Restore paycheck amounts
        self.app.first_paycheck.set(current_first)
        self.app.second_paycheck.set(current_second)
        
        # Load from database for current month
        self.app.data_manager.load_initial_data()
        
        # CRITICAL FIX: Force complete UI refresh
        self.force_ui_refresh()
    
    def show_blank_historical_period(self):
        """Show blank data for historical period with no snapshot - ENHANCED"""
        print("🗂️ Showing blank historical period")
        
        # Set default paycheck amounts for historical periods
        self.app.first_paycheck.set(2164.77)
        self.app.second_paycheck.set(2154.42)
        
        # Clear all spending
        for category_data in self.app.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        
        # CRITICAL FIX: Force complete UI refresh
        self.force_ui_refresh()
    
    def save_current_period_data(self):
        """Save data for the current period being viewed"""
        if not hasattr(self.app, '_current_period_id'):
            return
            
        period_id = self.app._current_period_id
        current_month_id = self.get_current_month_period_id()
        
        # Only save snapshots for current month or when explicitly saving
        if period_id != current_month_id:
            print(f"Not saving snapshot for historical period: {period_id}")
            return
        
        print(f"Saving current period data for: {period_id}")
        
        try:
            time_tracker = self.app.history_tab.get_time_tracker()
            
            # Get current period object
            period = time_tracker.get_current_period(PeriodType.MONTHLY)
            
            # CRITICAL FIX: Get actual paycheck values from UI
            first_paycheck = self.app.first_paycheck.get()
            second_paycheck = self.app.second_paycheck.get()
            
            print(f"💰 Saving paychecks: ${first_paycheck:.2f} / ${second_paycheck:.2f}")
            
            # Get current budget data
            budget_data = self.app.get_current_budget_data()
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
            
            # Create snapshot with ACTUAL paycheck values
            snapshot = BudgetSnapshot(
                period=period,
                scenario_name=budget_data['scenario_name'],
                first_paycheck=first_paycheck,        # ← Use UI values
                second_paycheck=second_paycheck,      # ← Use UI values
                total_income=first_paycheck + second_paycheck,  # ← Calculate from UI
                view_mode=budget_data['view_mode'].value,
                category_data=category_data,
                total_budgeted=budget_data['summary'].total_budgeted,
                total_spent=budget_data['summary'].total_spent,
                saved_date=datetime.now()
            )
            
            # Save the snapshot
            time_tracker.save_snapshot(snapshot)
            print(f"Saved snapshot for {period_id} with paychecks ${first_paycheck:.2f}/${second_paycheck:.2f}")
            
        except Exception as e:
            print(f"Error saving current period data: {e}")
    
    def create_manual_period(self):
        """Create a manual period for data entry"""
        # Create dialog for manual period creation
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Create Historical Period")
        dialog.geometry("400x300")
        dialog.transient(self.app.root)
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
                time_tracker = self.app.history_tab.get_time_tracker()
                
                # Create empty category data (all zeros)
                category_data = {}
                scenario = self.app.budget_data.get_scenario(self.app.current_scenario_name)
                for category_name in scenario.get_all_categories().keys():
                    category_data[category_name] = {
                        'budgeted': 0.0,  # Will be calculated when user enters spending
                        'actual': 0.0,
                        'notes': ''
                    }
                
                # Create snapshot
                snapshot = BudgetSnapshot(
                    period=period,
                    scenario_name=self.app.current_scenario_name,
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
                for i, period_id_check in enumerate(self.app.period_ids):
                    if period_id_check == period_id:
                        self.app.period_combo.current(i)
                        self.app.period_var.set(self.app.period_combo.get())
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