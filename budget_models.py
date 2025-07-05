# budget_models.py
from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum

class ViewMode(Enum):
    MONTHLY = "Monthly"
    PER_PAYCHECK = "Per-Paycheck"

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
    
    def calculate_budgeted_amount(self, income: float, view_mode: ViewMode) -> tuple[float, float]:
        """
        Calculate budgeted amount and percentage for given income and view mode.
        Returns (budgeted_amount, percentage)
        """
        if self.category_type == CategoryType.FIXED_DOLLAR:
            # Fixed dollar amount
            if view_mode == ViewMode.MONTHLY:
                budgeted = self.monthly_amount
                percentage = (budgeted / income * 100) if income > 0 else 0
            else:  # PER_PAYCHECK
                budgeted = self.monthly_amount / 2
                percentage = (budgeted / income * 100) if income > 0 else 0
        else:  # FIXED_PERCENTAGE
            # Fixed percentage
            percentage = self.percentage
            if view_mode == ViewMode.MONTHLY:
                budgeted = (percentage / 100) * income
            else:  # PER_PAYCHECK
                # Calculate based on monthly income (paycheck * 2) then divide by 2
                monthly_income = income * 2
                monthly_budgeted = (percentage / 100) * monthly_income
                budgeted = monthly_budgeted / 2
        
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
                return "On Target", "blue"
            elif difference > 0:
                return "Under Goal", "orange"
            else:  # actual > budgeted
                return "Exceeding Goal!", "green"
        else:  # EXPENSE
            # For expenses, spending less is better
            if difference == 0:
                return "On Target", "blue"
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
        
        # July-December 2025 scenario
        july_dec_categories = {
            "Roth IRA": BudgetCategory(
                "Roth IRA", 333.33, 8.4, 
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "General Savings": BudgetCategory(
                "General Savings", 769.23, 19.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "Vacation Fund": BudgetCategory(
                "Vacation Fund", 500.00, 12.5,
                CategoryType.FIXED_DOLLAR, CategoryGroup.SAVINGS
            ),
            "HOA": BudgetCategory(
                "HOA", 1078.81, 27.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Utilities": BudgetCategory(
                "Utilities", 60.00, 1.5,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Subscriptions": BudgetCategory(
                "Subscriptions", 90.00, 2.3,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Groceries": BudgetCategory(
                "Groceries", 300.00, 7.5,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Uber/Lyft": BudgetCategory(
                "Uber/Lyft", 50.00, 1.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Therapy": BudgetCategory(
                "Therapy", 44.00, 1.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Dining/Entertainment": BudgetCategory(
                "Dining/Entertainment", 150.00, 3.8,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Flex/Buffer": BudgetCategory(
                "Flex/Buffer", 657.38, 16.5,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
        }
        
        # Fresh New Year (Jan-May) scenario
        jan_may_categories = {
            "Roth IRA": BudgetCategory(
                "Roth IRA", 1400.00, 35.2,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "General Savings": BudgetCategory(
                "General Savings", 250.00, 6.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "Vacation Fund": BudgetCategory(
                "Vacation Fund", 50.00, 1.3,
                CategoryType.FIXED_DOLLAR, CategoryGroup.SAVINGS
            ),
            "HOA": BudgetCategory(
                "HOA", 1078.81, 27.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Utilities": BudgetCategory(
                "Utilities", 60.00, 1.5,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Subscriptions": BudgetCategory(
                "Subscriptions", 90.00, 2.3,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Groceries": BudgetCategory(
                "Groceries", 300.00, 7.5,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Uber/Lyft": BudgetCategory(
                "Uber/Lyft", 50.00, 1.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Dining/Entertainment": BudgetCategory(
                "Dining/Entertainment", 150.00, 3.8,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Therapy": BudgetCategory(
                "Therapy", 44.00, 1.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Flex/Buffer": BudgetCategory(
                "Flex/Buffer", 90.94, 2.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
        }
        
        # Fresh New Year (June-Dec) scenario
        june_dec_categories = {
            "Roth IRA": BudgetCategory(
                "Roth IRA", 0.00, 0.0,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "General Savings": BudgetCategory(
                "General Savings", 833.33, 20.9,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS
            ),
            "Vacation Fund": BudgetCategory(
                "Vacation Fund", 300.00, 7.5,
                CategoryType.FIXED_DOLLAR, CategoryGroup.SAVINGS
            ),
            "HOA": BudgetCategory(
                "HOA", 1078.81, 27.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Utilities": BudgetCategory(
                "Utilities", 60.00, 1.5,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Subscriptions": BudgetCategory(
                "Subscriptions", 90.00, 2.3,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Groceries": BudgetCategory(
                "Groceries", 300.00, 7.5,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Uber/Lyft": BudgetCategory(
                "Uber/Lyft", 50.00, 1.3,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Dining/Entertainment": BudgetCategory(
                "Dining/Entertainment", 150.00, 3.8,
                CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE
            ),
            "Therapy": BudgetCategory(
                "Therapy", 44.00, 1.1,
                CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE
            ),
            "Flex/Buffer": BudgetCategory(
                "Flex/Buffer", 857.61, 21.5,
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