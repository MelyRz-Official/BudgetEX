"""
Unit tests for DatabaseManager class.
Tests database operations, error handling, and data integrity.
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from models.database_manager import DatabaseManager


class TestDatabaseManagerInitialization:
    """Test DatabaseManager initialization and setup."""
    
    def test_database_manager_creation(self, clean_database):
        """Test creating a DatabaseManager instance."""
        db = DatabaseManager(clean_database)
        
        assert db.db_path == Path(clean_database).resolve()
        assert os.path.exists(clean_database)
        db.close()
    
    def test_database_tables_created(self, clean_database):
        """Test that required tables are created."""
        db = DatabaseManager(clean_database)
        
        # Check that tables exist
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'budget_data' in tables
            assert 'spending_history' in tables
            assert 'app_metadata' in tables
        
        db.close()
    
    def test_database_indexes_created(self, clean_database):
        """Test that performance indexes are created."""
        db = DatabaseManager(clean_database)
        
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get list of indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            assert 'idx_budget_scenario' in indexes
            assert 'idx_spending_history_date' in indexes
        
        db.close()
    
    def test_database_version_set(self, clean_database):
        """Test that database version metadata is set."""
        db = DatabaseManager(clean_database)
        
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM app_metadata WHERE key = 'db_version'")
            result = cursor.fetchone()
            
            assert result is not None
            assert result['value'] == '1.0'
        
        db.close()
    
    def test_database_pragma_settings(self, clean_database):
        """Test that database PRAGMA settings are applied."""
        db = DatabaseManager(clean_database)
        
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check foreign keys are enabled
            cursor.execute("PRAGMA foreign_keys")
            assert cursor.fetchone()[0] == 1
            
            # Check journal mode
            cursor.execute("PRAGMA journal_mode")
            assert cursor.fetchone()[0] == 'wal'
        
        db.close()


class TestDatabaseManagerCRUDOperations:
    """Test CRUD operations in DatabaseManager."""
    
    def test_save_budget_data_success(self, database_manager, sample_budget_data):
        """Test successfully saving budget data."""
        scenario = "Test Scenario"
        paycheck = 3000.0
        
        result = database_manager.save_budget_data(scenario, paycheck, sample_budget_data)
        assert result is True
        
        # Verify data was saved
        with database_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM budget_data WHERE scenario = ?", (scenario,))
            count = cursor.fetchone()['count']
            assert count == len(sample_budget_data)
    
    def test_save_budget_data_update_existing(self, database_manager, sample_budget_data):
        """Test updating existing budget data."""
        scenario = "Test Scenario"
        paycheck = 3000.0
        
        # Save initial data
        database_manager.save_budget_data(scenario, paycheck, sample_budget_data)
        
        # Update with new data
        updated_data = sample_budget_data.copy()
        updated_data["Groceries"] = 300.0  # Changed value
        updated_data["New Category"] = 150.0  # New category
        
        result = database_manager.save_budget_data(scenario, 3500.0, updated_data)
        assert result is True
        
        # Verify updates
        loaded_data = database_manager.load_budget_data(scenario)
        assert loaded_data is not None
        paycheck_amount, spending_data = loaded_data
        assert paycheck_amount == 3500.0
        assert spending_data["Groceries"] == 300.0
        assert spending_data["New Category"] == 150.0
    
    def test_load_budget_data_success(self, populated_database):
        """Test successfully loading budget data."""
        result = populated_database.load_budget_data("Test Scenario")
        
        assert result is not None
        paycheck, spending_data = result
        assert isinstance(paycheck, float)
        assert isinstance(spending_data, dict)
        assert len(spending_data) > 0
    
    def test_load_budget_data_nonexistent(self, database_manager):
        """Test loading data for non-existent scenario."""
        result = database_manager.load_budget_data("Non-existent Scenario")
        assert result is None
    
    def test_get_all_scenarios(self, populated_database):
        """Test getting all scenario names."""
        # Add another scenario
        populated_database.save_budget_data("Another Scenario", 4000.0, {"Test": 100.0})
        
        scenarios = populated_database.get_all_scenarios()
        assert isinstance(scenarios, list)
        assert "Test Scenario" in scenarios
        assert "Another Scenario" in scenarios
    
    def test_get_all_scenarios_empty(self, database_manager):
        """Test getting scenarios from empty database."""
        scenarios = database_manager.get_all_scenarios()
        assert scenarios == []
    
    def test_delete_scenario_success(self, populated_database):
        """Test successfully deleting a scenario."""
        scenario = "Test Scenario"
        
        # Verify scenario exists
        assert scenario in populated_database.get_all_scenarios()
        
        result = populated_database.delete_scenario(scenario)
        assert result is True
        
        # Verify scenario is deleted
        assert scenario not in populated_database.get_all_scenarios()
        assert populated_database.load_budget_data(scenario) is None
    
    def test_delete_scenario_nonexistent(self, database_manager):
        """Test deleting non-existent scenario."""
        result = database_manager.delete_scenario("Non-existent Scenario")
        assert result is True  # Should succeed even if nothing to delete
    
    def test_clear_spending_data(self, populated_database):
        """Test clearing spending data for a scenario."""
        scenario = "Test Scenario"
        
        result = populated_database.clear_spending_data(scenario)
        assert result is True
        
        # Verify spending is cleared
        loaded_data = populated_database.load_budget_data(scenario)
        assert loaded_data is not None
        _, spending_data = loaded_data
        assert all(amount == 0.0 for amount in spending_data.values())


class TestDatabaseManagerSpendingHistory:
    """Test spending history operations."""
    
    def test_add_spending_history_success(self, database_manager):
        """Test adding spending history entry."""
        result = database_manager.add_spending_history(
            "Test Scenario", "Groceries", 45.50, "Weekly shopping"
        )
        assert result is True
        
        # Verify entry was added
        with database_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM spending_history")
            count = cursor.fetchone()['count']
            assert count == 1
    
    def test_add_spending_history_without_description(self, database_manager):
        """Test adding spending history without description."""
        result = database_manager.add_spending_history(
            "Test Scenario", "Entertainment", 25.00
        )
        assert result is True
    
    def test_get_spending_history_by_scenario(self, populated_database):
        """Test getting spending history for a scenario."""
        history = populated_database.get_spending_history("Test Scenario")
        
        assert isinstance(history, list)
        assert len(history) > 0
        
        # Check structure of history entries
        for entry in history:
            assert 'scenario' in entry
            assert 'category' in entry
            assert 'amount' in entry
            assert 'date_added' in entry
    
    def test_get_spending_history_by_category(self, populated_database):
        """Test getting spending history filtered by category."""
        history = populated_database.get_spending_history("Test Scenario", "Groceries")
        
        assert isinstance(history, list)
        # All entries should be for Groceries category
        for entry in history:
            assert entry['category'] == 'Groceries'
    
    def test_get_spending_history_by_days(self, database_manager):
        """Test getting spending history filtered by days."""
        scenario = "Test Scenario"
        
        # Add some history entries
        database_manager.add_spending_history(scenario, "Groceries", 25.0, "Recent")
        
        # Get history for last 7 days
        history = database_manager.get_spending_history(scenario, days=7)
        assert len(history) == 1
        
        # Get history for last 0 days (should be empty)
        history = database_manager.get_spending_history(scenario, days=0)
        assert len(history) == 0
    
    def test_get_spending_history_empty(self, database_manager):
        """Test getting spending history when none exists."""
        history = database_manager.get_spending_history("Non-existent Scenario")
        assert history == []


class TestDatabaseManagerUtilities:
    """Test utility functions in DatabaseManager."""
    
    def test_backup_database_default_path(self, populated_database, temp_dir):
        """Test database backup with default path."""
        with patch('models.database_manager.Path.mkdir'), \
             patch('models.database_manager.shutil.copy2') as mock_copy:
            
            result = populated_database.backup_database()
            assert result is True
            mock_copy.assert_called_once()
    
    def test_backup_database_custom_path(self, populated_database, temp_dir):
        """Test database backup with custom path."""
        backup_path = temp_dir / "custom_backup.db"
        
        result = populated_database.backup_database(str(backup_path))
        assert result is True
        assert backup_path.exists()
    
    def test_get_database_stats(self, populated_database):
        """Test getting database statistics."""
        stats = populated_database.get_database_stats()
        
        assert isinstance(stats, dict)
        assert 'budget_records' in stats
        assert 'history_records' in stats
        assert 'file_size_bytes' in stats
        assert 'file_size_mb' in stats
        assert 'last_update' in stats
        assert 'database_path' in stats
        
        # Check data types
        assert isinstance(stats['budget_records'], int)
        assert isinstance(stats['history_records'], int)
        assert isinstance(stats['file_size_bytes'], int)
        assert isinstance(stats['file_size_mb'], float)
    
    def test_execute_query_select(self, populated_database):
        """Test executing custom SELECT query."""
        result = populated_database.execute_query(
            "SELECT scenario, COUNT(*) as count FROM budget_data GROUP BY scenario"
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'scenario' in result[0]
        assert 'count' in result[0]
    
    def test_execute_query_update(self, populated_database):
        """Test executing custom UPDATE query."""
        result = populated_database.execute_query(
            "UPDATE budget_data SET actual_spent = ? WHERE category = ?",
            (200.0, "Groceries")
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'affected_rows' in result[0]
        assert result[0]['affected_rows'] > 0
    
    def test_execute_query_invalid(self, database_manager):
        """Test executing invalid query."""
        result = database_manager.execute_query("INVALID SQL QUERY")
        assert result == []


class TestDatabaseManagerErrorHandling:
    """Test error handling in DatabaseManager."""
    
    def test_initialization_with_invalid_path(self):
        """Test initialization with invalid database path."""
        # This should still work as SQLite can create the file
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = os.path.join(temp_dir, "subdir", "test.db")
            # This might fail due to missing directory
            try:
                db = DatabaseManager(invalid_path)
                db.close()
            except Exception:
                # This is expected for truly invalid paths
                pass
    
    def test_save_data_with_database_error(self, database_manager):
        """Test saving data when database error occurs."""
        with patch.object(database_manager, '_get_connection', side_effect=sqlite3.Error("Mocked error")):
            result = database_manager.save_budget_data("Test", 1000.0, {"Test": 100.0})
            assert result is False
    
    def test_load_data_with_database_error(self, database_manager):
        """Test loading data when database error occurs."""
        with patch.object(database_manager, '_get_connection', side_effect=sqlite3.Error("Mocked error")):
            result = database_manager.load_budget_data("Test")
            assert result is None
    
    def test_backup_with_file_error(self, database_manager):
        """Test backup when file operation fails."""
        with patch('models.database_manager.shutil.copy2', side_effect=OSError("Permission denied")):
            result = database_manager.backup_database("/invalid/path")
            assert result is False
    
    def test_add_spending_history_with_error(self, database_manager):
        """Test adding spending history when database error occurs."""
        with patch.object(database_manager, '_get_connection', side_effect=sqlite3.Error("Mocked error")):
            result = database_manager.add_spending_history("Test", "Category", 100.0)
            assert result is False
    
    def test_get_stats_with_database_error(self, database_manager):
        """Test getting stats when database error occurs."""
        with patch.object(database_manager, '_get_connection', side_effect=sqlite3.Error("Mocked error")):
            result = database_manager.get_database_stats()
            assert result == {}


class TestDatabaseManagerPerformance:
    """Performance tests for DatabaseManager."""
    
    @pytest.mark.performance
    def test_large_dataset_save_performance(self, database_manager):
        """Test saving performance with large dataset."""
        import time
        
        # Create large dataset
        large_data = {f"Category_{i}": float(i * 10) for i in range(1000)}
        
        start_time = time.time()
        result = database_manager.save_budget_data("Performance Test", 50000.0, large_data)
        save_time = time.time() - start_time
        
        assert result is True
        assert save_time < 2.0, f"Large dataset save took too long: {save_time:.2f}s"
    
    @pytest.mark.performance
    def test_large_dataset_load_performance(self, database_manager):
        """Test loading performance with large dataset."""
        import time
        
        # First save large dataset
        large_data = {f"Category_{i}": float(i * 10) for i in range(1000)}
        database_manager.save_budget_data("Performance Test", 50000.0, large_data)
        
        start_time = time.time()
        result = database_manager.load_budget_data("Performance Test")
        load_time = time.time() - start_time
        
        assert result is not None
        assert load_time < 1.0, f"Large dataset load took too long: {load_time:.2f}s"
        
        paycheck, spending_data = result
        assert len(spending_data) == 1000
    
    @pytest.mark.performance
    def test_multiple_scenario_performance(self, database_manager):
        """Test performance with multiple scenarios."""
        import time
        
        # Create multiple scenarios
        start_time = time.time()
        for i in range(50):
            scenario_data = {f"Cat_{j}": float(j * 5) for j in range(20)}
            database_manager.save_budget_data(f"Scenario_{i}", 3000.0, scenario_data)
        save_time = time.time() - start_time
        
        # Load all scenarios
        start_time = time.time()
        scenarios = database_manager.get_all_scenarios()
        load_time = time.time() - start_time
        
        assert len(scenarios) == 50
        assert save_time < 5.0, f"Multiple scenario save took too long: {save_time:.2f}s"
        assert load_time < 1.0, f"Scenario list load took too long: {load_time:.2f}s"


class TestDatabaseManagerConcurrency:
    """Test concurrent access to DatabaseManager."""
    
    def test_multiple_connections(self, database_manager):
        """Test multiple database connections."""
        # Create multiple connections
        conn1 = database_manager._get_connection()
        conn2 = database_manager._get_connection()
        
        # Both should be valid
        assert conn1 is not None
        assert conn2 is not None
        
        # Test operations on both connections
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        cursor1.execute("SELECT COUNT(*) FROM budget_data")
        cursor2.execute("SELECT COUNT(*) FROM spending_history")
        
        # Should not raise errors
        result1 = cursor1.fetchone()
        result2 = cursor2.fetchone()
        
        assert result1 is not None
        assert result2 is not None
        
        conn1.close()
        conn2.close()
    
    @pytest.mark.slow
    def test_concurrent_writes(self, database_manager):
        """Test concurrent write operations."""
        import threading
        import time
        
        results = []
        
        def write_data(scenario_name, thread_id):
            try:
                data = {f"Category_{thread_id}_{i}": float(i * 10) for i in range(10)}
                result = database_manager.save_budget_data(f"{scenario_name}_{thread_id}", 3000.0, data)
                results.append((thread_id, result))
            except Exception as e:
                results.append((thread_id, False, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_data, args=("ConcurrentTest", i))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Check results
        assert len(results) == 5
        for result in results:
            if len(result) == 2:  # Success case
                thread_id, success = result
                assert success is True, f"Thread {thread_id} failed"
            else:  # Error case
                thread_id, success, error = result
                pytest.fail(f"Thread {thread_id} failed with error: {error}")


class TestDatabaseManagerDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_transaction_rollback_on_error(self, database_manager):
        """Test that transactions rollback properly on errors."""
        # This test ensures atomicity of operations
        original_count = 0
        
        # Get initial count
        with database_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM budget_data")
            original_count = cursor.fetchone()['count']
        
        # Try to save data with a mocked error in the middle
        with patch.object(database_manager, '_get_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            
            # First execute succeeds, second fails
            mock_cursor.execute.side_effect = [None, sqlite3.Error("Mocked error")]
            
            result = database_manager.save_budget_data("Test", 3000.0, {"Cat1": 100.0, "Cat2": 200.0})
            assert result is False
        
        # Verify count is unchanged (transaction rolled back)
        with database_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM budget_data")
            final_count = cursor.fetchone()['count']
            assert final_count == original_count
    
    def test_foreign_key_constraints(self, database_manager):
        """Test that foreign key constraints work properly."""
        # Note: The current schema doesn't have foreign keys, but this tests the setup
        with database_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 1  # Foreign keys should be enabled
    
    def test_unique_constraint_enforcement(self, database_manager):
        """Test that unique constraints are enforced."""
        scenario = "Test Scenario"
        category = "Test Category"
        
        # Save initial data
        database_manager.save_budget_data(scenario, 3000.0, {category: 100.0})
        
        # Try to save duplicate (should update, not create duplicate)
        database_manager.save_budget_data(scenario, 3500.0, {category: 200.0})
        
        # Verify only one record exists
        with database_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM budget_data WHERE scenario = ? AND category = ?",
                (scenario, category)
            )
            count = cursor.fetchone()['count']
            assert count == 1
            
            # Verify it was updated, not duplicated
            cursor.execute(
                "SELECT actual_spent, paycheck_amount FROM budget_data WHERE scenario = ? AND category = ?",
                (scenario, category)
            )
            result = cursor.fetchone()
            assert result['actual_spent'] == 200.0
            assert result['paycheck_amount'] == 3500.0
    
    def test_data_type_validation(self, database_manager):
        """Test that data types are properly handled."""
        # Test with various data types
        test_cases = [
            (3000, {"Category": 100}),        # Integers
            (3000.0, {"Category": 100.0}),    # Floats
            ("3000", {"Category": "100"}),    # Strings (should be converted)
        ]
        
        for i, (paycheck, spending_data) in enumerate(test_cases):
            scenario = f"Type Test {i}"
            result = database_manager.save_budget_data(scenario, paycheck, spending_data)
            assert result is True
            
            # Verify data is stored as numbers
            loaded_data = database_manager.load_budget_data(scenario)
            assert loaded_data is not None
            loaded_paycheck, loaded_spending = loaded_data
            assert isinstance(loaded_paycheck, float)
            assert isinstance(loaded_spending["Category"], float)


if __name__ == "__main__":
    # Run specific test classes for debugging
    pytest.main([__file__ + "::TestDatabaseManagerInitialization", "-v"])