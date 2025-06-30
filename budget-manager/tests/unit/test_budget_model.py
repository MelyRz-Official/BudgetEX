"""
Unit tests for BudgetModel, BudgetCategory, and BudgetScenario classes.
Tests business logic, calculations, and data validation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
import math

from models.budget_model import BudgetModel, BudgetCategory, BudgetScenario
from tests.conftest import (
    assert_budget_summary_valid, 
    create_test_spending_data,
    VALID_PAYCHECK_AMOUNTS,
    INVALID_PAYCHECK_AMOUNTS,
    VALID_SPENDING_AMOUNTS,
    INVALID_SPENDING_AMOUNTS
)


class TestBudgetCategory:
    """Test cases for BudgetCategory class."""
    
    def test_budget_category_creation(self):
        """Test creating a budget category with valid data."""
        category = BudgetCategory(
            name="Groceries",
            amount=250.0,
            percentage=8.3,
            fixed_amount=False,
            description="Food expenses"
        )
        
        assert category.name == "Groceries"
        assert category.amount == 250.0
        assert category.percentage == 8.3
        assert category.fixed_amount is False
        assert category.description == "Food expenses"
    
    def test_budget_category_defaults(self):
        """Test budget category with default values."""
        category = BudgetCategory("Rent", 1200.0, 40.0)
        
        assert category.fixed_amount is False
        assert category.description == ""
    
    @pytest.mark.parametrize("paycheck,expected", [
        (3000.0, 249.0),  # 8.3% of 3000
        (4000.0, 332.0),  # 8.3% of 4000
        (2000.0, 166.0),  # 8.3% of 2000
        (0.0, 0.0),       # Edge case
    ])
    def test_calculate_budgeted_amount_percentage_based(self, paycheck, expected):
        """Test budgeted amount calculation for percentage-based categories."""
        category = BudgetCategory("Groceries", 250.0, 8.3, fixed_amount=False)
        result = category.calculate_budgeted_amount(paycheck)
        assert abs(result - expected) < 0.01  # Allow for floating point precision
    
    @pytest.mark.parametrize("paycheck", VALID_PAYCHECK_AMOUNTS)
    def test_calculate_budgeted_amount_fixed(self, paycheck):
        """Test budgeted amount calculation for fixed categories."""
        fixed_amount = 1200.0
        category = BudgetCategory("Rent", fixed_amount, 40.0, fixed_amount=True)
        result = category.calculate_budgeted_amount(paycheck)
        assert result == fixed_amount
    
    @pytest.mark.parametrize("paycheck,expected_percentage", [
        (3000.0, 40.0),   # 1200/3000 * 100
        (2400.0, 50.0),   # 1200/2400 * 100
        (1200.0, 100.0),  # 1200/1200 * 100
    ])
    def test_calculate_percentage_fixed_amount(self, paycheck, expected_percentage):
        """Test percentage calculation for fixed amount categories."""
        category = BudgetCategory("Rent", 1200.0, 40.0, fixed_amount=True)
        result = category.calculate_percentage(paycheck)
        assert abs(result - expected_percentage) < 0.01
    
    def test_calculate_percentage_fixed_amount_zero_paycheck(self):
        """Test percentage calculation with zero paycheck."""
        category = BudgetCategory("Rent", 1200.0, 40.0, fixed_amount=True)
        result = category.calculate_percentage(0.0)
        assert result == 40.0  # Should return the original percentage
    
    def test_calculate_percentage_non_fixed(self):
        """Test percentage calculation for non-fixed categories."""
        category = BudgetCategory("Groceries", 250.0, 8.3, fixed_amount=False)
        result = category.calculate_percentage(3000.0)
        assert result == 8.3


class TestBudgetScenario:
    """Test cases for BudgetScenario class."""
    
    def test_budget_scenario_creation(self, sample_categories):
        """Test creating a budget scenario."""
        scenario = BudgetScenario(
            name="Test Scenario",
            categories=sample_categories,
            default_paycheck=3000.0,
            description="Test scenario"
        )
        
        assert scenario.name == "Test Scenario"
        assert len(scenario.categories) == 5
        assert scenario.default_paycheck == 3000.0
        assert scenario.description == "Test scenario"
    
    def test_get_total_fixed_amount(self, sample_categories):
        """Test calculation of total fixed amounts."""
        scenario = BudgetScenario("Test", sample_categories)
        
        # From sample_categories: Utilities (60.0, fixed) + Rent (1200.0, fixed)
        expected_total = 60.0 + 1200.0
        result = scenario.get_total_fixed_amount()
        assert result == expected_total
    
    def test_get_total_percentage(self, sample_categories):
        """Test calculation of total percentages."""
        scenario = BudgetScenario("Test", sample_categories)
        
        # From sample_categories: non-fixed categories sum
        # Groceries (8.3) + Entertainment (3.3) + Savings (16.7) = 28.3
        expected_total = 8.3 + 3.3 + 16.7
        result = scenario.get_total_percentage()
        assert abs(result - expected_total) < 0.01
    
    @pytest.mark.parametrize("paycheck", VALID_PAYCHECK_AMOUNTS)
    def test_validate_scenario_valid(self, sample_categories, paycheck):
        """Test scenario validation with valid data."""
        scenario = BudgetScenario("Test", sample_categories)
        errors = scenario.validate_scenario(paycheck)
        
        # Should have no errors for reasonable paycheck amounts
        if paycheck >= 2000:  # Sufficient to cover fixed expenses
            assert len(errors) == 0
    
    @pytest.mark.parametrize("paycheck", INVALID_PAYCHECK_AMOUNTS[:-2])  # Exclude string and None
    def test_validate_scenario_invalid_paycheck(self, sample_categories, paycheck):
        """Test scenario validation with invalid paycheck amounts."""
        scenario = BudgetScenario("Test", sample_categories)
        errors = scenario.validate_scenario(paycheck)
        
        assert len(errors) > 0
        assert any("positive" in error.lower() for error in errors)
    
    def test_validate_scenario_fixed_exceeds_paycheck(self, sample_categories):
        """Test validation when fixed expenses exceed paycheck."""
        scenario = BudgetScenario("Test", sample_categories)
        low_paycheck = 1000.0  # Less than fixed expenses (1260.0)
        
        errors = scenario.validate_scenario(low_paycheck)
        assert len(errors) > 0
        assert any("fixed expenses" in error.lower() for error in errors)
    
    def test_validate_scenario_percentage_over_100(self):
        """Test validation when percentages exceed 100%."""
        categories = {
            "Cat1": BudgetCategory("Cat1", 100.0, 60.0, False),
            "Cat2": BudgetCategory("Cat2", 200.0, 50.0, False)
        }
        scenario = BudgetScenario("Test", categories)
        
        errors = scenario.validate_scenario(3000.0)
        assert len(errors) > 0
        assert any("exceed 100%" in error for error in errors)


class TestBudgetModel:
    """Test cases for BudgetModel class."""
    
    def test_budget_model_initialization(self, test_db_path):
        """Test budget model initialization."""
        with patch('models.budget_model.DatabaseManager'):
            model = BudgetModel(test_db_path)
            
            assert model.current_scenario_name == "July-December 2025"
            assert model.current_paycheck == 3984.94
            assert len(model.scenarios) == 3
            assert isinstance(model.actual_spending, dict)
    
    def test_get_scenario_names(self, budget_model):
        """Test getting available scenario names."""
        names = budget_model.get_scenario_names()
        
        assert isinstance(names, list)
        assert "July-December 2025" in names
        assert "Fresh New Year (Jan-May)" in names
        assert "Fresh New Year (June-Dec)" in names
        assert len(names) == 3
    
    def test_get_current_scenario(self, budget_model):
        """Test getting current scenario."""
        scenario = budget_model.get_current_scenario()
        
        assert isinstance(scenario, BudgetScenario)
        assert scenario.name == budget_model.current_scenario_name
    
    @pytest.mark.parametrize("scenario_name", [
        "July-December 2025",
        "Fresh New Year (Jan-May)",
        "Fresh New Year (June-Dec)"
    ])
    def test_set_current_scenario_valid(self, budget_model, scenario_name):
        """Test setting valid scenario."""
        with patch.object(budget_model, 'save_scenario_data'), \
             patch.object(budget_model, 'load_scenario_data'):
            
            result = budget_model.set_current_scenario(scenario_name)
            assert result is True
            assert budget_model.current_scenario_name == scenario_name
    
    def test_set_current_scenario_invalid(self, budget_model):
        """Test setting invalid scenario."""
        result = budget_model.set_current_scenario("Non-existent Scenario")
        assert result is False
        assert budget_model.current_scenario_name == "July-December 2025"  # Unchanged
    
    @pytest.mark.parametrize("amount", VALID_PAYCHECK_AMOUNTS)
    def test_set_paycheck_amount_valid(self, budget_model, amount):
        """Test setting valid paycheck amounts."""
        result = budget_model.set_paycheck_amount(amount)
        assert result is True
        assert budget_model.current_paycheck == amount
    
    @pytest.mark.parametrize("amount", INVALID_PAYCHECK_AMOUNTS[:-2])  # Exclude string and None
    def test_set_paycheck_amount_invalid(self, budget_model, amount):
        """Test setting invalid paycheck amounts."""
        original_paycheck = budget_model.current_paycheck
        result = budget_model.set_paycheck_amount(amount)
        assert result is False
        assert budget_model.current_paycheck == original_paycheck
    
    @pytest.mark.parametrize("amount", VALID_SPENDING_AMOUNTS)
    def test_set_actual_spending_valid(self, budget_model, amount):
        """Test setting valid spending amounts."""
        category = "Groceries"  # Known to exist in default scenario
        result = budget_model.set_actual_spending(category, amount)
        assert result is True
        assert budget_model.get_actual_spending(category) == amount
    
    @pytest.mark.parametrize("amount", INVALID_SPENDING_AMOUNTS[:-2])  # Exclude string and None
    def test_set_actual_spending_invalid_amount(self, budget_model, amount):
        """Test setting invalid spending amounts."""
        category = "Groceries"
        original_amount = budget_model.get_actual_spending(category)
        result = budget_model.set_actual_spending(category, amount)
        assert result is False
        assert budget_model.get_actual_spending(category) == original_amount
    
    def test_set_actual_spending_invalid_category(self, budget_model):
        """Test setting spending for non-existent category."""
        result = budget_model.set_actual_spending("Non-existent Category", 100.0)
        assert result is False
    
    def test_get_actual_spending_existing(self, budget_model):
        """Test getting spending for existing category."""
        category = "Groceries"
        budget_model.set_actual_spending(category, 150.0)
        result = budget_model.get_actual_spending(category)
        assert result == 150.0
    
    def test_get_actual_spending_non_existing(self, budget_model):
        """Test getting spending for non-existing category."""
        result = budget_model.get_actual_spending("Non-existent Category")
        assert result == 0.0
    
    def test_calculate_budget_summary_structure(self, budget_model):
        """Test that budget summary has correct structure."""
        summary = budget_model.calculate_budget_summary()
        assert_budget_summary_valid(summary)
    
    def test_calculate_budget_summary_calculations(self, budget_model):
        """Test budget summary calculations."""
        # Set known spending amounts
        budget_model.set_actual_spending("Groceries", 250.0)
        budget_model.set_actual_spending("Utilities", 60.0)
        budget_model.set_paycheck_amount(4000.0)
        
        summary = budget_model.calculate_budget_summary()
        
        # Verify basic calculations
        assert summary['paycheck_amount'] == 4000.0
        assert summary['totals']['total_spent'] == 310.0  # 250 + 60
        
        # Verify category-specific data
        groceries_data = summary['categories']['Groceries']
        assert groceries_data['actual_spent'] == 250.0
        assert groceries_data['is_fixed'] is False
        
        utilities_data = summary['categories']['Utilities']
        assert utilities_data['actual_spent'] == 60.0
        assert utilities_data['is_fixed'] is True
    
    def test_calculate_budget_summary_status_determination(self, budget_model):
        """Test status determination in budget summary."""
        budget_model.set_paycheck_amount(3000.0)
        
        # Test different spending scenarios
        test_cases = [
            ("Groceries", 0.0, "not_set"),
            ("Utilities", 60.0, "on_target"),  # Fixed amount, exact match
            ("Dining/Entertainment", 100.0, "under_budget"),  # Less than budgeted
            ("Therapy", 60.0, "over_budget")  # More than fixed amount (44.0)
        ]
        
        for category, amount, expected_status in test_cases:
            budget_model.set_actual_spending(category, amount)
        
        summary = budget_model.calculate_budget_summary()
        
        for category, amount, expected_status in test_cases:
            actual_status = summary['categories'][category]['status']
            assert actual_status == expected_status, f"Category {category}: expected {expected_status}, got {actual_status}"
    
    def test_clear_all_spending(self, budget_model):
        """Test clearing all spending data."""
        # Set some spending
        budget_model.set_actual_spending("Groceries", 200.0)
        budget_model.set_actual_spending("Utilities", 65.0)
        
        with patch.object(budget_model.db, 'clear_spending_data', return_value=True):
            result = budget_model.clear_all_spending()
        
        assert result is True
        assert all(amount == 0.0 for amount in budget_model.actual_spending.values())
    
    def test_save_scenario_data(self, budget_model):
        """Test saving scenario data."""
        with patch.object(budget_model.db, 'save_budget_data', return_value=True) as mock_save:
            result = budget_model.save_scenario_data()
            
            assert result is True
            mock_save.assert_called_once_with(
                budget_model.current_scenario_name,
                budget_model.current_paycheck,
                budget_model.actual_spending
            )
    
    def test_load_scenario_data_success(self, budget_model):
        """Test loading scenario data successfully."""
        mock_data = (4000.0, {"Groceries": 275.0, "Utilities": 65.0})
        
        with patch.object(budget_model.db, 'load_budget_data', return_value=mock_data):
            result = budget_model.load_scenario_data("Test Scenario")
            
            assert result is True
            assert budget_model.current_paycheck == 4000.0
            assert budget_model.actual_spending["Groceries"] == 275.0
            assert budget_model.actual_spending["Utilities"] == 65.0
    
    def test_load_scenario_data_no_data(self, budget_model):
        """Test loading scenario data when no data exists."""
        with patch.object(budget_model.db, 'load_budget_data', return_value=None):
            result = budget_model.load_scenario_data("Test Scenario")
            
            assert result is False
            # Should initialize with zeros
            scenario = budget_model.get_current_scenario()
            for category in scenario.categories:
                assert budget_model.actual_spending[category] == 0.0
    
    def test_export_scenario_data_current(self, budget_model):
        """Test exporting current scenario data."""
        budget_model.set_actual_spending("Groceries", 200.0)
        budget_model.set_paycheck_amount(3500.0)
        
        export_data = budget_model.export_scenario_data()
        
        assert export_data['metadata']['scenario_name'] == budget_model.current_scenario_name
        assert export_data['metadata']['paycheck_amount'] == 3500.0
        assert len(export_data['categories']) > 0
        assert 'summary' in export_data
        
        # Check that datetime is properly formatted
        from datetime import datetime
        datetime.fromisoformat(export_data['metadata']['export_date'])  # Should not raise
    
    def test_export_scenario_data_different_scenario(self, budget_model):
        """Test exporting different scenario data."""
        original_scenario = budget_model.current_scenario_name
        target_scenario = "Fresh New Year (Jan-May)"
        
        with patch.object(budget_model, 'set_current_scenario') as mock_set:
            mock_set.return_value = True
            export_data = budget_model.export_scenario_data(target_scenario)
            
            # Should have attempted to switch scenarios
            mock_set.assert_called()
            assert export_data['metadata']['scenario_name'] == target_scenario
    
    def test_add_spending_transaction(self, budget_model):
        """Test adding a spending transaction."""
        category = "Groceries"
        initial_spending = 100.0
        transaction_amount = 25.50
        
        budget_model.set_actual_spending(category, initial_spending)
        
        with patch.object(budget_model.db, 'add_spending_history', return_value=True) as mock_add:
            result = budget_model.add_spending_transaction(category, transaction_amount, "Coffee shop")
            
            assert result is True
            assert budget_model.get_actual_spending(category) == initial_spending + transaction_amount
            mock_add.assert_called_once_with(
                budget_model.current_scenario_name, 
                category, 
                transaction_amount, 
                "Coffee shop"
            )
    
    def test_get_spending_trends(self, budget_model):
        """Test getting spending trends."""
        mock_trends = [
            {'category': 'Groceries', 'amount': 50.0, 'date_added': '2025-06-29'},
            {'category': 'Groceries', 'amount': 75.0, 'date_added': '2025-06-28'}
        ]
        
        with patch.object(budget_model.db, 'get_spending_history', return_value=mock_trends) as mock_get:
            result = budget_model.get_spending_trends("Groceries", 7)
            
            assert result == mock_trends
            mock_get.assert_called_once_with(budget_model.current_scenario_name, "Groceries", 7)
    
    def test_validate_all_scenarios(self, budget_model):
        """Test validating all scenarios."""
        validation_results = budget_model.validate_all_scenarios()
        
        assert isinstance(validation_results, dict)
        assert len(validation_results) == 3  # Three scenarios
        
        for scenario_name, errors in validation_results.items():
            assert isinstance(errors, list)
            assert scenario_name in budget_model.scenarios
    
    def test_get_category_suggestions(self, budget_model):
        """Test getting category suggestions."""
        suggestions = budget_model.get_category_suggestions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5  # Should limit to 5 suggestions
        
        # Should not suggest categories that already exist
        current_categories = set(budget_model.get_current_scenario().categories.keys())
        for suggestion in suggestions:
            assert suggestion not in current_categories
    
    def test_backup_data(self, budget_model):
        """Test creating data backup."""
        with patch.object(budget_model.db, 'backup_database', return_value=True) as mock_backup:
            result = budget_model.backup_data("/custom/path")
            
            assert result is True
            mock_backup.assert_called_once_with("/custom/path")
    
    def test_get_database_stats(self, budget_model):
        """Test getting database statistics."""
        mock_stats = {
            'budget_records': 10,
            'history_records': 25,
            'file_size_mb': 1.2
        }
        
        with patch.object(budget_model.db, 'get_database_stats', return_value=mock_stats) as mock_get:
            result = budget_model.get_database_stats()
            
            assert result == mock_stats
            mock_get.assert_called_once()


class TestBudgetModelIntegration:
    """Integration tests for BudgetModel with real database operations."""
    
    def test_model_with_real_database(self, test_db_path):
        """Test model operations with real database."""
        model = BudgetModel(test_db_path)
        
        # Test full workflow
        model.set_paycheck_amount(3500.0)
        model.set_actual_spending("Groceries", 275.0)
        model.set_actual_spending("Utilities", 65.0)
        
        # Save data
        assert model.save_scenario_data() is True
        
        # Create new model instance and load data
        model2 = BudgetModel(test_db_path)
        model2.load_scenario_data(model.current_scenario_name)
        
        # Verify data persistence
        assert model2.current_paycheck == 3500.0
        assert model2.get_actual_spending("Groceries") == 275.0
        assert model2.get_actual_spending("Utilities") == 65.0
    
    def test_scenario_switching_with_persistence(self, test_db_path):
        """Test scenario switching with data persistence."""
        model = BudgetModel(test_db_path)
        
        # Set data for first scenario
        model.set_paycheck_amount(4000.0)
        model.set_actual_spending("Groceries", 300.0)
        model.save_scenario_data()
        
        # Switch to second scenario
        model.set_current_scenario("Fresh New Year (Jan-May)")
        model.set_paycheck_amount(4200.0)
        model.set_actual_spending("Roth IRA", 1400.0)
        model.save_scenario_data()
        
        # Switch back to first scenario
        model.set_current_scenario("July-December 2025")
        
        # Verify original data is restored
        assert model.current_paycheck == 4000.0
        assert model.get_actual_spending("Groceries") == 300.0
    
    @pytest.mark.performance
    def test_model_performance_large_dataset(self, test_db_path, large_dataset):
        """Test model performance with large dataset."""
        import time
        
        # Create model with large scenario
        model = BudgetModel(test_db_path)
        large_scenario = BudgetScenario("Large Test", large_dataset, 50000.0)
        model.scenarios["Large Test"] = large_scenario
        model.set_current_scenario("Large Test")
        
        # Set spending for all categories
        start_time = time.time()
        for category in large_dataset.keys():
            model.set_actual_spending(category, 100.0)
        set_time = time.time() - start_time
        
        # Calculate summary
        start_time = time.time()
        summary = model.calculate_budget_summary()
        calc_time = time.time() - start_time
        
        # Save data
        start_time = time.time()
        model.save_scenario_data()
        save_time = time.time() - start_time
        
        # Performance assertions (adjust thresholds as needed)
        assert set_time < 1.0, f"Setting spending took too long: {set_time:.2f}s"
        assert calc_time < 0.5, f"Summary calculation took too long: {calc_time:.2f}s"
        assert save_time < 2.0, f"Saving data took too long: {save_time:.2f}s"
        
        # Verify correctness
        assert len(summary['categories']) == 100
        assert summary['totals']['total_spent'] == 10000.0  # 100 categories * 100.0 each


class TestBudgetModelErrorHandling:
    """Test error handling in BudgetModel."""
    
    def test_model_initialization_with_invalid_db(self):
        """Test model initialization with invalid database path."""
        with patch('models.budget_model.DatabaseManager', side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                BudgetModel("/invalid/path/budget.db")
    
    def test_save_data_with_database_error(self, budget_model):
        """Test saving data when database error occurs."""
        with patch.object(budget_model.db, 'save_budget_data', return_value=False):
            result = budget_model.save_scenario_data()
            assert result is False
    
    def test_load_data_with_database_error(self, budget_model):
        """Test loading data when database error occurs."""
        with patch.object(budget_model.db, 'load_budget_data', side_effect=Exception("DB Error")):
            # Should handle error gracefully and return False
            result = budget_model.load_scenario_data("Test Scenario")
            assert result is False
    
    def test_backup_with_permission_error(self, budget_model):
        """Test backup when file permission error occurs."""
        with patch.object(budget_model.db, 'backup_database', return_value=False):
            result = budget_model.backup_data()
            assert result is False


# Parametrized tests for comprehensive coverage
class TestBudgetModelParametrized:
    """Parametrized tests for comprehensive coverage."""
    
    @pytest.mark.parametrize("scenario_name,paycheck", [
        ("July-December 2025", 3984.94),
        ("Fresh New Year (Jan-May)", 4200.0),
        ("Fresh New Year (June-Dec)", 3800.0)
    ])
    def test_all_scenarios_summary_calculation(self, budget_model, scenario_name, paycheck):
        """Test summary calculation for all scenarios."""
        budget_model.set_current_scenario(scenario_name)
        budget_model.set_paycheck_amount(paycheck)
        
        summary = budget_model.calculate_budget_summary()
        assert_budget_summary_valid(summary)
        assert summary['scenario_name'] == scenario_name
        assert summary['paycheck_amount'] == paycheck
    
    @pytest.mark.parametrize("category,amount", [
        ("Groceries", 275.0),
        ("Utilities", 65.0),
        ("Entertainment", 0.0),
        ("Dining/Entertainment", 125.0)
    ])
    def test_individual_category_spending(self, budget_model, category, amount):
        """Test setting spending for individual categories."""
        # Ensure category exists in current scenario
        current_categories = budget_model.get_current_scenario().categories
        if category in current_categories:
            result = budget_model.set_actual_spending(category, amount)
            assert result is True
            assert budget_model.get_actual_spending(category) == amount
        else:
            result = budget_model.set_actual_spending(category, amount)
            assert result is False