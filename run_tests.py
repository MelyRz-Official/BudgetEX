#!/usr/bin/env python3
"""
Simple test runner for Budget Manager tests.
Run this script to execute tests without complex pytest setup.
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_simple_tests():
    """Run simple unit tests to verify basic functionality."""
    print("🧪 Running Budget Manager Tests")
    print("=" * 50)
    
    try:
        # Test 1: Configuration System
        print("\n1️⃣ Testing Configuration System...")
        from config import AppConfig, ConfigManager
        
        # Test basic config creation
        config = AppConfig()
        assert config.theme == "dark"
        assert config.currency_symbol == "$"
        print("   ✅ AppConfig creation successful")
        
        # Test config manager
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            manager = ConfigManager(tmp.name)
            assert manager.config.theme == "dark"
            print("   ✅ ConfigManager initialization successful")
        
        print("   🎉 Configuration tests PASSED!")
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False
    
    try:
        # Test 2: Database Manager
        print("\n2️⃣ Testing Database Manager...")
        from models.database_manager import DatabaseManager
        
        # Test database creation
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db = DatabaseManager(tmp.name)
            
            # Test basic operations
            sample_data = {"Groceries": 250.0, "Utilities": 60.0}
            success = db.save_budget_data("Test Scenario", 3000.0, sample_data)
            assert success is True
            print("   ✅ Database save successful")
            
            # Test loading
            result = db.load_budget_data("Test Scenario")
            assert result is not None
            paycheck, spending = result
            assert paycheck == 3000.0
            assert spending["Groceries"] == 250.0
            print("   ✅ Database load successful")
            
            db.close()
        
        print("   🎉 Database tests PASSED!")
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False
    
    try:
        # Test 3: Budget Model
        print("\n3️⃣ Testing Budget Model...")
        from models.budget_model import BudgetModel, BudgetCategory
        
        # Test category creation
        category = BudgetCategory("Test", 100.0, 10.0, False, "Test category")
        assert category.name == "Test"
        assert category.calculate_budgeted_amount(1000.0) == 100.0
        print("   ✅ BudgetCategory creation successful")
        
        # Test model initialization
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            model = BudgetModel(tmp.name)
            assert len(model.scenarios) == 3
            assert model.current_scenario_name == "July-December 2025"
            print("   ✅ BudgetModel initialization successful")
            
            # Test basic operations
            result = model.set_paycheck_amount(4000.0)
            assert result is True
            assert model.current_paycheck == 4000.0
            print("   ✅ Paycheck setting successful")
            
            # Test spending operations
            result = model.set_actual_spending("Groceries", 275.0)
            assert result is True
            assert model.get_actual_spending("Groceries") == 275.0
            print("   ✅ Spending operations successful")
        
        print("   🎉 Budget Model tests PASSED!")
        
    except Exception as e:
        print(f"   ❌ Budget Model test failed: {e}")
        return False
    
    try:
        # Test 4: Budget Controller
        print("\n4️⃣ Testing Budget Controller...")
        from controllers.budget_controller import BudgetController
        from models.budget_model import BudgetModel
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            model = BudgetModel(tmp.name)
            controller = BudgetController(model)
            
            # Test basic controller operations
            scenarios = controller.get_available_scenarios()
            assert len(scenarios) == 3
            print("   ✅ Controller scenario retrieval successful")
            
            # Test paycheck operations
            result = controller.set_paycheck_amount(3500.0)
            assert result is True
            assert controller.get_paycheck_amount() == 3500.0
            print("   ✅ Controller paycheck operations successful")
            
            # Test spending operations
            result = controller.set_actual_spending("Groceries", 280.0)
            assert result is True
            assert controller.get_actual_spending("Groceries") == 280.0
            print("   ✅ Controller spending operations successful")
            
            # Test summary generation
            summary = controller.get_budget_summary()
            assert 'totals' in summary
            assert 'categories' in summary
            print("   ✅ Budget summary generation successful")
            
            controller.cleanup()
        
        print("   🎉 Budget Controller tests PASSED!")
        
    except Exception as e:
        print(f"   ❌ Budget Controller test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! 🎉")
    print("Your Budget Manager is working correctly!")
    print("=" * 50)
    return True

def run_integration_test():
    """Run a complete integration test."""
    print("\n🔄 Running Integration Test...")
    
    try:
        import tempfile
        from models.budget_model import BudgetModel
        from controllers.budget_controller import BudgetController
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            # Create full system
            model = BudgetModel(tmp.name)
            controller = BudgetController(model)
            
            # Test complete workflow
            print("   📊 Testing complete workflow...")
            
            # 1. Switch scenario
            result = controller.switch_scenario("Fresh New Year (Jan-May)")
            assert result is True
            
            # 2. Set paycheck
            result = controller.set_paycheck_amount(4200.0)
            assert result is True
            
            # 3. Set some spending
            spending_data = {
                "Groceries": 320.0,
                "Utilities": 65.0,
                "Roth IRA": 1400.0
            }
            
            for category, amount in spending_data.items():
                result = controller.set_actual_spending(category, amount)
                assert result is True
            
            # 4. Get summary
            summary = controller.get_budget_summary()
            assert summary['paycheck_amount'] == 4200.0
            assert summary['totals']['total_spent'] == sum(spending_data.values())
            
            # 5. Save data
            result = controller.save_data()
            assert result is True
            
            # 6. Load data
            result = controller.load_data()
            assert result is True
            
            controller.cleanup()
            
        print("   ✅ Integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Budget Manager Test Suite")
    print("Starting comprehensive testing...")
    
    # Run basic unit tests
    unit_success = run_simple_tests()
    
    if unit_success:
        # Run integration test
        integration_success = run_integration_test()
        
        if integration_success:
            print("\n🏆 CONGRATULATIONS! 🏆")
            print("All systems are working perfectly!")
            print("Your Budget Manager is ready for production!")
        else:
            print("\n⚠️ Integration tests failed")
            sys.exit(1)
    else:
        print("\n⚠️ Unit tests failed")
        sys.exit(1)