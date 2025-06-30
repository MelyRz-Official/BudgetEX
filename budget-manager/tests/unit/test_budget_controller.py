"""
Unit tests for BudgetController class.
Tests controller logic, event handling, and view-model coordination.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import threading
import time

from controllers.budget_controller import BudgetController
from models.budget_model import BudgetModel
from config import ConfigManager, AppConfig


class TestBudgetControllerInitialization:
    """Test BudgetController initialization and setup."""
    
    def test_controller_creation(self, budget_model, mock_config_manager):
        """Test creating a BudgetController instance."""
        controller = BudgetController(budget_model, mock_config_manager)
        
        assert controller.model == budget_model
        assert controller.config_manager == mock_config_manager
        assert isinstance(controller.views, dict)
        assert isinstance(controller.callbacks, dict)
        assert len(controller.callbacks) == 6  # Expected number of event types
        
        controller.cleanup()
    
    def test_controller_with_default_config_manager(self, budget_model):
        """Test controller with default config manager."""
        with patch('controllers.budget_controller.ConfigManager') as mock_cm_class:
            mock_cm_instance = Mock()
            mock_cm_class.return_value = mock_cm_instance
            
            controller = BudgetController(budget_model)
            
            assert controller.config_manager == mock_cm_instance
            mock_cm_class.assert_called_once()
            
            controller.cleanup()
    
    def test_event_callbacks_initialization(self, budget_controller):
        """Test that event callbacks are properly initialized."""
        expected_events = [
            'scenario_changed', 'paycheck_changed', 'spending_changed',
            'data_saved', 'data_loaded', 'config_changed'
        ]
        
        for event in expected_events:
            assert event in budget_controller.callbacks
            assert isinstance(budget_controller.callbacks[event], list)
            assert len(budget_controller.callbacks[event]) == 0  # Initially empty


class TestBudgetControllerViewManagement:
    """Test view registration and management."""
    
    def test_register_view(self, budget_controller):
        """Test registering a view with the controller."""
        mock_view = Mock()
        view_name = "test_view"
        
        budget_controller.register_view(view_name, mock_view)
        
        assert view_name in budget_controller.views
        assert budget_controller.views[view_name] == mock_view
    
    def test_register_multiple_views(self, budget_controller):
        """Test registering multiple views."""
        views = {
            "budget_view": Mock(),
            "dashboard_view": Mock(),
            "settings_view": Mock()
        }
        
        for name, view in views.items():
            budget_controller.register_view(name, view)
        
        assert len(budget_controller.views) == 3
        for name, view in views.items():
            assert budget_controller.views[name] == view
    
    def test_subscribe_to_event(self, budget_controller):
        """Test subscribing callbacks to events."""
        callback1 = Mock()
        callback2 = Mock()
        
        budget_controller.subscribe_to_event('scenario_changed', callback1)
        budget_controller.subscribe_to_event('scenario_changed', callback2)
        
        assert len(budget_controller.callbacks['scenario_changed']) == 2
        assert callback1 in budget_controller.callbacks['scenario_changed']
        assert callback2 in budget_controller.callbacks['scenario_changed']
    
    def test_subscribe_to_invalid_event(self, budget_controller):
        """Test subscribing to non-existent event."""
        callback = Mock()
        
        # Should not raise error, but callback won't be added
        budget_controller.subscribe_to_event('invalid_event', callback)
        
        assert 'invalid_event' not in budget_controller.callbacks
    
    def test_emit_event(self, budget_controller):
        """Test emitting events to subscribers."""
        callback1 = Mock()
        callback2 = Mock()
        test_data = {"test": "data"}
        
        budget_controller.subscribe_to_event('scenario_changed', callback1)
        budget_controller.subscribe_to_event('scenario_changed', callback2)
        
        budget_controller._emit_event('scenario_changed', test_data)
        
        callback1.assert_called_once_with(test_data)
        callback2.assert_called_once_with(test_data)
    
    def test_emit_event_with_error(self, budget_controller):
        """Test emitting event when callback raises error."""
        good_callback = Mock()
        bad_callback = Mock(side_effect=Exception("Test error"))
        test_data = {"test": "data"}
        
        budget_controller.subscribe_to_event('scenario_changed', good_callback)
        budget_controller.subscribe_to_event('scenario_changed', bad_callback)
        
        # Should not raise error, should continue to other callbacks
        budget_controller._emit_event('scenario_changed', test_data)
        
        good_callback.assert_called_once_with(test_data)
        bad_callback.assert_called_once_with(test_data)


class TestBudgetControllerScenarioManagement:
    """Test scenario management operations."""
    
    def test_get_available_scenarios(self, budget_controller):
        """Test getting available scenarios."""
        mock_scenarios = ["Scenario 1", "Scenario 2", "Scenario 3"]
        budget_controller.model.get_scenario_names.return_value = mock_scenarios
        
        result = budget_controller.get_available_scenarios()
        
        assert result == mock_scenarios
        budget_controller.model.get_scenario_names.assert_called_once()
    
    def test_get_current_scenario_name(self, budget_controller):
        """Test getting current scenario name."""
        expected_name = "Test Scenario"
        budget_controller.model.current_scenario_name = expected_name
        
        result = budget_controller.get_current_scenario_name()
        
        assert result == expected_name
    
    def test_switch_scenario_success(self, budget_controller):
        """Test successfully switching scenarios."""
        new_scenario = "New Scenario"
        budget_controller.model.set_current_scenario.return_value = True
        budget_controller.model.current_paycheck = 4000.0
        budget_controller.model.actual_spending = {"Test": 100.0}
        
        # Mock event emission
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.switch_scenario(new_scenario)
            
            assert result is True
            budget_controller.model.set_current_scenario.assert_called_once_with(new_scenario)
            mock_emit.assert_called_once_with('scenario_changed', {
                'scenario_name': new_scenario,
                'paycheck_amount': 4000.0,
                'spending_data': {"Test": 100.0}
            })
    
    def test_switch_scenario_failure(self, budget_controller):
        """Test failed scenario switch."""
        new_scenario = "Invalid Scenario"
        budget_controller.model.set_current_scenario.return_value = False
        
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.switch_scenario(new_scenario)
            
            assert result is False
            budget_controller.model.set_current_scenario.assert_called_once_with(new_scenario)
            mock_emit.assert_not_called()


class TestBudgetControllerPaycheckManagement:
    """Test paycheck management operations."""
    
    def test_get_paycheck_amount(self, budget_controller):
        """Test getting paycheck amount."""
        expected_amount = 3500.0
        budget_controller.model.current_paycheck = expected_amount
        
        result = budget_controller.get_paycheck_amount()
        
        assert result == expected_amount
    
    @pytest.mark.parametrize("amount,expected_result", [
        (3000.0, True),
        (4500.0, True),
        ("3000", True),  # String that can be converted
        (0.0, False),    # Invalid amount
        (-100.0, False), # Negative amount
        ("invalid", False), # Invalid string
        (None, False),   # None value
    ])
    def test_set_paycheck_amount(self, budget_controller, amount, expected_result):
        """Test setting paycheck amount with various inputs."""
        budget_controller.model.set_paycheck_amount.return_value = expected_result
        
        with patch.object(budget_controller, '_emit_event') as mock_emit, \
             patch.object(budget_controller, '_schedule_auto_save') as mock_save:
            
            result = budget_controller.set_paycheck_amount(amount)
            
            assert result == expected_result
            
            if expected_result:
                # Should emit event and schedule save for valid amounts
                mock_emit.assert_called_once()
                if budget_controller.config.auto_save:
                    mock_save.assert_called_once()
            else:
                # Should not emit event for invalid amounts
                mock_emit.assert_not_called()
                mock_save.assert_not_called()
    
    def test_set_paycheck_amount_with_auto_save_disabled(self, budget_controller):
        """Test setting paycheck amount with auto-save disabled."""
        budget_controller.config.auto_save = False
        budget_controller.model.set_paycheck_amount.return_value = True
        
        with patch.object(budget_controller, '_emit_event'), \
             patch.object(budget_controller, '_schedule_auto_save') as mock_save:
            
            result = budget_controller.set_paycheck_amount(3000.0)
            
            assert result is True
            mock_save.assert_not_called()


class TestBudgetControllerSpendingManagement:
    """Test spending management operations."""
    
    def test_get_actual_spending(self, budget_controller):
        """Test getting actual spending for a category."""
        category = "Groceries"
        expected_amount = 250.0
        budget_controller.model.get_actual_spending.return_value = expected_amount
        
        result = budget_controller.get_actual_spending(category)
        
        assert result == expected_amount
        budget_controller.model.get_actual_spending.assert_called_once_with(category)
    
    @pytest.mark.parametrize("amount,expected_result", [
        (250.0, True),
        (0.0, True),     # Zero is valid
        ("100.5", True), # String that can be converted
        (-50.0, False),  # Negative amount
        ("invalid", False), # Invalid string
        (None, False),   # None value
    ])
    def test_set_actual_spending(self, budget_controller, amount, expected_result):
        """Test setting actual spending with various inputs."""
        category = "Groceries"
        budget_controller.model.set_actual_spending.return_value = expected_result
        
        with patch.object(budget_controller, '_emit_event') as mock_emit, \
             patch.object(budget_controller, '_schedule_auto_save') as mock_save:
            
            result = budget_controller.set_actual_spending(category, amount)
            
            assert result == expected_result
            
            if expected_result:
                mock_emit.assert_called_once()
                if budget_controller.config.auto_save:
                    mock_save.assert_called_once()
            else:
                mock_emit.assert_not_called()
                mock_save.assert_not_called()
    
    def test_clear_all_spending(self, budget_controller):
        """Test clearing all spending data."""
        budget_controller.model.clear_all_spending.return_value = True
        
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.clear_all_spending()
            
            assert result is True
            budget_controller.model.clear_all_spending.assert_called_once()
            mock_emit.assert_called_once_with('spending_changed', {
                'category': 'all',
                'amount': 0.0,
                'summary': budget_controller.get_budget_summary()
            })


class TestBudgetControllerCalculations:
    """Test budget calculation operations."""
    
    def test_get_budget_summary(self, budget_controller):
        """Test getting budget summary."""
        mock_summary = {
            'scenario_name': 'Test',
            'totals': {'total_spent': 500.0},
            'categories': {}
        }
        budget_controller.model.calculate_budget_summary.return_value = mock_summary
        
        result = budget_controller.get_budget_summary()
        
        assert result == mock_summary
        budget_controller.model.calculate_budget_summary.assert_called_once()
    
    def test_get_category_data(self, budget_controller):
        """Test getting specific category data."""
        category = "Groceries"
        mock_summary = {
            'categories': {
                'Groceries': {'budgeted': 300.0, 'actual': 250.0},
                'Utilities': {'budgeted': 60.0, 'actual': 65.0}
            }
        }
        budget_controller.model.calculate_budget_summary.return_value = mock_summary
        
        result = budget_controller.get_category_data(category)
        
        assert result == mock_summary['categories']['Groceries']
    
    def test_get_category_data_nonexistent(self, budget_controller):
        """Test getting data for non-existent category."""
        category = "Nonexistent"
        mock_summary = {'categories': {}}
        budget_controller.model.calculate_budget_summary.return_value = mock_summary
        
        result = budget_controller.get_category_data(category)
        
        assert result is None
    
    def test_validate_current_budget(self, budget_controller):
        """Test validating current budget."""
        mock_errors = ["Error 1", "Error 2"]
        mock_summary = {'validation_errors': mock_errors}
        budget_controller.model.calculate_budget_summary.return_value = mock_summary
        
        result = budget_controller.validate_current_budget()
        
        assert result == mock_errors


class TestBudgetControllerDataPersistence:
    """Test data persistence operations."""
    
    def test_save_data_success(self, budget_controller):
        """Test successful data saving."""
        budget_controller.model.save_scenario_data.return_value = True
        budget_controller.model.backup_data.return_value = True
        budget_controller.config.auto_backup = True
        
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.save_data()
            
            assert result is True
            budget_controller.model.save_scenario_data.assert_called_once()
            budget_controller.model.backup_data.assert_called_once()
            mock_emit.assert_called_once()
    
    def test_save_data_without_backup(self, budget_controller):
        """Test saving data without auto-backup."""
        budget_controller.model.save_scenario_data.return_value = True
        budget_controller.config.auto_backup = False
        
        result = budget_controller.save_data()
        
        assert result is True
        budget_controller.model.save_scenario_data.assert_called_once()
        budget_controller.model.backup_data.assert_not_called()
    
    def test_save_data_failure(self, budget_controller):
        """Test failed data saving."""
        budget_controller.model.save_scenario_data.return_value = False
        
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.save_data()
            
            assert result is False
            mock_emit.assert_not_called()
    
    def test_save_data_silent(self, budget_controller):
        """Test silent data saving (no event emission)."""
        budget_controller.model.save_scenario_data.return_value = True
        
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.save_data(show_message=False)
            
            assert result is True
            mock_emit.assert_not_called()
    
    def test_load_data_success(self, budget_controller):
        """Test successful data loading."""
        scenario = "Test Scenario"
        budget_controller.model.load_scenario_data.return_value = True
        budget_controller.model.current_scenario_name = scenario
        budget_controller.model.current_paycheck = 3000.0
        budget_controller.model.actual_spending = {"Test": 100.0}
        
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.load_data(scenario)
            
            assert result is True
            budget_controller.model.load_scenario_data.assert_called_once_with(scenario)
            mock_emit.assert_called_once()
    
    def test_load_data_failure(self, budget_controller):
        """Test failed data loading."""
        scenario = "Test Scenario"
        budget_controller.model.load_scenario_data.return_value = False
        
        with patch.object(budget_controller, '_emit_event') as mock_emit:
            result = budget_controller.load_data(scenario)
            
            assert result is False
            mock_emit.assert_not_called()
    
    def test_load_data_current_scenario(self, budget_controller):
        """Test loading data for current scenario."""
        budget_controller.model.current_scenario_name = "Current Scenario"
        budget_controller.model.load_scenario_data.return_value = True
        
        result = budget_controller.load_data()  # No scenario specified
        
        budget_controller.model.load_scenario_data.assert_called_once_with("Current Scenario")
        assert result is True


class TestBudgetControllerAutoSave:
    """Test auto-save functionality."""
    
    def test_schedule_auto_save(self, budget_controller):
        """Test scheduling auto-save operation."""
        budget_controller.config.auto_save = True
        
        with patch('threading.Timer') as mock_timer:
            mock_timer_instance = Mock()
            mock_timer.return_value = mock_timer_instance
            
            budget_controller._schedule_auto_save()
            
            mock_timer.assert_called_once_with(2.0, budget_controller._perform_auto_save)
            mock_timer_instance.start.assert_called_once()
            assert budget_controller._auto_save_pending is True
    
    def test_cancel_previous_auto_save(self, budget_controller):
        """Test that previous auto-save is cancelled when scheduling new one."""
        budget_controller.config.auto_save = True
        
        # Mock previous timer
        previous_timer = Mock()
        budget_controller._auto_save_timer = previous_timer
        
        with patch('threading.Timer') as mock_timer:
            budget_controller._schedule_auto_save()
            
            previous_timer.cancel.assert_called_once()
            mock_timer.assert_called_once()
    
    def test_perform_auto_save(self, budget_controller):
        """Test performing auto-save operation."""
        budget_controller._auto_save_pending = True
        
        with patch.object(budget_controller, 'save_data') as mock_save:
            budget_controller._perform_auto_save()
            
            mock_save.assert_called_once_with(show_message=False)
            assert budget_controller._auto_save_pending is False
    
    def test_perform_auto_save_not_pending(self, budget_controller):
        """Test auto-save when not pending."""
        budget_controller._auto_save_pending = False
        
        with patch.object(budget_controller, 'save_data') as mock_save:
            budget_controller._perform_auto_save()
            
            mock_save.assert_not_called()


class TestBudgetControllerConfigurationManagement:
    """Test configuration management operations."""
    
    def test_get_config(self, budget_controller):
        """Test getting current configuration."""
        result = budget_controller.get_config()
        assert result == budget_controller.config
    
    def test_update_config_success(self, budget_controller):
        """Test successful configuration update."""
        changes = {'theme': 'light', 'auto_save': True}
        
        with patch('controllers.budget_controller.update_config') as mock_update, \
             patch('controllers.budget_controller.get_config') as mock_get, \
             patch.object(budget_controller, '_emit_event') as mock_emit:
            
            mock_get.return_value = budget_controller.config
            
            result = budget_controller.update_config(**changes)
            
            assert result is True
            mock_update.assert_called_once_with(**changes)
            mock_emit.assert_called_once_with('config_changed', {
                'changes': changes,
                'new_config': budget_controller.config
            })
    
    def test_update_config_failure(self, budget_controller):
        """Test failed configuration update."""
        changes = {'invalid_key': 'value'}
        
        with patch('controllers.budget_controller.update_config', side_effect=Exception("Config error")), \
             patch.object(budget_controller, '_emit_event') as mock_emit:
            
            result = budget_controller.update_config(**changes)
            
            assert result is False
            mock_emit.assert_not_called()
    
    def test_save_config(self, budget_controller):
        """Test saving configuration."""
        with patch('controllers.budget_controller.save_config', return_value=True) as mock_save:
            result = budget_controller.save_config()
            
            assert result is True
            mock_save.assert_called_once()


class TestBudgetControllerExportOperations:
    """Test export and import operations."""
    
    def test_export_to_csv_success(self, budget_controller):
        """Test successful CSV export."""
        mock_export_data = {
            'categories': [
                {
                    'category': 'Groceries',
                    'percentage': 8.3,
                    'budgeted_amount': 250.0,
                    'actual_spent': 230.0,
                    'difference': 20.0,
                    'status': 'under_budget',
                    'is_fixed': False,
                    'description': 'Food expenses'
                }
            ],
            'summary': {
                'total_budgeted': 3000.0,
                'total_spent': 2800.0,
                'remaining': 200.0,
                'over_under': -200.0
            }
        }
        
        budget_controller.model.export_scenario_data.return_value = mock_export_data
        budget_controller.model.current_scenario_name = "Test Scenario"
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            with patch('csv.writer') as mock_csv_writer:
                mock_writer = Mock()
                mock_csv_writer.return_value = mock_writer
                
                result = budget_controller.export_to_csv()
                
                assert result is not None
                assert result.endswith('.csv')
                mock_writer.writerow.assert_called()  # Should have written rows
    
    def test_export_to_csv_with_custom_path(self, budget_controller):
        """Test CSV export with custom file path."""
        custom_path = "/custom/path/export.csv"
        mock_export_data = {'categories': [], 'summary': {}}
        
        budget_controller.model.export_scenario_data.return_value = mock_export_data
        
        with patch('builtins.open', create=True), \
             patch('csv.writer'):
            
            result = budget_controller.export_to_csv(custom_path)
            
            assert result == custom_path
    
    def test_export_to_csv_error(self, budget_controller):
        """Test CSV export with file error."""
        budget_controller.model.export_scenario_data.return_value = {'categories': [], 'summary': {}}
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            result = budget_controller.export_to_csv()
            
            assert result is None
    
    def test_get_spending_trends(self, budget_controller):
        """Test getting spending trends."""
        mock_trends = [
            {'category': 'Groceries', 'amount': 50.0, 'date': '2025-06-29'},
            {'category': 'Groceries', 'amount': 75.0, 'date': '2025-06-28'}
        ]
        
        budget_controller.model.get_spending_trends.return_value = mock_trends
        
        result = budget_controller.get_spending_trends("Groceries", 7)
        
        assert result == mock_trends
        budget_controller.model.get_spending_trends.assert_called_once_with("Groceries", 7)
    
    def test_get_database_stats(self, budget_controller):
        """Test getting database statistics."""
        mock_stats = {
            'budget_records': 10,
            'history_records': 25,
            'file_size_mb': 1.2
        }
        
        budget_controller.model.get_database_stats.return_value = mock_stats
        
        result = budget_controller.get_database_stats()
        
        assert result == mock_stats
        budget_controller.model.get_database_stats.assert_called_once()
    
    def test_backup_database(self, budget_controller):
        """Test creating database backup."""
        backup_path = "/backup/path.db"
        budget_controller.model.backup_data.return_value = True
        
        result = budget_controller.backup_database(backup_path)
        
        assert result is True
        budget_controller.model.backup_data.assert_called_once_with(backup_path)
    
    def test_get_category_suggestions(self, budget_controller):
        """Test getting category suggestions."""
        mock_suggestions = ["Medical", "Car Payment", "Insurance"]
        budget_controller.model.get_category_suggestions.return_value = mock_suggestions
        
        result = budget_controller.get_category_suggestions()
        
        assert result == mock_suggestions
        budget_controller.model.get_category_suggestions.assert_called_once()


class TestBudgetControllerCleanup:
    """Test controller cleanup operations."""
    
    def test_cleanup_with_pending_auto_save(self, budget_controller):
        """Test cleanup with pending auto-save."""
        # Mock pending auto-save
        mock_timer = Mock()
        budget_controller._auto_save_timer = mock_timer
        budget_controller._auto_save_pending = True
        
        with patch.object(budget_controller, 'save_data') as mock_save:
            budget_controller.cleanup()
            
            mock_timer.cancel.assert_called_once()
            mock_save.assert_called_once_with(show_message=False)
    
    def test_cleanup_without_pending_auto_save(self, budget_controller):
        """Test cleanup without pending auto-save."""
        budget_controller._auto_save_pending = False
        
        with patch.object(budget_controller, 'save_data') as mock_save:
            budget_controller.cleanup()
            
            mock_save.assert_not_called()
    
    def test_cleanup_with_no_timer(self, budget_controller):
        """Test cleanup when no timer exists."""
        budget_controller._auto_save_timer = None
        budget_controller._auto_save_pending = False
        
        # Should not raise error
        budget_controller.cleanup()


class TestBudgetControllerIntegration:
    """Integration tests for BudgetController with real components."""
    
    def test_full_workflow_integration(self, test_db_path, test_config):
        """Test complete workflow integration."""
        # Create real model and controller
        model = BudgetModel(test_db_path)
        
        with patch('controllers.budget_controller.get_config', return_value=test_config):
            controller = BudgetController(model)
        
        try:
            # Test scenario switching
            assert controller.switch_scenario("Fresh New Year (Jan-May)") is True
            assert controller.get_current_scenario_name() == "Fresh New Year (Jan-May)"
            
            # Test paycheck setting
            assert controller.set_paycheck_amount(4200.0) is True
            assert controller.get_paycheck_amount() == 4200.0
            
            # Test spending operations
            assert controller.set_actual_spending("Groceries", 275.0) is True
            assert controller.get_actual_spending("Groceries") == 275.0
            
            # Test budget calculations
            summary = controller.get_budget_summary()
            assert summary['paycheck_amount'] == 4200.0
            assert summary['categories']['Groceries']['actual_spent'] == 275.0
            
            # Test data persistence
            assert controller.save_data() is True
            
            # Test data loading
            assert controller.load_data() is True
            
        finally:
            controller.cleanup()
    
    def test_event_system_integration(self, test_db_path, test_config):
        """Test event system with real operations."""
        model = BudgetModel(test_db_path)
        
        with patch('controllers.budget_controller.get_config', return_value=test_config):
            controller = BudgetController(model)
        
        # Create mock callbacks
        scenario_callback = Mock()
        paycheck_callback = Mock()
        spending_callback = Mock()
        
        # Subscribe to events
        controller.subscribe_to_event('scenario_changed', scenario_callback)
        controller.subscribe_to_event('paycheck_changed', paycheck_callback)
        controller.subscribe_to_event('spending_changed', spending_callback)
        
        try:
            # Perform operations that should trigger events
            controller.switch_scenario("Fresh New Year (Jan-May)")
            controller.set_paycheck_amount(4000.0)
            controller.set_actual_spending("Groceries", 250.0)
            
            # Verify events were emitted
            scenario_callback.assert_called_once()
            paycheck_callback.assert_called_once()
            spending_callback.assert_called_once()
            
            # Verify event data
            scenario_data = scenario_callback.call_args[0][0]
            assert scenario_data['scenario_name'] == "Fresh New Year (Jan-May)"
            
            paycheck_data = paycheck_callback.call_args[0][0]
            assert paycheck_data['amount'] == 4000.0
            
            spending_data = spending_callback.call_args[0][0]
            assert spending_data['category'] == 'Groceries'
            assert spending_data['amount'] == 250.0
            
        finally:
            controller.cleanup()


class TestBudgetControllerPerformance:
    """Performance tests for BudgetController."""
    
    @pytest.mark.performance
    def test_auto_save_performance(self, budget_controller):
        """Test auto-save performance with multiple rapid changes."""
        import time
        
        budget_controller.config.auto_save = True
        
        with patch.object(budget_controller, 'save_data') as mock_save:
            # Make rapid changes
            start_time = time.time()
            for i in range(10):
                budget_controller.set_paycheck_amount(3000.0 + i)
                budget_controller.set_actual_spending("Groceries", 250.0 + i)
            
            # Wait for auto-save to complete
            time.sleep(3.0)
            operation_time = time.time() - start_time
            
            # Should have debounced saves (not 20 calls)
            assert mock_save.call_count < 10
            assert operation_time < 5.0
    
    @pytest.mark.performance
    def test_event_emission_performance(self, budget_controller):
        """Test performance with many event subscribers."""
        import time
        
        # Create many subscribers
        callbacks = [Mock() for _ in range(100)]
        for callback in callbacks:
            budget_controller.subscribe_to_event('spending_changed', callback)
        
        # Emit event and measure time
        start_time = time.time()
        budget_controller._emit_event('spending_changed', {'test': 'data'})
        emission_time = time.time() - start_time
        
        # Should complete quickly even with many subscribers
        assert emission_time < 0.1
        
        # Verify all callbacks were called
        for callback in callbacks:
            callback.assert_called_once_with({'test': 'data'})


class TestBudgetControllerErrorHandling:
    """Test error handling in BudgetController."""
    
    def test_model_operation_errors(self, budget_controller):
        """Test handling of model operation errors."""
        # Mock model methods to raise errors
        budget_controller.model.set_paycheck_amount.side_effect = Exception("Model error")
        budget_controller.model.set_actual_spending.side_effect = Exception("Model error")
        budget_controller.model.save_scenario_data.side_effect = Exception("Model error")
        
        # Operations should handle errors gracefully
        assert budget_controller.set_paycheck_amount(3000.0) is False
        assert budget_controller.set_actual_spending("Groceries", 250.0) is False
        assert budget_controller.save_data() is False
    
    def test_config_update_errors(self, budget_controller):
        """Test handling of configuration update errors."""
        with patch('controllers.budget_controller.update_config', side_effect=Exception("Config error")):
            result = budget_controller.update_config(theme='light')
            assert result is False
    
    def test_export_errors(self, budget_controller):
        """Test handling of export operation errors."""
        budget_controller.model.export_scenario_data.side_effect = Exception("Export error")
        
        result = budget_controller.export_to_csv()
        assert result is None
    
    def test_auto_save_errors(self, budget_controller):
        """Test handling of auto-save errors."""
        budget_controller._auto_save_pending = True
        
        with patch.object(budget_controller, 'save_data', side_effect=Exception("Save error")):
            # Should not raise error
            budget_controller._perform_auto_save()
            assert budget_controller._auto_save_pending is False


# Parametrized tests for comprehensive coverage
class TestBudgetControllerParametrized:
    """Parametrized tests for comprehensive coverage."""
    
    @pytest.mark.parametrize("scenario_name", [
        "July-December 2025",
        "Fresh New Year (Jan-May)",
        "Fresh New Year (June-Dec)"
    ])
    def test_all_scenarios_switching(self, budget_controller, scenario_name):
        """Test switching to all available scenarios."""
        budget_controller.model.set_current_scenario.return_value = True
        
        result = budget_controller.switch_scenario(scenario_name)
        assert result is True
        budget_controller.model.set_current_scenario.assert_called_with(scenario_name)
    
    @pytest.mark.parametrize("category,amount", [
        ("Groceries", 275.0),
        ("Utilities", 65.0),
        ("Entertainment", 0.0),
        ("Savings", 500.0),
    ])
    def test_spending_operations_various_categories(self, budget_controller, category, amount):
        """Test spending operations for various categories."""
        budget_controller.model.set_actual_spending.return_value = True
        budget_controller.model.get_actual_spending.return_value = amount
        
        # Test setting
        result = budget_controller.set_actual_spending(category, amount)
        assert result is True
        
        # Test getting
        result = budget_controller.get_actual_spending(category)
        assert result == amount
    
    @pytest.mark.parametrize("config_changes", [
        {'theme': 'light'},
        {'auto_save': True},
        {'currency_symbol': '€'},
        {'theme': 'dark', 'auto_save': False, 'decimal_places': 3}
    ])
    def test_config_updates_various_settings(self, budget_controller, config_changes):
        """Test configuration updates with various settings."""
        with patch('controllers.budget_controller.update_config') as mock_update, \
             patch('controllers.budget_controller.get_config') as mock_get:
            
            mock_get.return_value = budget_controller.config
            
            result = budget_controller.update_config(**config_changes)
            assert result is True
            mock_update.assert_called_once_with(**config_changes)


if __name__ == "__main__":
    # Run specific test classes for debugging
    pytest.main([__file__ + "::TestBudgetControllerInitialization", "-v"])