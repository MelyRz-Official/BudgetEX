# budget_models.py
from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum

class ViewMode(Enum):
    FIRST_PAYCHECK = "First Paycheck"
    SECOND_PAYCHECK = "Second Paycheck"
    MONTHLY = "Monthly"

class CategoryType(Enum):
    FIXED_DOLLAR = "fixed_dollar"      # Amount stays same (HOA, Utilities)
    FIXED_PERCENTAGE = "fixed_percentage"  # Percentage stays same (Roth IRA, Savings)

class CategoryGroup(Enum):
    SAVINGS = "savings"     # Over budget is good
    EXPENSE = "expense"     # Over budget is bad

@dataclass
class BudgetCategory:
    name: str
    monthly_amount: float
    percentage: float
    category_type: CategoryType
    category_group: CategoryGroup
    
    def calculate_budgeted_amount(self, first_paycheck: float, second_paycheck: float, view_mode: ViewMode) -> tuple[float, float]:
        """
        Calculate budgeted amount and percentage for given paychecks and view mode.
        Returns (budgeted_amount, percentage)
        """
        monthly_income = first_paycheck + second_paycheck
        
        if self.category_type == CategoryType.FIXED_DOLLAR:
            # Fixed dollar amount - split 50/50 for paycheck views
            if view_mode == ViewMode.MONTHLY:
                budgeted = self.monthly_amount
                percentage = (budgeted / monthly_income * 100) if monthly_income > 0 else 0
            else:  # First or Second Paycheck
                budgeted = self.monthly_amount / 2  # Split fixed expenses 50/50
                current_paycheck = first_paycheck if view_mode == ViewMode.FIRST_PAYCHECK else second_paycheck
                percentage = (budgeted / current_paycheck * 100) if current_paycheck > 0 else 0
        else:  # FIXED_PERCENTAGE
            # Fixed percentage
            percentage = self.percentage
            if view_mode == ViewMode.MONTHLY:
                budgeted = (percentage / 100) * monthly_income
            elif view_mode == ViewMode.FIRST_PAYCHECK:
                budgeted = (percentage / 100) * first_paycheck
            else:  # SECOND_PAYCHECK
                budgeted = (percentage / 100) * second_paycheck
        
        return budgeted, percentage
    
    def get_status_and_color(self, budgeted: float, actual: float) -> tuple[str, str]:
        """
        Get status text and color based on budgeted vs actual amounts.
        Returns (status_text, color)
        """
        if actual == 0:
            return "Not Set", "gray"
        
        difference = budgeted - actual
        
        if self.category_group == CategoryGroup.SAVINGS:
            # For savings, spending more is better
            if difference == 0:
                return "On Target", "cyan"
            elif difference > 0:
                return "Under Goal", "orange"
            else:  # actual > budgeted
                return "Exceeding Goal!", "green"
        else:  # EXPENSE
            # For expenses, spending less is better
            if difference == 0:
                return "On Target", "cyan"
            elif difference > 0:
                return "Under Budget", "green"
            else:  # actual > budgeted
                return "Over Budget", "red"

class BudgetScenario:
    def __init__(self, name: str, categories: Dict[str, BudgetCategory]):
        self.name = name
        self.categories = categories
    
    def get_category(self, category_name: str) -> BudgetCategory:
        return self.categories[category_name]
    
    def get_all_categories(self) -> Dict[str, BudgetCategory]:
        return self.categories

class BudgetData:
    """Manages all budget scenarios and calculations"""
    
    def __init__(self):
        self.scenarios = self._create_scenarios()
    
    def _create_scenarios(self) -> Dict[str, BudgetScenario]:
        """Create all budget scenarios with their categories"""
        
        # July-December 2025 scenario (Vacation Fund removed, redistributed to Groceries and Dining)
        july_dec_categories = {
            "Roth IRA": BudgetCategory(
                "Roth IRA", 333.33, 8.4, 
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "General Savings": BudgetCategory(
                "General Savings", 769.23, 19.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "HOA": BudgetCategory(
                "HOA", 1078.81, 27.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Utilities": BudgetCategory(
                "Utilities", 150.00, 3.8,  # Updated to $150
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Subscriptions": BudgetCategory(
                "Subscriptions", 60.00, 1.5,  # Updated to $60
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Groceries": BudgetCategory(
                "Groceries", 550.00, 13.8,  # Increased from 7.5% to 13.75% (rounded to 13.8%)
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Uber/Lyft": BudgetCategory(
                "Uber/Lyft", 70.00, 1.8,  # Updated to $70
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Therapy": BudgetCategory(
                "Therapy", 44.00, 1.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Dining/Entertainment": BudgetCategory(
                "Dining/Entertainment", 400.00, 10.0,  # Increased from 3.8% to 10.05% (rounded to 10.0%)
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Flex/Buffer": BudgetCategory(
                "Flex/Buffer", 535.14, 13.4,  # Remains same to maintain 100% total
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
        }
        
        # Fresh New Year (Jan-May) scenario (Vacation Fund removed, redistributed)
        jan_may_categories = {
            "Roth IRA": BudgetCategory(
                "Roth IRA", 1400.00, 35.2,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "General Savings": BudgetCategory(
                "General Savings", 250.00, 6.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "HOA": BudgetCategory(
                "HOA", 1078.81, 27.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Utilities": BudgetCategory(
                "Utilities", 150.00, 3.8,  # Updated to $150
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Subscriptions": BudgetCategory(
                "Subscriptions", 60.00, 1.5,  # Updated to $60
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Groceries": BudgetCategory(
                "Groceries", 324.50, 8.1,  # Increased from 7.5% to 8.15% (rounded to 8.1%)
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Uber/Lyft": BudgetCategory(
                "Uber/Lyft", 70.00, 1.8,  # Updated to $70
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Dining/Entertainment": BudgetCategory(
                "Dining/Entertainment", 178.00, 4.5,  # Increased from 3.8% to 4.45% (rounded to 4.5%)
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Therapy": BudgetCategory(
                "Therapy", 44.00, 1.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Flex/Buffer": BudgetCategory(
                "Flex/Buffer", 50.94, 1.3,  # Adjusted to make total = 100%
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
        }
        
        # Fresh New Year (June-Dec) scenario (Vacation Fund removed, redistributed)
        june_dec_categories = {
            "Roth IRA": BudgetCategory(
                "Roth IRA", 0.00, 0.0,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "General Savings": BudgetCategory(
                "General Savings", 833.33, 20.9,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "HOA": BudgetCategory(
                "HOA", 1078.81, 27.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Utilities": BudgetCategory(
                "Utilities", 150.00, 3.8,  # Updated to $150
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Subscriptions": BudgetCategory(
                "Subscriptions", 60.00, 1.5,  # Updated to $60
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Groceries": BudgetCategory(
                "Groceries", 450.00, 11.3,  # Increased from 7.5% to 11.25% (rounded to 11.3%)
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Uber/Lyft": BudgetCategory(
                "Uber/Lyft", 70.00, 1.8,  # Updated to $70
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Dining/Entertainment": BudgetCategory(
                "Dining/Entertainment", 302.00, 7.6,  # Increased from 3.8% to 7.55% (rounded to 7.6%)
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Therapy": BudgetCategory(
                "Therapy", 44.00, 1.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Flex/Buffer": BudgetCategory(
                "Flex/Buffer", 817.61, 20.5,  # Adjusted to make total = 100%
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
        }
        
        return {
            "July-December 2025": BudgetScenario("July-December 2025", july_dec_categories),
            "Fresh New Year (Jan-May)": BudgetScenario("Fresh New Year (Jan-May)", jan_may_categories),
            "Fresh New Year (June-Dec)": BudgetScenario("Fresh New Year (June-Dec)", june_dec_categories),
        }
    
    def get_scenario(self, scenario_name: str) -> BudgetScenario:
        return self.scenarios[scenario_name]
    
    def get_scenario_names(self) -> list[str]:
        return list(self.scenarios.keys())