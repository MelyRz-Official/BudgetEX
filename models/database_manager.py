"""
Database management layer for the Budget Manager application.
Handles all database operations including connection, CRUD operations, and migrations.
"""

import sqlite3
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import shutil


class DatabaseManager:
    """Manages all database operations for the budget application."""
    
    def __init__(self, db_path: str = "budget_data.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path).resolve()
        self.connection_pool = {}
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database with required tables and indexes."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create budget_data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS budget_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scenario TEXT NOT NULL,
                        paycheck_amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        actual_spent REAL NOT NULL DEFAULT 0.0,
                        date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(scenario, category)
                    )
                ''')
                
                # Create spending_history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS spending_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scenario TEXT NOT NULL,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT,
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create app_metadata table for versioning and settings
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS app_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_budget_scenario 
                    ON budget_data(scenario)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_spending_history_date 
                    ON spending_history(date_added)
                ''')
                
                # Set database version if not exists
                cursor.execute('''
                    INSERT OR IGNORE INTO app_metadata (key, value) 
                    VALUES ('db_version', '1.0')
                ''')
                
                conn.commit()
                
        except Exception as e:
            raise Exception(f"Failed to initialize database: {str(e)}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection with optimized settings.
        
        Returns:
            SQLite connection object.
        """
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0
        )
        
        # Enable foreign keys and WAL mode for better performance
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        
        # Enable row factory for easier data access
        conn.row_factory = sqlite3.Row
        
        return conn
    
    def save_budget_data(self, scenario: str, paycheck_amount: float, 
                        spending_data: Dict[str, float]) -> bool:
        """
        Save budget data for a specific scenario.
        
        Args:
            scenario: Budget scenario name.
            paycheck_amount: Total paycheck amount.
            spending_data: Dictionary of category -> actual_spent amounts.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                for category, actual_spent in spending_data.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO budget_data 
                        (scenario, paycheck_amount, category, actual_spent, date_updated)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (scenario, paycheck_amount, category, float(actual_spent)))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving budget data: {str(e)}")
            return False
    
    def load_budget_data(self, scenario: str) -> Optional[Tuple[float, Dict[str, float]]]:
        """
        Load budget data for a specific scenario.
        
        Args:
            scenario: Budget scenario name.
            
        Returns:
            Tuple of (paycheck_amount, spending_data) or None if not found.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT category, actual_spent, paycheck_amount 
                    FROM budget_data 
                    WHERE scenario = ?
                    ORDER BY category
                ''', (scenario,))
                
                results = cursor.fetchall()
                
                if not results:
                    return None
                
                paycheck_amount = float(results[0]['paycheck_amount'])
                spending_data = {
                    row['category']: float(row['actual_spent']) 
                    for row in results
                }
                
                return paycheck_amount, spending_data
                
        except Exception as e:
            print(f"Error loading budget data: {str(e)}")
            return None
    
    def get_all_scenarios(self) -> List[str]:
        """
        Get list of all budget scenarios in the database.
        
        Returns:
            List of scenario names.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT DISTINCT scenario 
                    FROM budget_data 
                    ORDER BY scenario
                ''')
                
                return [row['scenario'] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting scenarios: {str(e)}")
            return []
    
    def add_spending_history(self, scenario: str, category: str, 
                           amount: float, description: str = None) -> bool:
        """
        Add entry to spending history.
        
        Args:
            scenario: Budget scenario name.
            category: Spending category.
            amount: Amount spent.
            description: Optional description.
            
        Returns:
            bool: True if successful.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO spending_history 
                    (scenario, category, amount, description, date_added)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (scenario, category, amount, description))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error adding spending history: {str(e)}")
            return False
    
    def get_spending_history(self, scenario: str, category: str = None, 
                           days: int = 30) -> List[Dict[str, Any]]:
        """
        Get spending history for a scenario and optional category.
        
        Args:
            scenario: Budget scenario name.
            category: Optional category filter.
            days: Number of days to look back.
            
        Returns:
            List of spending history records.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if category:
                    cursor.execute('''
                        SELECT * FROM spending_history 
                        WHERE scenario = ? AND category = ?
                        AND date_added >= date('now', '-{} days')
                        ORDER BY date_added DESC
                    '''.format(days), (scenario, category))
                else:
                    cursor.execute('''
                        SELECT * FROM spending_history 
                        WHERE scenario = ?
                        AND date_added >= date('now', '-{} days')
                        ORDER BY date_added DESC
                    '''.format(days), (scenario,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting spending history: {str(e)}")
            return []
    
    def delete_scenario(self, scenario: str) -> bool:
        """
        Delete all data for a specific scenario.
        
        Args:
            scenario: Budget scenario name to delete.
            
        Returns:
            bool: True if successful.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM budget_data WHERE scenario = ?', (scenario,))
                cursor.execute('DELETE FROM spending_history WHERE scenario = ?', (scenario,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error deleting scenario: {str(e)}")
            return False
    
    def clear_spending_data(self, scenario: str) -> bool:
        """
        Clear all actual spending data for a scenario (reset to 0).
        
        Args:
            scenario: Budget scenario name.
            
        Returns:
            bool: True if successful.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE budget_data 
                    SET actual_spent = 0.0, date_updated = CURRENT_TIMESTAMP 
                    WHERE scenario = ?
                ''', (scenario,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error clearing spending data: {str(e)}")
            return False
    
    def backup_database(self, backup_path: str = None) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for backup file. Auto-generated if None.
            
        Returns:
            bool: True if successful.
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = Path("backups")
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"budget_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_path)
            print(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics and metadata.
        
        Returns:
            Dictionary with database statistics.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table sizes
                cursor.execute("SELECT COUNT(*) as count FROM budget_data")
                budget_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM spending_history")
                history_count = cursor.fetchone()['count']
                
                # Get database file size
                file_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                # Get last update time
                cursor.execute('''
                    SELECT MAX(date_updated) as last_update 
                    FROM budget_data
                ''')
                last_update = cursor.fetchone()['last_update']
                
                return {
                    'budget_records': budget_count,
                    'history_records': history_count,
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'last_update': last_update,
                    'database_path': str(self.db_path)
                }
                
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return {}
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a custom SQL query (for advanced operations).
        
        Args:
            query: SQL query string.
            params: Query parameters.
            
        Returns:
            List of result dictionaries.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    return [dict(row) for row in cursor.fetchall()]
                else:
                    conn.commit()
                    return [{'affected_rows': cursor.rowcount}]
                    
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            return []
    
    def close(self):
        """Close database connections."""
        # In this implementation, connections are auto-closed with context managers
        # This method is here for interface compatibility
        pass


# Example usage and testing
if __name__ == "__main__":
    # Demo database operations
    print("Database Manager Demo")
    print("-" * 50)
    
    # Initialize database
    db = DatabaseManager("test_budget.db")
    
    # Save some test data
    test_spending = {
        "Groceries": 250.0,
        "Utilities": 60.0,
        "Entertainment": 100.0
    }
    
    success = db.save_budget_data("Test Scenario", 3000.0, test_spending)
    print(f"Save test data: {'Success' if success else 'Failed'}")
    
    # Load the data back
    result = db.load_budget_data("Test Scenario")
    if result:
        paycheck, spending = result
        print(f"Loaded paycheck: ${paycheck}")
        print(f"Loaded spending: {spending}")
    
    # Get database stats
    stats = db.get_database_stats()
    print(f"Database stats: {stats}")
    
    # Clean up test database
    Path("test_budget.db").unlink(missing_ok=True)
    print("Test completed and cleaned up!")