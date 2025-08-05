# budget_app_core.py - Core application logic
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Import our separated modules
from budget_models import BudgetData, ViewMode
from budget_database import BudgetDatabase
from budget_calculator import BudgetCalculator
from budget_dashboard import BudgetDashboard
from budget_settings import BudgetSettings
from budget_history_tab import BudgetHistoryTab
from budget_time_tracker import PeriodType, BudgetSnapshot
from config import get_config

# Import our new separated UI modules
from budget_ui_controls import ControlsManager
from budget_ui_table import TableManager
from budget_ui_summary import SummaryManager
from budget_data_manager import DataManager
from budget_period_manager import PeriodManager
from budget_file_operations import FileOperations

class BudgetApp:
    """Main Budget Application Class - Now streamlined with separated concerns"""
    
    def __init__(self, root):
        self.root = root
        self.config = get_config()
        
        # Initialize core data models
        self.budget_data = BudgetData()
        self.database = BudgetDatabase(self.config.database_filename)
        
        # Initialize managers
        self.data_manager = DataManager(self)
        self.period_manager = PeriodManager(self)
        self.file_ops = FileOperations(self)
        
        # Application state
        self.current_scenario_name = self.config.default_scenario
        self.view_mode = ViewMode.MONTHLY
        
        # Set your EXACT paycheck amounts as defaults
        self.first_paycheck = tk.DoubleVar(value=2164.77)
        self.second_paycheck = tk.DoubleVar(value=2154.42)
        self.actual_spending = {}
        
        # Track loading state and current period
        self._loading_data = False
        
        # CRITICAL FIX: Set current period BEFORE creating UI
        self._current_period_id = self.period_manager.get_current_month_period_id()
        print(f"Initialized with current period: {self._current_period_id}")
        
        # Initialize UI
        self.setup_window()
        self.create_widgets()
        
        # CRITICAL FIX: Load data AFTER period is properly set
        self.data_manager.load_initial_data()
        self.period_manager.refresh_period_list()
        self.update_calculations()
        
        print(f"App initialized - Current period: {self._current_period_id}")
    
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
                self.data_manager.auto_save_data()
                print("Auto-saved data before closing")
            
            # Ask user if they want to save if auto-save is disabled
            elif messagebox.askyesno("Save Before Exit", "Do you want to save your current data before exiting?"):
                self.data_manager.save_data()
            
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
        """Create the budget overview tab using UI managers"""
        # Initialize UI managers
        self.controls_manager = ControlsManager(self.budget_frame, self)
        self.table_manager = TableManager(self.budget_frame, self)
        self.summary_manager = SummaryManager(self.budget_frame, self)
        
        # Create the UI components
        self.controls_manager.create_controls()
        self.table_manager.create_categories_table()
        self.summary_manager.create_summary_section()
    
    def update_calculations(self):
        """Update all calculations and display - DEBUG VERSION"""
        if self._loading_data:
            print("⏸️ Skipping calculations - loading data")
            return
        
        # DEBUG: Check what values we're getting
        print(f"🧮 === CALCULATION DEBUG START ===")
        
        # Check direct UI values
        ui_first = self.first_paycheck.get()
        ui_second = self.second_paycheck.get()
        print(f"🔍 Direct UI paychecks: ${ui_first:.2f} / ${ui_second:.2f}")
        
        # Check what data_manager returns
        first_paycheck, second_paycheck = self.data_manager.get_safe_paychecks()
        print(f"🔍 DataManager paychecks: ${first_paycheck:.2f} / ${second_paycheck:.2f}")
        
        # Check if they match
        if ui_first != first_paycheck or ui_second != second_paycheck:
            print("⚠️ WARNING: UI and DataManager paycheck values don't match!")
            print("⚠️ This is likely the source of your calculation problem")
        
        spending = self.data_manager.get_safe_spending()
        
        print(f"🧮 Calculating with: ${first_paycheck:.2f} + ${second_paycheck:.2f} = ${first_paycheck + second_paycheck:.2f}")
        
        # Update monthly total display
        self.controls_manager.update_monthly_total()
        
        # Get current scenario and calculator
        scenario = self.budget_data.get_scenario(self.current_scenario_name)
        calculator = BudgetCalculator(scenario)
        
        # Calculate results
        category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
        summary = calculator.calculate_summary(category_results, first_paycheck, second_paycheck, self.view_mode)
        
        # DEBUG: Check sample results
        if category_results:
            sample_category = list(category_results.keys())[0]
            sample_result = category_results[sample_category]
            print(f"🧮 Sample result for {sample_category}:")
            print(f"   Budgeted: ${sample_result.budgeted:.2f}")
            print(f"   Actual: ${sample_result.actual:.2f}")
            print(f"   Difference: ${sample_result.difference:.2f}")
            print(f"   Percentage: {sample_result.percentage:.1f}%")
            print(f"   Status: {sample_result.status}")
        
        print(f"🧮 === CALCULATION DEBUG END ===")
        
        # Update display
        self.table_manager.update_category_display(category_results)
        self.summary_manager.update_summary_display(summary)
    
    def refresh_dashboard(self):
        """Refresh dashboard charts with current data"""
        first_paycheck, second_paycheck = self.data_manager.get_safe_paychecks()
        spending = self.data_manager.get_safe_spending()
        
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
            first_paycheck, second_paycheck = self.data_manager.get_safe_paychecks()
            spending = self.data_manager.get_safe_spending()
            
            # Get current scenario and calculator
            scenario = self.budget_data.get_scenario(self.current_scenario_name)
            calculator = BudgetCalculator(scenario)
            
            # Calculate results
            category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.view_mode, spending)
            summary = calculator.calculate_summary(category_results, first_paycheck, second_paycheck, self.view_mode)
            
            return {
                'scenario_name': self.current_scenario_name,
                'first_paycheck': first_paycheck,
                'second_paycheck': second_paycheck,
                'total_income': first_paycheck + second_paycheck,
                'view_mode': self.view_mode,
                'category_results': category_results,
                'summary': summary
            }
        except Exception as e:
            print(f"Error getting current budget data: {e}")
            return None
    
    # Event handlers - delegate to appropriate managers
    def on_scenario_change(self, event=None):
        """Handle scenario change"""
        return self.data_manager.on_scenario_change(event)
    
    def on_view_change(self, event=None):
        """Handle view mode change"""
        return self.data_manager.on_view_change(event)
    
    def on_period_change(self, event=None):
        """Handle period selection change"""
        return self.period_manager.on_period_change(event)
    
    def on_paycheck_change(self):
        """Handle paycheck amount change"""
        return self.data_manager.on_paycheck_change()
    
    def on_spending_change(self, category):
        """Handle spending amount change"""
        return self.data_manager.on_spending_change(category)
    
    # File operations
    def save_data(self):
        """Save current data"""
        return self.data_manager.save_data()
    
    def export_csv(self):
        """Export to CSV"""
        return self.file_ops.export_csv()
    
    def import_from_csv(self):
        """Import from CSV"""
        return self.file_ops.import_from_csv()
    
    def manual_csv_backup(self):
        """Create manual CSV backup"""
        return self.file_ops.manual_csv_backup()
    
    def show_data_location(self):
        """Show data location"""
        return self.file_ops.show_data_location()
    
    def clear_all_spending(self):
        """Clear all spending"""
        return self.data_manager.clear_all_spending()
    
    def create_manual_period(self):
        """Create manual period"""
        return self.period_manager.create_manual_period()
    
    def debug_paycheck_values(self):
        """Debug paycheck values"""
        return self.data_manager.debug_paycheck_values()