"""
Budget controller implementing the Controller layer of MVC pattern.
Manages communication between the model and views, handles user interactions.
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import threading
from models.budget_model import BudgetModel
from config import ConfigManager, get_config, save_config, update_config


class BudgetController:
    """
    Main controller for the budget application.
    Coordinates between model and views, handles business logic flow.
    """
    
    def __init__(self, model: BudgetModel, config_manager: ConfigManager = None):
        """
        Initialize the budget controller.
        
        Args:
            model: Budget model instance.
            config_manager: Configuration manager instance.
        """
        self.model = model
        self.config_manager = config_manager or ConfigManager()
        self.config = get_config()
        
        # View references (will be set by views)
        self.views = {}
        
        # Event callbacks for views to subscribe to
        self.callbacks = {
            'scenario_changed': [],
            'paycheck_changed': [],
            'spending_changed': [],
            'data_saved': [],
            'data_loaded': [],
            'config_changed': []
        }
        
        # Auto-save timer
        self._auto_save_timer = None
        self._auto_save_pending = False
    
    def register_view(self, view_name: str, view_instance) -> None:
        """
        Register a view with the controller.
        
        Args:
            view_name: Name identifier for the view.
            view_instance: View instance to register.
        """
        self.views[view_name] = view_instance
    
    def subscribe_to_event(self, event_name: str, callback: Callable) -> None:
        """
        Subscribe a callback to an event.
        
        Args:
            event_name: Name of the event.
            callback: Function to call when event occurs.
        """
        if event_name in self.callbacks:
            self.callbacks[event_name].append(callback)
    
    def _emit_event(self, event_name: str, data: Any = None) -> None:
        """
        Emit an event to all subscribed callbacks.
        
        Args:
            event_name: Name of the event.
            data: Optional data to pass to callbacks.
        """
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event callback for {event_name}: {e}")
    
    # Scenario Management
    def get_available_scenarios(self) -> List[str]:
        """Get list of available budget scenarios."""
        return self.model.get_scenario_names()
    
    def get_current_scenario_name(self) -> str:
        """Get name of current active scenario."""
        return self.model.current_scenario_name
    
    def switch_scenario(self, scenario_name: str) -> bool:
        """
        Switch to a different budget scenario.
        
        Args:
            scenario_name: Name of scenario to switch to.
            
        Returns:
            bool: True if successful.
        """
        if self.model.set_current_scenario(scenario_name):
            self._emit_event('scenario_changed', {
                'scenario_name': scenario_name,
                'paycheck_amount': self.model.current_paycheck,
                'spending_data': self.model.actual_spending
            })
            return True
        return False
    
    # Paycheck Management
    def get_paycheck_amount(self) -> float:
        """Get current paycheck amount."""
        return self.model.current_paycheck
    
    def set_paycheck_amount(self, amount: float) -> bool:
        """
        Set paycheck amount with validation.
        
        Args:
            amount: New paycheck amount.
            
        Returns:
            bool: True if valid and set successfully.
        """
        try:
            amount = float(amount)
            if amount <= 0:
                return False
            
            if self.model.set_paycheck_amount(amount):
                self._emit_event('paycheck_changed', {
                    'amount': amount,
                    'summary': self.get_budget_summary()
                })
                
                # Auto-save if enabled
                if self.config.auto_save:
                    self._schedule_auto_save()
                
                return True
        except ValueError:
            pass
        
        return False
    
    # Spending Management
    def get_actual_spending(self, category: str) -> float:
        """
        Get actual spending for a category.
        
        Args:
            category: Category name.
            
        Returns:
            Actual spending amount.
        """
        return self.model.get_actual_spending(category)
    
    def set_actual_spending(self, category: str, amount: float) -> bool:
        """
        Set actual spending for a category with validation.
        
        Args:
            category: Category name.
            amount: Spending amount.
            
        Returns:
            bool: True if valid and set successfully.
        """
        try:
            amount = float(amount)
            if amount < 0:
                return False
            
            if self.model.set_actual_spending(category, amount):
                self._emit_event('spending_changed', {
                    'category': category,
                    'amount': amount,
                    'summary': self.get_budget_summary()
                })
                
                # Auto-save if enabled
                if self.config.auto_save:
                    self._schedule_auto_save()
                
                return True
        except ValueError:
            pass
        
        return False
    
    def clear_all_spending(self) -> bool:
        """
        Clear all actual spending data.
        
        Returns:
            bool: True if successful.
        """
        if self.model.clear_all_spending():
            self._emit_event('spending_changed', {
                'category': 'all',
                'amount': 0.0,
                'summary': self.get_budget_summary()
            })
            return True
        return False
    
    # Budget Calculations
    def get_budget_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive budget summary with all calculations.
        
        Returns:
            Dictionary with budget summary data.
        """
        return self.model.calculate_budget_summary()
    
    def get_category_data(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed data for a specific category.
        
        Args:
            category: Category name.
            
        Returns:
            Category data dictionary or None if not found.
        """
        summary = self.get_budget_summary()
        return summary['categories'].get(category)
    
    def validate_current_budget(self) -> List[str]:
        """
        Validate current budget scenario.
        
        Returns:
            List of validation error messages.
        """
        summary = self.get_budget_summary()
        return summary.get('validation_errors', [])
    
    # Data Persistence
    def save_data(self, show_message: bool = True) -> bool:
        """
        Save current budget data to database.
        
        Args:
            show_message: Whether to emit save event (for UI feedback).
            
        Returns:
            bool: True if successful.
        """
        success = self.model.save_scenario_data()
        
        if success:
            # Create backup if enabled
            if self.config.auto_backup:
                self.model.backup_data()
            
            if show_message:
                self._emit_event('data_saved', {
                    'scenario': self.model.current_scenario_name,
                    'timestamp': datetime.now()
                })
        
        return success
    
    def load_data(self, scenario_name: str = None) -> bool:
        """
        Load budget data for a scenario.
        
        Args:
            scenario_name: Scenario to load (current if None).
            
        Returns:
            bool: True if data was found and loaded.
        """
        if scenario_name is None:
            scenario_name = self.model.current_scenario_name
        
        success = self.model.load_scenario_data(scenario_name)
        
        if success:
            self._emit_event('data_loaded', {
                'scenario': scenario_name,
                'paycheck_amount': self.model.current_paycheck,
                'spending_data': self.model.actual_spending
            })
        
        return success
    
    def _schedule_auto_save(self) -> None:
        """Schedule an auto-save operation."""
        if self._auto_save_timer:
            self._auto_save_timer.cancel()
        
        # Auto-save after 2 seconds of inactivity
        self._auto_save_timer = threading.Timer(2.0, self._perform_auto_save)
        self._auto_save_timer.start()
        self._auto_save_pending = True
    
    def _perform_auto_save(self) -> None:
        """Perform the actual auto-save operation."""
        if self._auto_save_pending:
            self.save_data(show_message=False)  # Silent save for auto-save
            self._auto_save_pending = False
    
    # Configuration Management
    def get_config(self) -> Any:
        """Get current configuration."""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """
        Update configuration settings.
        
        Args:
            **kwargs: Configuration key-value pairs.
            
        Returns:
            bool: True if successful.
        """
        try:
            update_config(**kwargs)
            self.config = get_config()  # Refresh local config
            
            self._emit_event('config_changed', {
                'changes': kwargs,
                'new_config': self.config
            })
            
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            bool: True if successful.
        """
        return save_config()
    
    # Export/Import Operations
    def export_to_csv(self, file_path: str = None, scenario_name: str = None) -> Optional[str]:
        """
        Export budget data to CSV format.
        
        Args:
            file_path: Output file path (auto-generated if None).
            scenario_name: Scenario to export (current if None).
            
        Returns:
            File path if successful, None otherwise.
        """
        try:
            if scenario_name is None:
                scenario_name = self.model.current_scenario_name
            
            export_data = self.model.export_scenario_data(scenario_name)
            
            if file_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"budget_export_{scenario_name.replace(' ', '_')}_{timestamp}.csv"
            
            # Write CSV data
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                writer.writerow([
                    'Category', 'Percentage', 'Budgeted Amount', 
                    'Actual Spent', 'Difference', 'Status', 'Is Fixed', 'Description'
                ])
                
                # Write category data
                for cat_data in export_data['categories']:
                    writer.writerow([
                        cat_data['category'],
                        f"{cat_data['percentage']:.1f}%",
                        f"{cat_data['budgeted_amount']:.2f}",
                        f"{cat_data['actual_spent']:.2f}",
                        f"{cat_data['difference']:.2f}",
                        cat_data['status'],
                        'Yes' if cat_data['is_fixed'] else 'No',
                        cat_data['description']
                    ])
                
                # Write summary
                writer.writerow([])  # Empty row
                writer.writerow(['SUMMARY'])
                summary = export_data['summary']
                writer.writerow(['Total Budgeted', f"{summary['total_budgeted']:.2f}"])
                writer.writerow(['Total Spent', f"{summary['total_spent']:.2f}"])
                writer.writerow(['Remaining', f"{summary['remaining']:.2f}"])
                writer.writerow(['Over/Under', f"{summary['over_under']:.2f}"])
            
            return file_path
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return None
    
    def get_spending_trends(self, category: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get spending trends for analysis.
        
        Args:
            category: Specific category (all if None).
            days: Number of days to analyze.
            
        Returns:
            List of spending trend data.
        """
        return self.model.get_spending_trends(category, days)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return self.model.get_database_stats()
    
    def backup_database(self, backup_path: str = None) -> bool:
        """
        Create a database backup.
        
        Args:
            backup_path: Custom backup path (auto-generated if None).
            
        Returns:
            bool: True if successful.
        """
        return self.model.backup_data(backup_path)
    
    def get_category_suggestions(self) -> List[str]:
        """Get suggestions for new budget categories."""
        return self.model.get_category_suggestions()
    
    def cleanup(self) -> None:
        """Cleanup controller resources."""
        # Cancel any pending auto-save
        if self._auto_save_timer:
            self._auto_save_timer.cancel()
        
        # Perform final save if pending
        if self._auto_save_pending:
            self.save_data(show_message=False)


# Example usage and testing
if __name__ == "__main__":
    print("Budget Controller Demo")
    print("-" * 50)
    
    # Initialize model and controller
    from models.budget_model import BudgetModel
    
    model = BudgetModel("test_controller.db")
    controller = BudgetController(model)
    
    # Test basic operations
    print(f"Available scenarios: {controller.get_available_scenarios()}")
    print(f"Current scenario: {controller.get_current_scenario_name()}")
    
    # Test paycheck setting
    success = controller.set_paycheck_amount(4000.0)
    print(f"Set paycheck to $4000: {'Success' if success else 'Failed'}")
    
    # Test spending operations
    controller.set_actual_spending("Groceries", 250.0)
    controller.set_actual_spending("Utilities", 65.0)
    
    # Get summary
    summary = controller.get_budget_summary()
    print(f"\nBudget Summary:")
    print(f"Total budgeted: ${summary['totals']['total_budgeted']:.2f}")
    print(f"Total spent: ${summary['totals']['total_spent']:.2f}")
    
    # Test export
    export_file = controller.export_to_csv()
    print(f"Exported to: {export_file}")
    
    # Cleanup
    controller.cleanup()
    import os
    if export_file and os.path.exists(export_file):
        os.unlink(export_file)
    os.unlink("test_controller.db")
    print("\nTest completed and cleaned up!")