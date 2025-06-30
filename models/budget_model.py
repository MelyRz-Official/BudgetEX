"""
Budget model containing business logic and data structures for the Budget Manager.
Handles budget calculations, scenario management, and data validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from .database_manager import DatabaseManager


@dataclass
class BudgetCategory:
    """Represents a single budget category with its properties."""
    
    name: str
    amount: float
    percentage: float
    fixed_amount: bool = False
    description: str = ""
    
    def calculate_budgeted_amount(self, paycheck: float) -> float:
        """
        Calculate the budgeted amount for this category.
        
        Args:
            paycheck: Total paycheck amount.
            
        Returns:
            Calculated budget amount.
        """
        if self.fixed_amount:
            return self.amount
        else:
            return (self.percentage / 100) * paycheck
    
    def calculate_percentage(self, paycheck: float) -> float:
        """
        Calculate the percentage for this category.
        
        Args:
            paycheck: Total paycheck amount.
            
        Returns:
            Calculated percentage.
        """
        if self.fixed_amount and paycheck > 0:
            return (self.amount / paycheck) * 100
        else:
            return self.percentage


@dataclass
class BudgetScenario:
    """Represents a complete budget scenario with all categories."""
    
    name: str
    categories: Dict[str, BudgetCategory]
    default_paycheck: float = 0.0
    description: str = ""
    
    def get_total_fixed_amount(self) -> float:
        """Get total amount of all fixed categories."""
        return sum(
            cat.amount for cat in self.categories.values() 
            if cat.fixed_amount
        )
    
    def get_total_percentage(self) -> float:
        """Get total percentage of all percentage-based categories."""
        return sum(
            cat.percentage for cat in self.categories.values() 
            if not cat.fixed_amount
        )
    
    def validate_scenario(self, paycheck: float) -> List[str]:
        """
        Validate the budget scenario for a given paycheck.
        
        Args:
            paycheck: Paycheck amount to validate against.
            
        Returns:
            List of validation error messages.
        """
        errors = []
        
        if paycheck <= 0:
            errors.append("Paycheck amount must be positive")
            return errors
        
        total_fixed = self.get_total_fixed_amount()
        if total_fixed > paycheck:
            errors.append(f"Fixed expenses (${total_fixed:.2f}) exceed paycheck (${paycheck:.2f})")
        
        total_percentage = self.get_total_percentage()
        if total_percentage > 100:
            errors.append(f"Total percentages ({total_percentage:.1f}%) exceed 100%")
        
        # Check if total budget exceeds paycheck
        total_budgeted = sum(
            cat.calculate_budgeted_amount(paycheck) 
            for cat in self.categories.values()
        )
        
        if total_budgeted > paycheck:
            errors.append(f"Total budget (${total_budgeted:.2f}) exceeds paycheck (${paycheck:.2f})")
        
        return errors


class BudgetModel:
    """Main model class containing all budget logic and data management."""
    
    def __init__(self, db_path: str = "budget_data.db"):
        """
        Initialize budget model.
        
        Args:
            db_path: Path to the database file.
        """
        self.db = DatabaseManager(db_path)
        self.scenarios = self._initialize_scenarios()
        self.current_scenario_name = "July-December 2025"
        self.current_paycheck = 3984.94
        self.actual_spending: Dict[str, float] = {}
        
        # Load saved data
        self.load_scenario_data(self.current_scenario_name)
    
    def _initialize_scenarios(self) -> Dict[str, BudgetScenario]:
        """Initialize predefined budget scenarios."""
        scenarios = {}
        
        # July-December 2025 scenario
        july_dec_categories = {
            "Roth IRA": BudgetCategory("Roth IRA", 333.33, 8.4, False, "Retirement savings"),
            "General Savings": BudgetCategory("General Savings", 769.23, 19.3, False, "Emergency fund"),
            "Vacation Fund": BudgetCategory("Vacation Fund", 500.00, 12.5, False, "Travel savings"),
            "HOA": BudgetCategory("HOA", 1078.81, 27.1, True, "Housing association fees"),
            "Utilities": BudgetCategory("Utilities", 60.00, 1.5, True, "Water, electric, gas"),
            "Subscriptions": BudgetCategory("Subscriptions", 90.00, 2.3, True, "Netflix, Spotify, etc."),
            "Groceries": BudgetCategory("Groceries", 300.00, 7.5, False, "Food and household items"),
            "Uber/Lyft": BudgetCategory("Uber/Lyft", 50.00, 1.3, False, "Transportation"),
            "Therapy": BudgetCategory("Therapy", 44.00, 1.1, True, "Mental health"),
            "Dining/Entertainment": BudgetCategory("Dining/Entertainment", 150.00, 3.8, False, "Fun activities"),
            "Flex/Buffer": BudgetCategory("Flex/Buffer", 657.38, 16.5, False, "Flexible spending")
        }
        
        scenarios["July-December 2025"] = BudgetScenario(
            "July-December 2025", 
            july_dec_categories, 
            3984.94,
            "Current year budget plan"
        )
        
        # Fresh New Year (Jan-May) scenario
        jan_may_categories = {
            "Roth IRA": BudgetCategory("Roth IRA", 1400.00, 35.2, False, "Max out early"),
            "General Savings": BudgetCategory("General Savings", 250.00, 6.3, False, "Emergency fund"),
            "Vacation Fund": BudgetCategory("Vacation Fund", 50.00, 1.3, False, "Travel savings"),
            "HOA": BudgetCategory("HOA", 1078.81, 27.1, True, "Housing association fees"),
            "Utilities": BudgetCategory("Utilities", 60.00, 1.5, True, "Water, electric, gas"),
            "Subscriptions": BudgetCategory("Subscriptions", 90.00, 2.3, True, "Netflix, Spotify, etc."),
            "Groceries": BudgetCategory("Groceries", 300.00, 7.5, False, "Food and household items"),
            "Uber/Lyft": BudgetCategory("Uber/Lyft", 50.00, 1.3, False, "Transportation"),
            "Dining/Entertainment": BudgetCategory("Dining/Entertainment", 150.00, 3.8, False, "Fun activities"),
            "Therapy": BudgetCategory("Therapy", 44.00, 1.1, True, "Mental health"),
            "Flex/Buffer": BudgetCategory("Flex/Buffer", 90.94, 2.3, False, "Flexible spending")
        }
        
        scenarios["Fresh New Year (Jan-May)"] = BudgetScenario(
            "Fresh New Year (Jan-May)", 
            jan_may_categories, 
            3984.94,
            "High IRA contribution period"
        )
        
        # Fresh New Year (June-Dec) scenario
        june_dec_categories = {
            "Roth IRA": BudgetCategory("Roth IRA", 0.00, 0.0, False, "Already maxed out"),
            "General Savings": BudgetCategory("General Savings", 833.33, 20.9, False, "Emergency fund"),
            "Vacation Fund": BudgetCategory("Vacation Fund", 300.00, 7.5, False, "Travel savings"),
            "HOA": BudgetCategory("HOA", 1078.81, 27.1, True, "Housing association fees"),
            "Utilities": BudgetCategory("Utilities", 60.00, 1.5, True, "Water, electric, gas"),
            "Subscriptions": BudgetCategory("Subscriptions", 90.00, 2.3, True, "Netflix, Spotify, etc."),
            "Groceries": BudgetCategory("Groceries", 300.00, 7.5, False, "Food and household items"),
            "Uber/Lyft": BudgetCategory("Uber/Lyft", 50.00, 1.3, False, "Transportation"),
            "Dining/Entertainment": BudgetCategory("Dining/Entertainment", 150.00, 3.8, False, "Fun activities"),
            "Therapy": BudgetCategory("Therapy", 44.00, 1.1, True, "Mental health"),
            "Flex/Buffer": BudgetCategory("Flex/Buffer", 857.61, 21.5, False, "Flexible spending")
        }
        
        scenarios["Fresh New Year (June-Dec)"] = BudgetScenario(
            "Fresh New Year (June-Dec)", 
            june_dec_categories, 
            3984.94,
            "Post-IRA max-out period"
        )
        
        return scenarios
    
    def get_scenario_names(self) -> List[str]:
        """Get list of all available scenario names."""
        return list(self.scenarios.keys())
    
    def get_current_scenario(self) -> BudgetScenario:
        """Get the currently active budget scenario."""
        return self.scenarios[self.current_scenario_name]
    
    def set_current_scenario(self, scenario_name: str) -> bool:
        """
        Set the current active scenario.
        
        Args:
            scenario_name: Name of the scenario to activate.
            
        Returns:
            bool: True if successful, False if scenario doesn't exist.
        """
        if scenario_name in self.scenarios:
            # Save current data before switching
            self.save_scenario_data()
            
            self.current_scenario_name = scenario_name
            self.load_scenario_data(scenario_name)
            return True
        return False
    
    def set_paycheck_amount(self, amount: float) -> bool:
        """
        Set the current paycheck amount.
        
        Args:
            amount: New paycheck amount.
            
        Returns:
            bool: True if valid amount.
        """
        if amount > 0:
            self.current_paycheck = amount
            return True
        return False
    
    def set_actual_spending(self, category: str, amount: float) -> bool:
        """
        Set actual spending for a category.
        
        Args:
            category: Category name.
            amount: Amount spent.
            
        Returns:
            bool: True if category exists and amount is valid.
        """
        scenario = self.get_current_scenario()
        if category in scenario.categories and amount >= 0:
            self.actual_spending[category] = amount
            return True
        return False
    
    def get_actual_spending(self, category: str) -> float:
        """
        Get actual spending for a category.
        
        Args:
            category: Category name.
            
        Returns:
            Actual spending amount (0.0 if not set).
        """
        return self.actual_spending.get(category, 0.0)
    
    def calculate_budget_summary(self) -> Dict[str, Any]:
        """
        Calculate comprehensive budget summary.
        
        Returns:
            Dictionary with budget calculations and statistics.
        """
        scenario = self.get_current_scenario()
        summary = {
            'scenario_name': self.current_scenario_name,
            'paycheck_amount': self.current_paycheck,
            'categories': {},
            'totals': {},
            'validation_errors': []
        }
        
        total_budgeted = 0
        total_spent = 0
        
        # Calculate per-category data
        for cat_name, category in scenario.categories.items():
            budgeted = category.calculate_budgeted_amount(self.current_paycheck)
            actual = self.get_actual_spending(cat_name)
            difference = budgeted - actual
            percentage = category.calculate_percentage(self.current_paycheck)
            
            total_budgeted += budgeted
            total_spent += actual
            
            # Determine status
            if actual == 0:
                status = "not_set"
            elif difference > 0:
                status = "under_budget"
            elif difference < 0:
                status = "over_budget"
            else:
                status = "on_target"
            
            summary['categories'][cat_name] = {
                'budgeted_amount': budgeted,
                'actual_spent': actual,
                'difference': difference,
                'percentage': percentage,
                'status': status,
                'is_fixed': category.fixed_amount,
                'description': category.description
            }
        
        # Calculate totals
        remaining = self.current_paycheck - total_spent
        over_under = total_spent - total_budgeted
        
        summary['totals'] = {
            'total_budgeted': total_budgeted,
            'total_spent': total_spent,
            'remaining': remaining,
            'over_under': over_under,
            'budget_utilization': (total_spent / self.current_paycheck) * 100 if self.current_paycheck > 0 else 0
        }
        
        # Add validation errors
        summary['validation_errors'] = scenario.validate_scenario(self.current_paycheck)
        
        return summary
    
    def clear_all_spending(self) -> bool:
        """
        Clear all actual spending data for current scenario.
        
        Returns:
            bool: True if successful.
        """
        self.actual_spending = {}
        return self.db.clear_spending_data(self.current_scenario_name)
    
    def save_scenario_data(self) -> bool:
        """
        Save current scenario data to database.
        
        Returns:
            bool: True if successful.
        """
        return self.db.save_budget_data(
            self.current_scenario_name,
            self.current_paycheck,
            self.actual_spending
        )
    
    def load_scenario_data(self, scenario_name: str) -> bool:
        """
        Load scenario data from database.
        
        Args:
            scenario_name: Name of scenario to load.
            
        Returns:
            bool: True if data was loaded.
        """
        result = self.db.load_budget_data(scenario_name)
        if result:
            paycheck, spending_data = result
            self.current_paycheck = paycheck
            
            # Initialize actual spending for all categories
            scenario = self.scenarios[scenario_name]
            self.actual_spending = {}
            for category_name in scenario.categories:
                self.actual_spending[category_name] = spending_data.get(category_name, 0.0)
            
            return True
        else:
            # Initialize with zeros if no saved data
            scenario = self.scenarios[scenario_name]
            self.actual_spending = {cat: 0.0 for cat in scenario.categories}
            return False
    
    def export_scenario_data(self, scenario_name: str = None) -> Dict[str, Any]:
        """
        Export scenario data for external use (CSV, reports, etc.).
        
        Args:
            scenario_name: Scenario to export (current if None).
            
        Returns:
            Dictionary with exportable data.
        """
        if scenario_name is None:
            scenario_name = self.current_scenario_name
        
        # Temporarily switch to requested scenario for export
        original_scenario = self.current_scenario_name
        if scenario_name != original_scenario:
            temp_paycheck = self.current_paycheck
            temp_spending = self.actual_spending.copy()
            self.set_current_scenario(scenario_name)
        
        try:
            summary = self.calculate_budget_summary()
            export_data = {
                'metadata': {
                    'scenario_name': scenario_name,
                    'export_date': datetime.now().isoformat(),
                    'paycheck_amount': self.current_paycheck
                },
                'categories': [],
                'summary': summary['totals']
            }
            
            # Format category data for export
            for cat_name, cat_data in summary['categories'].items():
                export_data['categories'].append({
                    'category': cat_name,
                    'percentage': cat_data['percentage'],
                    'budgeted_amount': cat_data['budgeted_amount'],
                    'actual_spent': cat_data['actual_spent'],
                    'difference': cat_data['difference'],
                    'status': cat_data['status'],
                    'is_fixed': cat_data['is_fixed'],
                    'description': cat_data['description']
                })
            
            return export_data
            
        finally:
            # Restore original scenario if we switched
            if scenario_name != original_scenario:
                self.current_scenario_name = original_scenario
                self.current_paycheck = temp_paycheck
                self.actual_spending = temp_spending
    
    def get_spending_trends(self, category: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get spending trends from history.
        
        Args:
            category: Specific category (all if None).
            days: Number of days to analyze.
            
        Returns:
            List of spending trend data.
        """
        return self.db.get_spending_history(self.current_scenario_name, category, days)
    
    def add_spending_transaction(self, category: str, amount: float, description: str = None) -> bool:
        """
        Add a spending transaction to history and update actual spending.
        
        Args:
            category: Category name.
            amount: Transaction amount.
            description: Optional description.
            
        Returns:
            bool: True if successful.
        """
        if self.set_actual_spending(category, self.get_actual_spending(category) + amount):
            return self.db.add_spending_history(
                self.current_scenario_name, category, amount, description
            )
        return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return self.db.get_database_stats()
    
    def backup_data(self, backup_path: str = None) -> bool:
        """
        Create a backup of all budget data.
        
        Args:
            backup_path: Custom backup path (auto-generated if None).
            
        Returns:
            bool: True if successful.
        """
        return self.db.backup_database(backup_path)
    
    def validate_all_scenarios(self) -> Dict[str, List[str]]:
        """
        Validate all budget scenarios.
        
        Returns:
            Dictionary mapping scenario names to validation errors.
        """
        validation_results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            validation_results[scenario_name] = scenario.validate_scenario(scenario.default_paycheck)
        
        return validation_results
    
    def get_category_suggestions(self) -> List[str]:
        """
        Get suggestions for new budget categories based on spending history.
        
        Returns:
            List of suggested category names.
        """
        # This could be enhanced with ML in the future
        common_categories = [
            "Medical/Healthcare",
            "Car Payment", 
            "Car Insurance",
            "Phone Bill",
            "Internet",
            "Clothing",
            "Gifts",
            "Home Maintenance",
            "Personal Care",
            "Pet Expenses",
            "Education",
            "Charity/Donations"
        ]
        
        # Filter out categories that already exist
        current_categories = set(self.get_current_scenario().categories.keys())
        suggestions = [cat for cat in common_categories if cat not in current_categories]
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def __del__(self):
        """Cleanup when model is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()


# Example usage and testing
if __name__ == "__main__":
    print("Budget Model Demo")
    print("-" * 50)
    
    # Initialize model
    model = BudgetModel("test_budget_model.db")
    
    # Test basic operations
    print(f"Available scenarios: {model.get_scenario_names()}")
    print(f"Current scenario: {model.current_scenario_name}")
    
    # Set some spending
    model.set_actual_spending("Groceries", 275.50)
    model.set_actual_spending("Utilities", 65.00)
    
    # Get budget summary
    summary = model.calculate_budget_summary()
    print(f"\nBudget Summary:")
    print(f"Total budgeted: ${summary['totals']['total_budgeted']:.2f}")
    print(f"Total spent: ${summary['totals']['total_spent']:.2f}")
    print(f"Remaining: ${summary['totals']['remaining']:.2f}")
    
    # Test scenario switching
    model.set_current_scenario("Fresh New Year (Jan-May)")
    print(f"\nSwitched to: {model.current_scenario_name}")
    
    # Export data
    export_data = model.export_scenario_data()
    print(f"Export data has {len(export_data['categories'])} categories")
    
    # Cleanup
    import os
    os.unlink("test_budget_model.db")
    print("\nTest completed and cleaned up!")