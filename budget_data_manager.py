# # budget_data_manager.py - Manages all data operations
# import tkinter as tk
# from tkinter import messagebox
# from datetime import datetime
# from budget_models import ViewMode
# from budget_time_tracker import BudgetSnapshot

# class DataManager:
#     """Manages all data operations including loading, saving, and validation"""
    
#     def __init__(self, app):
#         self.app = app
    
#     def load_initial_data(self):
#         """Load initial data on app startup"""
#         print("Loading initial data...")
        
#         # Try to load from database first
#         data = self.app.database.load_budget_data(self.app.current_scenario_name)
        
#         if data:
#             income, spending_data = data
            
#             # Load EXACT individual paycheck amounts
#             stored_first = spending_data.get('first_paycheck')
#             stored_second = spending_data.get('second_paycheck')
            
#             if stored_first is not None and stored_second is not None:
#                 print(f"Loading stored paychecks: ${stored_first:.2f} / ${stored_second:.2f}")
#                 self.app.first_paycheck.set(stored_first)
#                 self.app.second_paycheck.set(stored_second)
#             else:
#                 print("No stored paychecks found - using defaults")
            
#             # Load spending amounts for all view modes
#             for category in self.app.actual_spending.keys():
#                 for view_mode in ViewMode:
#                     key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
#                     amount = spending_data.get(key, 0.0)
#                     self.app.actual_spending[category][view_mode].set(amount)
#         else:
#             print("No database data found - starting fresh")
#             # For a completely fresh start, clear all spending
#             self.clear_all_spending_silent()
        
#         self.update_monthly_total()
    
#     def get_safe_paychecks(self):
#         """Get paycheck amounts with error handling"""
#         try:
#             first = self.app.first_paycheck.get()
#         except (ValueError, tk.TclError):
#             first = 2164.77  # Default
        
#         try:
#             second = self.app.second_paycheck.get()
#         except (ValueError, tk.TclError):
#             second = 2154.42  # Default
        
#         return first, second
    
#     def get_safe_spending(self):
#         """Get spending amounts for current view mode with error handling"""
#         spending = {}
#         for category, view_data in self.app.actual_spending.items():
#             try:
#                 spending[category] = view_data[self.app.view_mode].get()
#             except (ValueError, tk.TclError):
#                 spending[category] = 0.0
#         return spending
    
#     def update_monthly_total(self):
#         """Update monthly total display"""
#         if hasattr(self.app, 'controls_manager') and self.app.controls_manager:
#             self.app.controls_manager.update_monthly_total()
    
#     def on_scenario_change(self, event=None):
#         """Handle scenario change"""
#         if self.app._loading_data:
#             return
            
#         print(f"Scenario changed to: {self.app.scenario_var.get()}")
#         self.save_data()  # Save current data
#         self.app.current_scenario_name = self.app.scenario_var.get()
#         self.app.table_manager.create_category_rows()  # Recreate rows for new scenario
#         self.load_initial_data()  # Load data for new scenario
#         self.app.update_calculations()
    
#     def on_view_change(self, event=None):
#         """Handle view mode change"""
#         view_str = self.app.view_var.get()
        
#         if view_str == "First Paycheck":
#             self.app.view_mode = ViewMode.FIRST_PAYCHECK
#         elif view_str == "Second Paycheck":
#             self.app.view_mode = ViewMode.SECOND_PAYCHECK
#         else:
#             self.app.view_mode = ViewMode.MONTHLY
        
#         # Update entry widgets to use the new view mode
#         self.app.table_manager.update_spending_entries()
#         self.app.update_calculations()
    
#     def on_paycheck_change(self):
#         """Handle paycheck amount change"""
#         if self.app._loading_data:
#             return
            
#         self.update_monthly_total()
#         self.app.root.after(100, self.app.update_calculations)  # Small delay for smooth typing
        
#         # Auto-save if enabled
#         if self.app.config.auto_save:
#             self.app.root.after(1000, self.auto_save_data)
        
#         # Update dashboard
#         self.app.root.after(200, self.app.refresh_dashboard)
    
#     def on_spending_change(self, category):
#         """Handle spending amount change"""
#         if self.app._loading_data:
#             return
            
#         # If we're in monthly view, split the amount between paychecks
#         if self.app.view_mode == ViewMode.MONTHLY:
#             try:
#                 monthly_amount = self.app.actual_spending[category][ViewMode.MONTHLY].get()
#                 # Split 50/50 between paychecks
#                 paycheck_amount = monthly_amount / 2
#                 self.app.actual_spending[category][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
#                 self.app.actual_spending[category][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
#             except (ValueError, tk.TclError):
#                 pass
#         else:
#             # If we're in paycheck view, update monthly total
#             try:
#                 first_amount = self.app.actual_spending[category][ViewMode.FIRST_PAYCHECK].get()
#                 second_amount = self.app.actual_spending[category][ViewMode.SECOND_PAYCHECK].get()
#                 monthly_amount = first_amount + second_amount
#                 self.app.actual_spending[category][ViewMode.MONTHLY].set(monthly_amount)
#             except (ValueError, tk.TclError):
#                 pass
        
#         self.app.root.after(100, self.app.update_calculations)
        
#         # Auto-save if enabled
#         if self.app.config.auto_save:
#             self.app.root.after(1000, self.auto_save_data)
        
#         # Update dashboard
#         self.app.root.after(200, self.app.refresh_dashboard)
    
#     def save_data(self):
#         """Save current data to database"""
#         if self.app._loading_data:
#             return False
            
#         first_paycheck, second_paycheck = self.get_safe_paychecks()
        
#         print(f"=== SAVING DATA ===")
#         print(f"Paychecks: ${first_paycheck:.2f} / ${second_paycheck:.2f}")
#         print(f"Current period: {getattr(self.app, '_current_period_id', 'None')}")
        
#         # Save to database (regular scenario data)
#         all_spending = {}
#         for category, view_data in self.app.actual_spending.items():
#             for view_mode in ViewMode:
#                 key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
#                 try:
#                     all_spending[key] = view_data[view_mode].get()
#                 except (ValueError, tk.TclError):
#                     all_spending[key] = 0.0
        
#         # Save paycheck amounts
#         all_spending['first_paycheck'] = first_paycheck
#         all_spending['second_paycheck'] = second_paycheck
        
#         success = self.app.database.save_budget_data(
#             self.app.current_scenario_name, first_paycheck + second_paycheck, all_spending)
        
#         if success:
#             print("Database save successful")
            
#             # Also save as period snapshot
#             current_month_id = self.app.period_manager.get_current_month_period_id()
#             current_period = getattr(self.app, '_current_period_id', current_month_id)
            
#             if current_period == current_month_id:
#                 print("Saving current month snapshot")
#                 self.save_current_period_snapshot()
#             else:
#                 print("Saving historical period snapshot")
#                 self.save_historical_period_snapshot(current_period)
            
#             messagebox.showinfo("Success", "Data saved to database!")
            
#             # Create backup if enabled
#             if self.app.config.auto_backup:
#                 self.app.database.create_backup(self.app.config.backup_directory)
#         else:
#             messagebox.showerror("Error", "Failed to save data to database!")
        
#         return success
    
#     def auto_save_data(self):
#         """Auto-save data without showing message"""
#         if self.app._loading_data:
#             return
            
#         first_paycheck, second_paycheck = self.get_safe_paychecks()
        
#         # Save spending data for all view modes
#         all_spending = {}
#         for category, view_data in self.app.actual_spending.items():
#             for view_mode in ViewMode:
#                 key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
#                 try:
#                     all_spending[key] = view_data[view_mode].get()
#                 except (ValueError, tk.TclError):
#                     all_spending[key] = 0.0
        
#         # Save paycheck amounts SEPARATELY
#         all_spending['first_paycheck'] = first_paycheck
#         all_spending['second_paycheck'] = second_paycheck
        
#         success = self.app.database.save_budget_data(
#             self.app.current_scenario_name, first_paycheck + second_paycheck, all_spending)
        
#         # Also auto-save snapshot if save was successful
#         if success:
#             self.save_current_period_snapshot()
    
#     def save_current_period_snapshot(self):
#         """Save a snapshot of current period to history"""
#         try:
#             time_tracker = self.app.history_tab.get_time_tracker()
#             current_period = time_tracker.get_current_period(self.app.period_manager.PeriodType.MONTHLY)
            
#             # Get current budget data
#             budget_data = self.app.get_current_budget_data()
#             if not budget_data:
#                 return
            
#             # Create category data for snapshot
#             category_data = {}
#             for category_name, result in budget_data['category_results'].items():
#                 category_data[category_name] = {
#                     'budgeted': result.budgeted,
#                     'actual': result.actual,
#                     'notes': ''
#                 }
            
#             # Create snapshot with individual paycheck amounts
#             snapshot = BudgetSnapshot(
#                 period=current_period,
#                 scenario_name=budget_data['scenario_name'],
#                 first_paycheck=budget_data['first_paycheck'],
#                 second_paycheck=budget_data['second_paycheck'],
#                 total_income=budget_data['total_income'],
#                 view_mode=budget_data['view_mode'].value,
#                 category_data=category_data,
#                 total_budgeted=budget_data['summary'].total_budgeted,
#                 total_spent=budget_data['summary'].total_spent,
#                 saved_date=datetime.now()
#             )
            
#             time_tracker.save_snapshot(snapshot)
            
#         except Exception as e:
#             print(f"Error saving snapshot: {e}")
    
#     def save_historical_period_snapshot(self, period_id):
#         """Save snapshot for historical period being edited"""
#         try:
#             time_tracker = self.app.history_tab.get_time_tracker()
            
#             # Get existing snapshot to preserve period info
#             existing_snapshot = time_tracker.get_snapshot(period_id)
#             if not existing_snapshot:
#                 print(f"Cannot save historical period {period_id} - no existing snapshot")
#                 return
            
#             period = existing_snapshot.period
            
#             # Get current budget data
#             budget_data = self.app.get_current_budget_data()
#             if not budget_data:
#                 return
            
#             # Create category data for snapshot
#             category_data = {}
#             for category_name, result in budget_data['category_results'].items():
#                 category_data[category_name] = {
#                     'budgeted': result.budgeted,
#                     'actual': result.actual,
#                     'notes': ''
#                 }
            
#             # Create updated snapshot
#             snapshot = BudgetSnapshot(
#                 period=period,
#                 scenario_name=budget_data['scenario_name'],
#                 first_paycheck=budget_data['first_paycheck'],
#                 second_paycheck=budget_data['second_paycheck'],
#                 total_income=budget_data['total_income'],
#                 view_mode=budget_data['view_mode'].value,
#                 category_data=category_data,
#                 total_budgeted=budget_data['summary'].total_budgeted,
#                 total_spent=budget_data['summary'].total_spent,
#                 saved_date=datetime.now()
#             )
            
#             # Save the updated snapshot
#             time_tracker.save_snapshot(snapshot)
#             print(f"Saved historical snapshot for {period_id}")
            
#         except Exception as e:
#             print(f"Error saving historical period snapshot: {e}")
    
#     def clear_all_spending(self):
#         """Clear all spending data"""
#         if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
#             self.clear_all_spending_silent()
            
#     def clear_all_spending_silent(self):
#         """Clear all spending data without confirmation"""
#         for category_data in self.app.actual_spending.values():
#             for view_mode in ViewMode:
#                 category_data[view_mode].set(0.0)
#         self.app.update_calculations()
    
#     def debug_paycheck_values(self):
#         """Debug method to check paycheck values"""
#         try:
#             first = self.app.first_paycheck.get()
#             second = self.app.second_paycheck.get()
#             total = first + second
            
#             print(f"=== PAYCHECK DEBUG ===")
#             print(f"  UI First Paycheck: {first}")
#             print(f"  UI Second Paycheck: {second}")
#             print(f"  UI Total: {total}")
            
#             # Check what's in database
#             data = self.app.database.load_budget_data(self.app.current_scenario_name)
#             if data:
#                 income, spending_data = data
#                 db_first = spending_data.get('first_paycheck')
#                 db_second = spending_data.get('second_paycheck')
#                 print(f"  Database First: {db_first}")
#                 print(f"  Database Second: {db_second}")
#                 print(f"  Database Total: {income}")
                
#                 # Check for corruption
#                 if db_first is not None and abs(db_first - first) > 0.01:
#                     print(f"  WARNING: Database value differs from UI!")
#             else:
#                 print(f"  No database data found")
            
#             # Check current period snapshot
#             time_tracker = self.app.history_tab.get_time_tracker()
#             current_period_id = self.app.period_manager.get_current_month_period_id()
#             snapshot = time_tracker.get_snapshot(current_period_id)
#             if snapshot:
#                 print(f"  Snapshot First: {snapshot.first_paycheck}")
#                 print(f"  Snapshot Second: {snapshot.second_paycheck}")
#                 print(f"  Snapshot Total: {snapshot.total_income}")
#             else:
#                 print(f"  No snapshot for current period: {current_period_id}")
            
#             print(f"=== END DEBUG ===")
            
#             # Show in UI as well
#             messagebox.showinfo("Debug Info", 
#                 f"UI: ${first:.2f} / ${second:.2f}\n"
#                 f"DB: ${db_first or 'None'} / ${db_second or 'None'}\n"
#                 f"See console for full details")
        
#         except Exception as e:
#             print(f"Debug error: {e}")

#     def debug_period_data_isolation(self):
#         """Comprehensive debugging for period data isolation issues"""
        
#         print("\n" + "="*60)
#         print("🔍 PERIOD DATA ISOLATION DEBUG")
#         print("="*60)
        
#         # 1. Check current application state
#         current_period = getattr(self.app, '_current_period_id', 'UNKNOWN')
#         current_month_id = self.app.period_manager.get_current_month_period_id()
        
#         print(f"📍 Current Period ID: {current_period}")
#         print(f"📅 Current Month ID: {current_month_id}")
#         print(f"🏷️  Scenario: {self.app.current_scenario_name}")
        
#         # 2. Check paycheck values in different places
#         print(f"\n💰 PAYCHECK VALUES:")
#         ui_first = self.app.first_paycheck.get()
#         ui_second = self.app.second_paycheck.get()
#         print(f"   UI First: ${ui_first:.2f}")
#         print(f"   UI Second: ${ui_second:.2f}")
#         print(f"   UI Total: ${ui_first + ui_second:.2f}")
        
#         # 3. Check database values
#         print(f"\n🗄️  DATABASE VALUES:")
#         db_data = self.app.database.load_budget_data(self.app.current_scenario_name)
#         if db_data:
#             income, spending_data = db_data
#             db_first = spending_data.get('first_paycheck', 'NOT_FOUND')
#             db_second = spending_data.get('second_paycheck', 'NOT_FOUND')
#             print(f"   DB First: ${db_first}")
#             print(f"   DB Second: ${db_second}")
#             print(f"   DB Total Income: ${income:.2f}")
#         else:
#             print("   No database data found")
        
#         # 4. Check snapshots for July and August
#         print(f"\n📸 SNAPSHOT DATA:")
#         time_tracker = self.app.history_tab.get_time_tracker()
        
#         # Check July 2025
#         july_id = "monthly_2025_07"
#         july_snapshot = time_tracker.get_snapshot(july_id)
#         if july_snapshot:
#             print(f"   July 2025: ${july_snapshot.first_paycheck:.2f} / ${july_snapshot.second_paycheck:.2f}")
#             print(f"   July Total: ${july_snapshot.total_income:.2f}")
#             # Show some category data
#             for i, (cat, data) in enumerate(july_snapshot.category_data.items()):
#                 if i < 3:  # Show first 3 categories
#                     print(f"     {cat}: ${data.get('actual', 0):.2f}")
#         else:
#             print("   July 2025: No snapshot found")
        
#         # Check August 2025
#         august_id = "monthly_2025_08"
#         august_snapshot = time_tracker.get_snapshot(august_id)
#         if august_snapshot:
#             print(f"   August 2025: ${august_snapshot.first_paycheck:.2f} / ${august_snapshot.second_paycheck:.2f}")
#             print(f"   August Total: ${august_snapshot.total_income:.2f}")
#             # Show some category data
#             for i, (cat, data) in enumerate(august_snapshot.category_data.items()):
#                 if i < 3:  # Show first 3 categories
#                     print(f"     {cat}: ${data.get('actual', 0):.2f}")
#         else:
#             print("   August 2025: No snapshot found")
        
#         # 5. Check current UI spending values
#         print(f"\n💸 CURRENT UI SPENDING (first 5 categories):")
#         for i, (category, view_data) in enumerate(self.app.actual_spending.items()):
#             if i < 5:
#                 monthly_val = view_data[self.app.view_mode].get()
#                 print(f"   {category}: ${monthly_val:.2f}")
        
#         # 6. Check for data corruption indicators
#         print(f"\n⚠️  CORRUPTION CHECKS:")
        
#         # Check if paycheck values match between UI and database
#         if db_data:
#             db_first = spending_data.get('first_paycheck', 0)
#             db_second = spending_data.get('second_paycheck', 0)
#             if abs(ui_first - db_first) > 0.01 or abs(ui_second - db_second) > 0.01:
#                 print("   🚨 WARNING: UI paycheck values don't match database!")
#                 print(f"      UI: ${ui_first:.2f} / ${ui_second:.2f}")
#                 print(f"      DB: ${db_first:.2f} / ${db_second:.2f}")
#             else:
#                 print("   ✅ Paycheck values match between UI and database")
        
#         # Check if current period matches what should be displayed
#         if current_period == august_id and july_snapshot and august_snapshot:
#             # We're viewing August but check if data looks like July
#             july_total = july_snapshot.total_income
#             august_total = august_snapshot.total_income
#             if abs(ui_first + ui_second - july_total) < 0.01:
#                 print("   🚨 WARNING: Viewing August but UI shows July paycheck amounts!")
#             elif abs(ui_first + ui_second - august_total) < 0.01:
#                 print("   ✅ August period shows correct paycheck amounts")
        
#         print("="*60)
#         print("🔍 END DEBUG")
#         print("="*60 + "\n")

#     def debug_save_load_cycle(self):
#         """Debug the save/load cycle for period data"""
        
#         print("\n" + "="*50)
#         print("🔄 SAVE/LOAD CYCLE DEBUG")
#         print("="*50)
        
#         current_period = getattr(self.app, '_current_period_id', 'UNKNOWN')
#         print(f"Current period: {current_period}")
        
#         # Capture current state before save
#         print("\n📥 BEFORE SAVE:")
#         pre_save_first = self.app.first_paycheck.get()
#         pre_save_second = self.app.second_paycheck.get()
#         print(f"  Paychecks: ${pre_save_first:.2f} / ${pre_save_second:.2f}")
        
#         # Show first few category values
#         pre_save_spending = {}
#         for i, (cat, view_data) in enumerate(self.app.actual_spending.items()):
#             if i < 3:
#                 val = view_data[self.app.view_mode].get()
#                 pre_save_spending[cat] = val
#                 print(f"  {cat}: ${val:.2f}")
        
#         # Perform save
#         print(f"\n💾 SAVING...")
#         success = self.save_data()
#         print(f"  Save success: {success}")
        
#         # Check what was actually saved
#         print(f"\n📤 WHAT WAS SAVED:")
        
#         # Check database
#         db_data = self.app.database.load_budget_data(self.app.current_scenario_name)
#         if db_data:
#             income, spending_data = db_data
#             saved_first = spending_data.get('first_paycheck', 'NOT_FOUND')
#             saved_second = spending_data.get('second_paycheck', 'NOT_FOUND')
#             print(f"  DB Paychecks: ${saved_first} / ${saved_second}")
        
#         # Check snapshot
#         time_tracker = self.app.history_tab.get_time_tracker()
#         snapshot = time_tracker.get_snapshot(current_period)
#         if snapshot:
#             print(f"  Snapshot Paychecks: ${snapshot.first_paycheck:.2f} / ${snapshot.second_paycheck:.2f}")
#             for cat in pre_save_spending.keys():
#                 snap_val = snapshot.category_data.get(cat, {}).get('actual', 0)
#                 print(f"  Snapshot {cat}: ${snap_val:.2f}")
        
#         print("="*50)
#         print("🔄 END SAVE/LOAD DEBUG")
#         print("="*50 + "\n")

#     def debug_period_switching(self, from_period, to_period):
#         """Debug period switching operations"""
        
#         print(f"\n🔄 PERIOD SWITCH DEBUG: {from_period} → {to_period}")
#         print("="*60)
        
#         time_tracker = self.app.history_tab.get_time_tracker()
        
#         # Check what we're switching FROM
#         from_snapshot = time_tracker.get_snapshot(from_period)
#         if from_snapshot:
#             print(f"📤 FROM {from_period}:")
#             print(f"   Paychecks: ${from_snapshot.first_paycheck:.2f} / ${from_snapshot.second_paycheck:.2f}")
#             print(f"   Total spent: ${from_snapshot.total_spent:.2f}")
#         else:
#             print(f"📤 FROM {from_period}: No snapshot found")
        
#         # Check what we're switching TO
#         to_snapshot = time_tracker.get_snapshot(to_period)
#         if to_snapshot:
#             print(f"📥 TO {to_period}:")
#             print(f"   Paychecks: ${to_snapshot.first_paycheck:.2f} / ${to_snapshot.second_paycheck:.2f}")
#             print(f"   Total spent: ${to_snapshot.total_spent:.2f}")
#         else:
#             print(f"📥 TO {to_period}: No snapshot found")
        
#         print("="*60 + "\n")

# budget_data_manager.py - Manages all data operations
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from budget_models import ViewMode
from budget_time_tracker import BudgetSnapshot, PeriodType

class DataManager:
    """Manages all data operations including loading, saving, and validation"""
    
    def __init__(self, app):
        self.app = app
    
    def load_initial_data(self):
        """Load initial data on app startup - ENHANCED VERSION"""
        print("💾 Loading initial data...")
        
        current_month_id = self.app.period_manager.get_current_month_period_id()
        current_period = getattr(self.app, '_current_period_id', current_month_id)
        
        print(f"📍 Current month ID: {current_month_id}")
        print(f"📍 Current period: {current_period}")
        
        # CRITICAL FIX: Only load from database if we're viewing current month
        if current_period == current_month_id:
            print("✅ Loading from DATABASE (current month)")
            
            # Try to load from database first
            data = self.app.database.load_budget_data(self.app.current_scenario_name)
            
            if data:
                income, spending_data = data
                
                # Load EXACT individual paycheck amounts
                stored_first = spending_data.get('first_paycheck')
                stored_second = spending_data.get('second_paycheck')
                
                if stored_first is not None and stored_second is not None:
                    print(f"💰 Loading stored paychecks: ${stored_first:.2f} / ${stored_second:.2f}")
                    self.app.first_paycheck.set(stored_first)
                    self.app.second_paycheck.set(stored_second)
                else:
                    print("⚠️ No stored paychecks found - using defaults")
                
                # Load spending amounts for all view modes
                for category in self.app.actual_spending.keys():
                    for view_mode in ViewMode:
                        key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
                        amount = spending_data.get(key, 0.0)
                        self.app.actual_spending[category][view_mode].set(amount)
                        
                print("✅ Database data loaded successfully")
            else:
                print("❌ No database data found - starting fresh")
                # For a completely fresh start, clear all spending
                self.clear_all_spending_silent()
        else:
            print("⚠️ SKIPPING database load (historical period)")
            print("📂 Historical periods load from snapshots only")
            # Don't load from database for historical periods
            # They will be loaded by the period manager
        
        self.update_monthly_total()
        print("✅ Initial data loading complete")
    
    def get_safe_paychecks(self):
        """Get paycheck amounts with error handling"""
        try:
            first = self.app.first_paycheck.get()
        except (ValueError, tk.TclError):
            first = 2164.77  # Default
        
        try:
            second = self.app.second_paycheck.get()
        except (ValueError, tk.TclError):
            second = 2154.42  # Default
        
        return first, second
    
    def get_safe_spending(self):
        """Get spending amounts for current view mode with error handling"""
        spending = {}
        for category, view_data in self.app.actual_spending.items():
            try:
                spending[category] = view_data[self.app.view_mode].get()
            except (ValueError, tk.TclError):
                spending[category] = 0.0
        return spending
    
    def update_monthly_total(self):
        """Update monthly total display"""
        if hasattr(self.app, 'controls_manager') and self.app.controls_manager:
            self.app.controls_manager.update_monthly_total()
    
    def on_scenario_change(self, event=None):
        """Handle scenario change"""
        if self.app._loading_data:
            return
            
        print(f"Scenario changed to: {self.app.scenario_var.get()}")
        self.save_data()  # Save current data
        self.app.current_scenario_name = self.app.scenario_var.get()
        self.app.table_manager.create_category_rows()  # Recreate rows for new scenario
        self.load_initial_data()  # Load data for new scenario
        self.app.update_calculations()
    
    def on_view_change(self, event=None):
        """Handle view mode change"""
        view_str = self.app.view_var.get()
        
        if view_str == "First Paycheck":
            self.app.view_mode = ViewMode.FIRST_PAYCHECK
        elif view_str == "Second Paycheck":
            self.app.view_mode = ViewMode.SECOND_PAYCHECK
        else:
            self.app.view_mode = ViewMode.MONTHLY
        
        # Update entry widgets to use the new view mode
        self.app.table_manager.update_spending_entries()
        self.app.update_calculations()
    
    def on_paycheck_change(self):
        """Handle paycheck amount change"""
        # Allow updates if we're just finishing loading a period
        if self.app._loading_data and not getattr(self.app, '_allow_paycheck_update', False):
            return
            
        self.update_monthly_total()
        self.app.root.after(100, self.app.update_calculations)  # Small delay for smooth typing
        
        # Auto-save if enabled
        if self.app.config.auto_save:
            self.app.root.after(1000, self.auto_save_data)
        
        # Update dashboard
        self.app.root.after(200, self.app.refresh_dashboard)
    
    def on_spending_change(self, category):
        """Handle spending amount change"""
        if self.app._loading_data:
            return
            
        # If we're in monthly view, split the amount between paychecks
        if self.app.view_mode == ViewMode.MONTHLY:
            try:
                monthly_amount = self.app.actual_spending[category][ViewMode.MONTHLY].get()
                # Split 50/50 between paychecks
                paycheck_amount = monthly_amount / 2
                self.app.actual_spending[category][ViewMode.FIRST_PAYCHECK].set(paycheck_amount)
                self.app.actual_spending[category][ViewMode.SECOND_PAYCHECK].set(paycheck_amount)
            except (ValueError, tk.TclError):
                pass
        else:
            # If we're in paycheck view, update monthly total
            try:
                first_amount = self.app.actual_spending[category][ViewMode.FIRST_PAYCHECK].get()
                second_amount = self.app.actual_spending[category][ViewMode.SECOND_PAYCHECK].get()
                monthly_amount = first_amount + second_amount
                self.app.actual_spending[category][ViewMode.MONTHLY].set(monthly_amount)
            except (ValueError, tk.TclError):
                pass
        
        self.app.root.after(100, self.app.update_calculations)
        
        # Auto-save if enabled
        if self.app.config.auto_save:
            self.app.root.after(1000, self.auto_save_data)
        
        # Update dashboard
        self.app.root.after(200, self.app.refresh_dashboard)
    
    def save_data(self):
        """Save current data to both snapshot and regular database"""
        try:
            # Get current data
            first_paycheck, second_paycheck = self.get_safe_paychecks()
            spending = self.get_safe_spending()
            
            # CRITICAL: Include paycheck amounts in the spending dictionary
            spending_with_paychecks = {
                **spending,
                'first_paycheck': first_paycheck,
                'second_paycheck': second_paycheck
            }
            
            # Save to regular budget_data table
            success = self.app.database.save_budget_data(
                self.app.current_scenario_name,
                first_paycheck + second_paycheck,
                spending_with_paychecks
            )
            
            if success:
                # Also save current period as snapshot
                self.app.period_manager.save_current_period_data()
                messagebox.showinfo("Success", "Data saved successfully!")
                return True
            else:
                messagebox.showerror("Error", "Failed to save data to database!")
                return False
                
        except Exception as e:
            print(f"Error saving data: {e}")
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            return False

    def save_current_period_snapshot(self):
        """Save current data as a snapshot for historical tracking"""
        try:
            # Get current budget data
            budget_data = self.app.get_current_budget_data()
            if not budget_data:
                return
                
            # Get time tracker from history tab
            time_tracker = self.app.history_tab.get_time_tracker()
            current_period = time_tracker.get_current_period(PeriodType.MONTHLY)
            
            # Create category data for snapshot
            category_data = {}
            for category_name, result in budget_data['category_results'].items():
                category_data[category_name] = {
                    'budgeted': result.budgeted,
                    'actual': result.actual,
                    'notes': ''
                }
            
            # Create snapshot
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
            
            # Save the snapshot
            time_tracker.save_snapshot(snapshot)
            print("✅ Also saved current data as historical snapshot")
            
        except Exception as e:
            print(f"Warning: Could not save snapshot: {e}")
    
    def auto_save_data(self):
        """Auto-save data without showing message - FIXED VERSION"""
        if self.app._loading_data:
            return
            
        current_month_id = self.app.period_manager.get_current_month_period_id()
        current_period = getattr(self.app, '_current_period_id', current_month_id)
        
        # CRITICAL FIX: Only auto-save to database for current month
        if current_period == current_month_id:
            first_paycheck, second_paycheck = self.get_safe_paychecks()
            
            # Save spending data for all view modes
            all_spending = {}
            for category, view_data in self.app.actual_spending.items():
                for view_mode in ViewMode:
                    key = f"{category}_{view_mode.value.replace(' ', '_').lower()}"
                    try:
                        all_spending[key] = view_data[view_mode].get()
                    except (ValueError, tk.TclError):
                        all_spending[key] = 0.0
            
            # Save paycheck amounts SEPARATELY
            all_spending['first_paycheck'] = first_paycheck
            all_spending['second_paycheck'] = second_paycheck
            
            success = self.app.database.save_budget_data(
                self.app.current_scenario_name, first_paycheck + second_paycheck, all_spending)
            
            # Also auto-save snapshot if save was successful
            if success:
                self.save_current_period_snapshot()
        else:
            print("Auto-save: Historical period - saving snapshot only")
            # For historical periods, only save snapshot
            self.save_historical_period_snapshot(current_period)
    
    def save_current_period_snapshot(self):
        """Save a snapshot of current period to history"""
        try:
            time_tracker = self.app.history_tab.get_time_tracker()
            current_period = time_tracker.get_current_period(PeriodType.MONTHLY)
            
            # Get current budget data
            budget_data = self.app.get_current_budget_data()
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
    
    def save_historical_period_snapshot(self, period_id):
        """Save snapshot for historical period being edited"""
        try:
            time_tracker = self.app.history_tab.get_time_tracker()
            
            # Get existing snapshot to preserve period info
            existing_snapshot = time_tracker.get_snapshot(period_id)
            if not existing_snapshot:
                print(f"Cannot save historical period {period_id} - no existing snapshot")
                return
            
            period = existing_snapshot.period
            
            # Get current budget data
            budget_data = self.app.get_current_budget_data()
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
    
    def clear_all_spending(self):
        """Clear all spending data"""
        if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
            self.clear_all_spending_silent()
            
    def clear_all_spending_silent(self):
        """Clear all spending data without confirmation"""
        for category_data in self.app.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        self.app.update_calculations()
    
    def debug_period_data_isolation(self):
        """Comprehensive debugging for period data isolation issues"""
        
        print("\n" + "="*60)
        print("🔍 PERIOD DATA ISOLATION DEBUG")
        print("="*60)
        
        # 1. Check current application state
        current_period = getattr(self.app, '_current_period_id', 'UNKNOWN')
        current_month_id = self.app.period_manager.get_current_month_period_id()
        
        print(f"📍 Current Period ID: {current_period}")
        print(f"📅 Current Month ID: {current_month_id}")
        print(f"🏷️  Scenario: {self.app.current_scenario_name}")
        
        # 2. Check paycheck values in different places
        print(f"\n💰 PAYCHECK VALUES:")
        ui_first = self.app.first_paycheck.get()
        ui_second = self.app.second_paycheck.get()
        print(f"   UI First: ${ui_first:.2f}")
        print(f"   UI Second: ${ui_second:.2f}")
        print(f"   UI Total: ${ui_first + ui_second:.2f}")
        
        # 3. Check database values
        print(f"\n🗄️  DATABASE VALUES:")
        db_data = self.app.database.load_budget_data(self.app.current_scenario_name)
        if db_data:
            income, spending_data = db_data
            db_first = spending_data.get('first_paycheck', 'NOT_FOUND')
            db_second = spending_data.get('second_paycheck', 'NOT_FOUND')
            print(f"   DB First: ${db_first}")
            print(f"   DB Second: ${db_second}")
            print(f"   DB Total Income: ${income:.2f}")
        else:
            print("   No database data found")
        
        # 4. Check snapshots for July and August
        print(f"\n📸 SNAPSHOT DATA:")
        time_tracker = self.app.history_tab.get_time_tracker()
        
        # Check July 2025
        july_id = "monthly_2025_07"
        july_snapshot = time_tracker.get_snapshot(july_id)
        if july_snapshot:
            print(f"   July 2025: ${july_snapshot.first_paycheck:.2f} / ${july_snapshot.second_paycheck:.2f}")
            print(f"   July Total: ${july_snapshot.total_income:.2f}")
            # Show some category data
            for i, (cat, data) in enumerate(july_snapshot.category_data.items()):
                if i < 3:  # Show first 3 categories
                    print(f"     {cat}: ${data.get('actual', 0):.2f}")
        else:
            print("   July 2025: No snapshot found")
        
        # Check August 2025
        august_id = "monthly_2025_08"
        august_snapshot = time_tracker.get_snapshot(august_id)
        if august_snapshot:
            print(f"   August 2025: ${august_snapshot.first_paycheck:.2f} / ${august_snapshot.second_paycheck:.2f}")
            print(f"   August Total: ${august_snapshot.total_income:.2f}")
            # Show some category data
            for i, (cat, data) in enumerate(august_snapshot.category_data.items()):
                if i < 3:  # Show first 3 categories
                    print(f"     {cat}: ${data.get('actual', 0):.2f}")
        else:
            print("   August 2025: No snapshot found")
        
        # 5. Check current UI spending values
        print(f"\n💸 CURRENT UI SPENDING (first 5 categories):")
        for i, (category, view_data) in enumerate(self.app.actual_spending.items()):
            if i < 5:
                monthly_val = view_data[self.app.view_mode].get()
                print(f"   {category}: ${monthly_val:.2f}")
        
        # 6. Check for data corruption indicators
        print(f"\n⚠️  CORRUPTION CHECKS:")
        
        # Check if paycheck values match between UI and database
        if db_data:
            db_first = spending_data.get('first_paycheck', 0)
            db_second = spending_data.get('second_paycheck', 0)
            if abs(ui_first - db_first) > 0.01 or abs(ui_second - db_second) > 0.01:
                print("   🚨 WARNING: UI paycheck values don't match database!")
                print(f"      UI: ${ui_first:.2f} / ${ui_second:.2f}")
                print(f"      DB: ${db_first:.2f} / ${db_second:.2f}")
            else:
                print("   ✅ Paycheck values match between UI and database")
        
        # Check if current period matches what should be displayed
        if current_period == august_id and july_snapshot and august_snapshot:
            # We're viewing August but check if data looks like July
            july_total = july_snapshot.total_income
            august_total = august_snapshot.total_income
            if abs(ui_first + ui_second - july_total) < 0.01:
                print("   🚨 WARNING: Viewing August but UI shows July paycheck amounts!")
            elif abs(ui_first + ui_second - august_total) < 0.01:
                print("   ✅ August period shows correct paycheck amounts")
        
        print("="*60)
        print("🔍 END DEBUG")
    
    def save_historical_period_snapshot(self, period_id):
        """Save snapshot for historical period being edited"""
        try:
            time_tracker = self.app.history_tab.get_time_tracker()
            
            # Get existing snapshot to preserve period info
            existing_snapshot = time_tracker.get_snapshot(period_id)
            if not existing_snapshot:
                print(f"Cannot save historical period {period_id} - no existing snapshot")
                return
            
            period = existing_snapshot.period
            
            # Get current budget data
            budget_data = self.app.get_current_budget_data()
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
    
    def clear_all_spending(self):
        """Clear all spending data"""
        if messagebox.askyesno("Confirm", "Clear all actual spending data for this scenario?"):
            self.clear_all_spending_silent()
            
    def clear_all_spending_silent(self):
        """Clear all spending data without confirmation"""
        for category_data in self.app.actual_spending.values():
            for view_mode in ViewMode:
                category_data[view_mode].set(0.0)
        self.app.update_calculations()