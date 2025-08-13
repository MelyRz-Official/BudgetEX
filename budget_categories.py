"""
Budget Categories Module
Contains category definitions and calculation logic
"""
from enum import Enum
import tkinter as tk

class CategoryType(Enum):
    FIXED_DOLLAR = "fixed_dollar"
    FIXED_PERCENTAGE = "fixed_percentage"

class CategoryGroup(Enum):
    SAVINGS = "savings"
    EXPENSE = "expense"

class ViewMode(Enum):
    FIRST_PAYCHECK = "First Paycheck"
    SECOND_PAYCHECK = "Second Paycheck"
    MONTHLY = "Monthly"

class BudgetCategory:
    def __init__(self, name, monthly_amount, percentage, category_type, category_group):
        self.name = name
        self.monthly_amount = monthly_amount
        self.percentage = percentage
        self.category_type = category_type
        self.category_group = category_group
    
    def calculate_budgeted_amount(self, first_paycheck, second_paycheck, view_mode):
        """Calculate budgeted amount and percentage for given paychecks and view mode"""
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
    
    def get_status_and_color(self, budgeted, actual):
        """Get status text and color based on budgeted vs actual amounts"""
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

def create_real_categories():
    """Create real budget categories based on budget_models.py"""
    categories = {}
    
    # Real categories from July-December 2025 scenario
    category_data = [
        ("Roth IRA", 333.33, 8.4, CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS),
        ("General Savings", 769.23, 19.3, CategoryType.FIXED_PERCENTAGE, CategoryGroup.SAVINGS),
        ("HOA", 1078.81, 27.1, CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE),
        ("Utilities", 150.00, 3.8, CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE),
        ("Subscriptions", 60.00, 1.5, CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE),
        ("Groceries", 550.00, 13.8, CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE),
        ("Uber/Lyft", 70.00, 1.8, CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE),
        ("Therapy", 44.00, 1.1, CategoryType.FIXED_DOLLAR, CategoryGroup.EXPENSE),
        ("Dining/Entertainment", 400.00, 10.0, CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE),
        ("Flex/Buffer", 535.14, 13.4, CategoryType.FIXED_PERCENTAGE, CategoryGroup.EXPENSE),
    ]
    
    for name, monthly_amount, percentage, cat_type, cat_group in category_data:
        categories[name] = {
            'category': BudgetCategory(name, monthly_amount, percentage, cat_type, cat_group),
            'spending': tk.DoubleVar()
        }
    
    return categories