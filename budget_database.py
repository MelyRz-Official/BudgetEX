# budget_database.py
import sqlite3
import os
from datetime import datetime
from typing import Dict, Optional, List, Tuple

class BudgetDatabase:
    def __init__(self, db_filename: str = "budget.db"):
        self.db_filename = db_filename
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_filename)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
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
            
            # Create budget_snapshots table for historical period data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budget_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period_id TEXT NOT NULL UNIQUE,
                    period_type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    scenario_name TEXT NOT NULL,
                    income REAL NOT NULL,
                    view_mode TEXT NOT NULL,
                    total_budgeted REAL NOT NULL,
                    total_spent REAL NOT NULL,
                    notes TEXT,
                    saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create snapshot_categories table for category details within snapshots
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshot_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    category_name TEXT NOT NULL,
                    budgeted_amount REAL NOT NULL,
                    actual_amount REAL NOT NULL,
                    category_notes TEXT,
                    FOREIGN KEY (snapshot_id) REFERENCES budget_snapshots (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            raise Exception(f"Failed to initialize database: {str(e)}")
    
    def save_budget_data(self, scenario: str, paycheck_amount: float, 
                        category_spending: Dict[str, float]) -> bool:
        """Save budget data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for category, actual_spent in category_spending.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO budget_data 
                    (scenario, paycheck_amount, category, actual_spent, date_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (scenario, paycheck_amount, category, actual_spent))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Failed to save data: {str(e)}")
            return False
    
    def save_budget_snapshot(self, snapshot) -> bool:
        """Save a budget snapshot to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save main snapshot data
            cursor.execute('''
                INSERT OR REPLACE INTO budget_snapshots 
                (period_id, period_type, start_date, end_date, display_name, 
                 scenario_name, income, view_mode, total_budgeted, total_spent, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot.period.period_id,
                snapshot.period.period_type.value,
                snapshot.period.start_date.isoformat(),
                snapshot.period.end_date.isoformat(),
                snapshot.period.display_name,
                snapshot.scenario_name,
                snapshot.income,
                snapshot.view_mode,
                snapshot.total_budgeted,
                snapshot.total_spent,
                snapshot.notes
            ))
            
            # Get the snapshot ID
            snapshot_id = cursor.lastrowid
            
            # Delete existing category data for this snapshot
            cursor.execute('DELETE FROM snapshot_categories WHERE snapshot_id = ?', (snapshot_id,))
            
            # Save category data
            for category_name, category_data in snapshot.category_data.items():
                cursor.execute('''
                    INSERT INTO snapshot_categories 
                    (snapshot_id, category_name, budgeted_amount, actual_amount, category_notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    snapshot_id,
                    category_name,
                    category_data['budgeted'],
                    category_data['actual'],
                    category_data.get('notes', '')
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Failed to save snapshot: {str(e)}")
            return False
    
    def load_budget_snapshots(self) -> Dict:
        """Load all budget snapshots from database"""
        try:
            from budget_time_tracker import BudgetPeriod, BudgetSnapshot, PeriodType
            from datetime import datetime
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all snapshots
            cursor.execute('''
                SELECT id, period_id, period_type, start_date, end_date, display_name,
                       scenario_name, income, view_mode, total_budgeted, total_spent, 
                       notes, saved_date
                FROM budget_snapshots
                ORDER BY start_date DESC
            ''')
            
            snapshots = {}
            snapshot_rows = cursor.fetchall()
            
            for row in snapshot_rows:
                (snapshot_id, period_id, period_type_str, start_date_str, end_date_str, 
                 display_name, scenario_name, income, view_mode, total_budgeted, 
                 total_spent, notes, saved_date_str) = row
                
                # Create period object
                period_type = PeriodType(period_type_str)
                start_date = datetime.fromisoformat(start_date_str).date()
                end_date = datetime.fromisoformat(end_date_str).date()
                
                period = BudgetPeriod(
                    period_id=period_id,
                    period_type=period_type,
                    start_date=start_date,
                    end_date=end_date,
                    display_name=display_name
                )
                
                # Get category data for this snapshot
                cursor.execute('''
                    SELECT category_name, budgeted_amount, actual_amount, category_notes
                    FROM snapshot_categories
                    WHERE snapshot_id = ?
                ''', (snapshot_id,))
                
                category_data = {}
                for cat_row in cursor.fetchall():
                    cat_name, budgeted, actual, cat_notes = cat_row
                    category_data[cat_name] = {
                        'budgeted': budgeted,
                        'actual': actual,
                        'notes': cat_notes or ''
                    }
                
                # Parse saved date
                saved_date = datetime.fromisoformat(saved_date_str.replace(' ', 'T'))
                
                # Create snapshot object
                snapshot = BudgetSnapshot(
                    period=period,
                    scenario_name=scenario_name,
                    income=income,
                    view_mode=view_mode,
                    category_data=category_data,
                    total_budgeted=total_budgeted,
                    total_spent=total_spent,
                    saved_date=saved_date,
                    notes=notes or ''
                )
                
                snapshots[period_id] = snapshot
            
            conn.close()
            return snapshots
            
        except Exception as e:
            print(f"Failed to load snapshots: {str(e)}")
            return {}
    
    def delete_budget_snapshot(self, period_id: str) -> bool:
        """Delete a budget snapshot from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete snapshot and related category data (CASCADE should handle categories)
            cursor.execute('DELETE FROM budget_snapshots WHERE period_id = ?', (period_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Failed to delete snapshot: {str(e)}")
            return False
    
    def load_budget_data(self, scenario: str) -> Optional[Tuple[float, Dict[str, float]]]:
        """Load budget data from database. Returns (paycheck_amount, category_spending)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, actual_spent, paycheck_amount 
                FROM budget_data 
                WHERE scenario = ?
            ''', (scenario,))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return None
            
            # Get paycheck amount from first record
            paycheck_amount = float(results[0][2])
            
            # Build category spending dictionary
            category_spending = {}
            for category, actual_spent, _ in results:
                category_spending[category] = float(actual_spent)
            
            return paycheck_amount, category_spending
            
        except Exception as e:
            print(f"Failed to load data: {str(e)}")
            return None
    
    def add_spending_history(self, scenario: str, category: str, 
                           amount: float, description: str = "") -> bool:
        """Add entry to spending history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO spending_history 
                (scenario, category, amount, description, date_added)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (scenario, category, amount, description))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Failed to add spending history: {str(e)}")
            return False
    
    def get_spending_history(self, scenario: str, category: str = None) -> List[Tuple]:
        """Get spending history for scenario and optionally specific category"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT category, amount, description, date_added 
                    FROM spending_history 
                    WHERE scenario = ? AND category = ?
                    ORDER BY date_added DESC
                ''', (scenario, category))
            else:
                cursor.execute('''
                    SELECT category, amount, description, date_added 
                    FROM spending_history 
                    WHERE scenario = ?
                    ORDER BY date_added DESC
                ''', (scenario,))
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            print(f"Failed to get spending history: {str(e)}")
            return []
    
    def create_backup(self, backup_directory: str = "backups") -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            from pathlib import Path
            
            # Create backup directory
            backup_dir = Path(backup_directory)
            backup_dir.mkdir(exist_ok=True)
            
            # Create timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"budget_backup_{timestamp}.db"
            backup_path = backup_dir / backup_filename
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            print(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Backup failed: {str(e)}")
            return False