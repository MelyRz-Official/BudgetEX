"""
Pytest configuration and shared fixtures for Budget Manager tests.
Contains common test setup, fixtures, and utilities used across all test modules.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sqlite3
from typing import Dict, Any, Generator
import os
import sys

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.budget_model import BudgetModel, BudgetCategory, BudgetScenario
from models.database_manager import DatabaseManager
from controllers.budget_controller import BudgetController
from config import ConfigManager, AppConfig


@pytest.fixture(scope="session")
def test_config():
    """Create test configuration with safe defaults."""
    return AppConfig(
        theme="dark",
        window_width=800,
        window_height=600,
        default_scenario="Test Scenario",
        default_paycheck=3000.0,
        auto_save=False,
        auto_backup=False,
        database_filename=":memory:",  # Use in-memory DB for tests
        backup_directory="test_backups",
        export_directory="test_exports",
        currency_symbol="$",
        decimal_places=2
    )


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_db_path(temp_dir):
    """Create a temporary database file path."""
    return str(temp_dir / "test_budget.db")


@pytest.fixture
def clean_database(test_db_path):
    """Create a clean database for testing."""
    # Ensure clean state
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)
    
    yield test_db_path
    
    # Cleanup after test
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)


@pytest.fixture
def database_manager(clean_database):
    """Create a DatabaseManager instance for testing."""
    db = DatabaseManager(clean_database)
    yield db
    db.close()


@pytest.fixture
def sample_budget_data():
    """Sample budget data for testing."""
    return {
        "Groceries": 250.0,
        "Utilities": 60.0,
        "Entertainment": 100.0,
        "Savings": 500.0,
        "Rent": 1200.0
    }


@pytest.fixture
def sample_categories():
    """Sample budget categories for testing."""
    return {
        "Groceries": BudgetCategory("Groceries", 250.0, 8.3, False, "Food expenses"),
        "Utilities": BudgetCategory("Utilities", 60.0, 2.0, True, "Fixed utilities"),
        "Entertainment": BudgetCategory("Entertainment", 100.0, 3.3, False, "Fun activities"),
        "Savings": BudgetCategory("Savings", 500.0, 16.7, False, "Emergency fund"),
        "Rent": BudgetCategory("Rent", 1200.0, 40.0, True, "Monthly rent")
    }


@pytest.fixture
def sample_scenario(sample_categories):
    """Sample budget scenario for testing."""
    return BudgetScenario(
        name="Test Scenario",
        categories=sample_categories,
        default_paycheck=3000.0,
        description="Test scenario for unit tests"
    )


@pytest.fixture
def budget_model(test_db_path):
    """Create a BudgetModel instance for testing."""
    model = BudgetModel(test_db_path)
    yield model
    # Cleanup is handled by clean_database fixture


@pytest.fixture
def budget_controller(budget_model, test_config):
    """Create a BudgetController instance for testing."""
    # Mock config manager to use test config
    with patch('controllers.budget_controller.get_config', return_value=test_config):
        controller = BudgetController(budget_model)
        yield controller
        controller.cleanup()


@pytest.fixture
def populated_database(database_manager, sample_budget_data):
    """Database with sample data populated."""
    # Add sample scenario data
    database_manager.save_budget_data("Test Scenario", 3000.0, sample_budget_data)
    
    # Add some spending history
    database_manager.add_spending_history("Test Scenario", "Groceries", 45.50, "Weekly shopping")
    database_manager.add_spending_history("Test Scenario", "Entertainment", 25.00, "Movie tickets")
    
    return database_manager


@pytest.fixture
def mock_config_manager(test_config):
    """Mock configuration manager for testing."""
    mock_manager = Mock(spec=ConfigManager)
    mock_manager.config = test_config
    mock_manager.get.side_effect = lambda key, default=None: getattr(test_config, key, default)
    mock_manager.set.return_value = True
    mock_manager.save_config.return_value = True
    return mock_manager


# Parametrized fixtures for testing different scenarios
@pytest.fixture(params=[
    ("July-December 2025", 3984.94),
    ("Fresh New Year (Jan-May)", 4200.0),
    ("Fresh New Year (June-Dec)", 3800.0)
])
def scenario_paycheck_combinations(request):
    """Parametrized fixture for different scenario/paycheck combinations."""
    scenario_name, paycheck_amount = request.param
    return scenario_name, paycheck_amount


@pytest.fixture(params=[0.0, 50.0, 100.0, 150.0, 250.0])
def spending_amounts(request):
    """Parametrized fixture for different spending amounts."""
    return request.param


@pytest.fixture(params=["light", "dark"])
def theme_options(request):
    """Parametrized fixture for theme testing."""
    return request.param


# Database state fixtures
@pytest.fixture
def empty_database_state():
    """Fixture representing empty database state."""
    return {
        'budget_records': 0,
        'history_records': 0,
        'scenarios': []
    }


@pytest.fixture
def populated_database_state():
    """Fixture representing populated database state."""
    return {
        'budget_records': 5,
        'history_records': 10,
        'scenarios': ["Test Scenario", "Another Scenario"]
    }


# Mock external dependencies
@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing export/import functionality."""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.path.exists', return_value=True) as mock_exists, \
         patch('shutil.copy2') as mock_copy:
        
        mock_open.return_value.__enter__.return_value.write.return_value = None
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'copy': mock_copy
        }


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    from freezegun import freeze_time
    with freeze_time("2025-06-30 12:00:00"):
        yield


# Performance testing fixtures
@pytest.fixture
def large_dataset():
    """Generate large dataset for performance testing."""
    categories = {}
    for i in range(100):
        categories[f"Category_{i}"] = BudgetCategory(
            f"Category_{i}", 
            float(i * 10), 
            float(i * 0.5), 
            i % 2 == 0,  # Every other category is fixed
            f"Description for category {i}"
        )
    return categories


@pytest.fixture
def performance_scenario(large_dataset):
    """Large scenario for performance testing."""
    return BudgetScenario(
        name="Performance Test Scenario",
        categories=large_dataset,
        default_paycheck=50000.0,
        description="Large scenario for performance testing"
    )


# Error simulation fixtures
@pytest.fixture
def mock_database_error():
    """Mock database error for error handling tests."""
    with patch('sqlite3.connect', side_effect=sqlite3.Error("Mocked database error")):
        yield


@pytest.fixture
def mock_file_permission_error():
    """Mock file permission error for testing error handling."""
    with patch('builtins.open', side_effect=PermissionError("Mocked permission error")):
        yield


# Helper functions for tests
def assert_budget_summary_valid(summary: Dict[str, Any]):
    """Assert that a budget summary has all required fields and valid values."""
    assert 'scenario_name' in summary
    assert 'paycheck_amount' in summary
    assert 'categories' in summary
    assert 'totals' in summary
    assert 'validation_errors' in summary
    
    # Check totals structure
    totals = summary['totals']
    assert 'total_budgeted' in totals
    assert 'total_spent' in totals
    assert 'remaining' in totals
    assert 'over_under' in totals
    assert 'budget_utilization' in totals
    
    # Check that values are numeric
    assert isinstance(totals['total_budgeted'], (int, float))
    assert isinstance(totals['total_spent'], (int, float))
    assert isinstance(totals['remaining'], (int, float))
    assert isinstance(totals['over_under'], (int, float))
    assert isinstance(totals['budget_utilization'], (int, float))


def create_test_spending_data(categories: Dict[str, BudgetCategory], 
                            spending_ratio: float = 0.8) -> Dict[str, float]:
    """
    Create test spending data based on categories.
    
    Args:
        categories: Dictionary of budget categories.
        spending_ratio: Ratio of budgeted amount to spend (0.0 to 1.5).
        
    Returns:
        Dictionary of category -> spending amount.
    """
    paycheck = 3000.0
    spending_data = {}
    
    for name, category in categories.items():
        budgeted = category.calculate_budgeted_amount(paycheck)
        spending_data[name] = budgeted * spending_ratio
    
    return spending_data


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "acceptance: Acceptance tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add smoke marker to quick tests
        if "quick" in item.name or "smoke" in item.name:
            item.add_marker(pytest.mark.smoke)
        
        # Add slow marker to performance tests
        if "performance" in str(item.fspath) or "benchmark" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add database marker to database tests
        if "database" in str(item.fspath) or "db" in item.name:
            item.add_marker(pytest.mark.database)


# Module-level test data
TEST_SCENARIOS = [
    "July-December 2025",
    "Fresh New Year (Jan-May)", 
    "Fresh New Year (June-Dec)"
]

TEST_CATEGORIES = [
    "Groceries", "Utilities", "Entertainment", 
    "Savings", "Rent", "Transportation"
]

VALID_PAYCHECK_AMOUNTS = [1000.0, 2500.0, 3984.94, 5000.0, 10000.0]
INVALID_PAYCHECK_AMOUNTS = [-100.0, 0.0, "invalid", None]

VALID_SPENDING_AMOUNTS = [0.0, 25.50, 100.0, 500.0]
INVALID_SPENDING_AMOUNTS = [-50.0, "invalid", None]