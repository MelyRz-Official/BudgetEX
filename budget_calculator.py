# budget_calculator.py
from dataclasses import dataclass
from typing import Dict
from budget_models import BudgetScenario, ViewMode

@dataclass
class CategoryResult:
    name: str
    percentage: float
    budgeted: float
    actual: float
    difference: float
    status: str
    color: str

@dataclass
class BudgetSummary:
    total_budgeted: float
    total_spent: float
    remaining: float
    over_under: float
    over_under_status: str
    over_under_color: str

class BudgetCalculator:
    """Handles all budget calculations and logic"""
    
    def __init__(self, scenario: BudgetScenario):
        self.scenario = scenario
    
    def calculate_all_categories(self, income: float, view_mode: ViewMode, 
                               actual_spending: Dict[str, float]) -> Dict[str, CategoryResult]:
        """Calculate results for all categories in the scenario"""
        results = {}
        
        for category_name, category in self.scenario.get_all_categories().items():
            actual = actual_spending.get(category_name, 0.0)
            
            # Calculate budgeted amount and percentage
            budgeted, percentage = category.calculate_budgeted_amount(income, view_mode)
            
            # Calculate difference
            difference = budgeted - actual
            
            # Get status and color
            status, color = category.get_status_and_color(budgeted, actual)
            
            results[category_name] = CategoryResult(
                name=category_name,
                percentage=percentage,
                budgeted=budgeted,
                actual=actual,
                difference=difference,
                status=status,
                color=color
            )
        
        return results
    
    def calculate_summary(self, category_results: Dict[str, CategoryResult], 
                         income: float) -> BudgetSummary:
        """Calculate budget summary from category results"""
        total_budgeted = sum(result.budgeted for result in category_results.values())
        total_spent = sum(result.actual for result in category_results.values())
        remaining = income - total_spent
        over_under = total_spent - total_budgeted
        
        # Determine over/under status and color
        if over_under > 0:
            over_under_status = "OVER"
            over_under_color = "red"
        elif over_under < 0:
            over_under_status = "UNDER"
            over_under_color = "green"
            over_under = abs(over_under)  # Make positive for display
        else:
            over_under_status = "ON TARGET"
            over_under_color = "blue"
        
        return BudgetSummary(
            total_budgeted=total_budgeted,
            total_spent=total_spent,
            remaining=remaining,
            over_under=over_under,
            over_under_status=over_under_status,
            over_under_color=over_under_color
        )
    
    def export_to_csv_data(self, category_results: Dict[str, CategoryResult], 
                          view_mode: ViewMode) -> list:
        """Export category results to CSV-ready data"""
        csv_data = []
        csv_data.append(['View Mode', 'Scenario', 'Category', 'Percentage', 
                        'Budgeted Amount', 'Actual Spent', 'Difference', 'Status'])
        
        for result in category_results.values():
            csv_data.append([
                view_mode.value,
                self.scenario.name,
                result.name,
                f"{result.percentage:.1f}%",
                f"{result.budgeted:.2f}",
                f"{result.actual:.2f}",
                f"{result.difference:.2f}",
                result.status
            ])
        
        return csv_data