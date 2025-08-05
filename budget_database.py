# # Add this to the top of budget_database.py
# import sqlite3
# import os
# import sys
# from datetime import datetime
# from typing import Dict, Optional, List, Tuple
# from pathlib import Path

# class BudgetDatabase:
#     def __init__(self, db_filename: str = "budget.db"):
#         self.db_filename = db_filename
        
#         # Fix for PyInstaller - get the correct data directory
#         self.data_dir = self.get_data_directory()
#         self.db_path = os.path.join(self.data_dir, db_filename)
        
#         # Create data directory if it doesn't exist
#         os.makedirs(self.data_dir, exist_ok=True)
        
#         print(f"Database will be saved to: {self.db_path}")  # Debug info
#         self.init_database()
    
#     def get_data_directory(self):
#         """Get the correct directory for saving data files"""
#         if getattr(sys, 'frozen', False):
#             # Running as PyInstaller executable
#             # Save data in the user's Documents folder
#             import os
#             documents_path = os.path.expanduser("~/Documents")
#             return os.path.join(documents_path, "Personal Budget Manager")
#         else:
#             # Running as Python script - save in current directory
#             return os.path.dirname(os.path.abspath(__file__))
    
#     def create_csv_backup(self, backup_filename: str = None) -> bool:
#         """Create a CSV backup of all budget data"""
#         try:
#             if backup_filename is None:
#                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                 backup_filename = f"budget_backup_{timestamp}.csv"
            
#             backup_path = os.path.join(self.data_dir, backup_filename)
            
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             # Get all budget data
#             cursor.execute('''
#                 SELECT scenario, paycheck_amount, category, actual_spent, date_updated 
#                 FROM budget_data 
#                 ORDER BY scenario, category
#             ''')
            
#             results = cursor.fetchall()
#             conn.close()
            
#             # Write to CSV
#             import csv
#             with open(backup_path, 'w', newline='', encoding='utf-8') as csvfile:
#                 writer = csv.writer(csvfile)
#                 writer.writerow(['Scenario', 'Paycheck Amount', 'Category', 'Actual Spent', 'Date Updated'])
#                 writer.writerows(results)
            
#             print(f"CSV backup created: {backup_path}")
#             return True
            
#         except Exception as e:
#             print(f"Failed to create CSV backup: {str(e)}")
#             return False
    
#     def load_from_csv_backup(self, csv_filename: str) -> bool:
#         """Load data from a CSV backup file"""
#         try:
#             csv_path = os.path.join(self.data_dir, csv_filename)
            
#             if not os.path.exists(csv_path):
#                 print(f"CSV file not found: {csv_path}")
#                 return False
            
#             import csv
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             # Clear existing data
#             cursor.execute('DELETE FROM budget_data')
            
#             # Load from CSV
#             with open(csv_path, 'r', encoding='utf-8') as csvfile:
#                 reader = csv.DictReader(csvfile)
#                 for row in reader:
#                     cursor.execute('''
#                         INSERT INTO budget_data 
#                         (scenario, paycheck_amount, category, actual_spent, date_updated)
#                         VALUES (?, ?, ?, ?, ?)
#                     ''', (
#                         row['Scenario'],
#                         float(row['Paycheck Amount']),
#                         row['Category'],
#                         float(row['Actual Spent']),
#                         row['Date Updated']
#                     ))
            
#             conn.commit()
#             conn.close()
            
#             print(f"Data loaded from CSV: {csv_path}")
#             return True
            
#         except Exception as e:
#             print(f"Failed to load from CSV: {str(e)}")
#             return False
    
#     def get_available_csv_backups(self) -> List[str]:
#         """Get list of available CSV backup files"""
#         try:
#             csv_files = []
#             for file in os.listdir(self.data_dir):
#                 if file.endswith('.csv') and 'budget' in file.lower():
#                     csv_files.append(file)
#             return sorted(csv_files, reverse=True)  # Most recent first
#         except Exception:
#             return []
    
#     def save_budget_data(self, scenario: str, paycheck_amount: float, 
#                         category_spending: Dict[str, float]) -> bool:
#         """Save budget data to database"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             for category, actual_spent in category_spending.items():
#                 cursor.execute('''
#                     INSERT OR REPLACE INTO budget_data 
#                     (scenario, paycheck_amount, category, actual_spent, date_updated)
#                     VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
#                 ''', (scenario, paycheck_amount, category, actual_spent))
            
#             conn.commit()
#             conn.close()
            
#             # Also create CSV backup on each save
#             self.create_csv_backup()
            
#             return True
            
#         except Exception as e:
#             print(f"Failed to save data: {str(e)}")
#             return False
    
#     # ... rest of your existing methods stay the same ...
    
#     def init_database(self):
#         """Initialize SQLite database with required tables"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             # Create budget_data table
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS budget_data (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     scenario TEXT NOT NULL,
#                     paycheck_amount REAL NOT NULL,
#                     category TEXT NOT NULL,
#                     actual_spent REAL NOT NULL DEFAULT 0.0,
#                     date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                     UNIQUE(scenario, category)
#                 )
#             ''')
            
#             # Create spending_history table
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS spending_history (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     scenario TEXT NOT NULL,
#                     category TEXT NOT NULL,
#                     amount REAL NOT NULL,
#                     description TEXT,
#                     date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                 )
#             ''')
            
#             # Create budget_snapshots table for historical period data
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS budget_snapshots (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     period_id TEXT NOT NULL UNIQUE,
#                     period_type TEXT NOT NULL,
#                     start_date TEXT NOT NULL,
#                     end_date TEXT NOT NULL,
#                     display_name TEXT NOT NULL,
#                     scenario_name TEXT NOT NULL,
#                     income REAL NOT NULL,
#                     view_mode TEXT NOT NULL,
#                     total_budgeted REAL NOT NULL,
#                     total_spent REAL NOT NULL,
#                     notes TEXT,
#                     saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                 )
#             ''')
            
#             # Create snapshot_categories table for category details within snapshots
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS snapshot_categories (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     snapshot_id INTEGER NOT NULL,
#                     category_name TEXT NOT NULL,
#                     budgeted_amount REAL NOT NULL,
#                     actual_amount REAL NOT NULL,
#                     category_notes TEXT,
#                     FOREIGN KEY (snapshot_id) REFERENCES budget_snapshots (id) ON DELETE CASCADE
#                 )
#             ''')
            
#             conn.commit()
#             conn.close()
            
#         except Exception as e:
#             raise Exception(f"Failed to initialize database: {str(e)}")
    
#     def load_budget_data(self, scenario: str) -> Optional[Tuple[float, Dict[str, float]]]:
#         """Load budget data from database. Returns (paycheck_amount, category_spending)"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             cursor.execute('''
#                 SELECT category, actual_spent, paycheck_amount 
#                 FROM budget_data 
#                 WHERE scenario = ?
#             ''', (scenario,))
            
#             results = cursor.fetchall()
#             conn.close()
            
#             if not results:
#                 return None
            
#             # Get paycheck amount from first record
#             paycheck_amount = float(results[0][2])
            
#             # Build category spending dictionary
#             category_spending = {}
#             for category, actual_spent, _ in results:
#                 category_spending[category] = float(actual_spent)
            
#             return paycheck_amount, category_spending
            
#         except Exception as e:
#             print(f"Failed to load data: {str(e)}")
#             return None
    
#     def add_spending_history(self, scenario: str, category: str, 
#                            amount: float, description: str = "") -> bool:
#         """Add entry to spending history"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             cursor.execute('''
#                 INSERT INTO spending_history 
#                 (scenario, category, amount, description, date_added)
#                 VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
#             ''', (scenario, category, amount, description))
            
#             conn.commit()
#             conn.close()
#             return True
            
#         except Exception as e:
#             print(f"Failed to add spending history: {str(e)}")
#             return False
    
#     def get_spending_history(self, scenario: str, category: str = None) -> List[Tuple]:
#         """Get spending history for scenario and optionally specific category"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             if category:
#                 cursor.execute('''
#                     SELECT category, amount, description, date_added 
#                     FROM spending_history 
#                     WHERE scenario = ? AND category = ?
#                     ORDER BY date_added DESC
#                 ''', (scenario, category))
#             else:
#                 cursor.execute('''
#                     SELECT category, amount, description, date_added 
#                     FROM spending_history 
#                     WHERE scenario = ?
#                     ORDER BY date_added DESC
#                 ''', (scenario,))
            
#             results = cursor.fetchall()
#             conn.close()
#             return results
            
#         except Exception as e:
#             print(f"Failed to get spending history: {str(e)}")
#             return []
    
#     def create_backup(self, backup_directory: str = "backups") -> bool:
#         """Create a backup of the database"""
#         try:
#             import shutil
#             from pathlib import Path
            
#             # Create backup directory
#             backup_dir = Path(self.data_dir) / backup_directory
#             backup_dir.mkdir(exist_ok=True)
            
#             # Create timestamped backup filename
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             backup_filename = f"budget_backup_{timestamp}.db"
#             backup_path = backup_dir / backup_filename
            
#             # Copy database file
#             shutil.copy2(self.db_path, backup_path)
#             print(f"Backup created: {backup_path}")
#             return True
            
#         except Exception as e:
#             print(f"Backup failed: {str(e)}")
#             return False
    
#     def save_budget_snapshot(self, snapshot) -> bool:
#         """Save a budget snapshot to database"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             # Save main snapshot data
#             cursor.execute('''
#                 INSERT OR REPLACE INTO budget_snapshots 
#                 (period_id, period_type, start_date, end_date, display_name, 
#                  scenario_name, income, view_mode, total_budgeted, total_spent, notes)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             ''', (
#                 snapshot.period.period_id,
#                 snapshot.period.period_type.value,
#                 snapshot.period.start_date.isoformat(),
#                 snapshot.period.end_date.isoformat(),
#                 snapshot.period.display_name,
#                 snapshot.scenario_name,
#                 snapshot.income,
#                 snapshot.view_mode,
#                 snapshot.total_budgeted,
#                 snapshot.total_spent,
#                 snapshot.notes
#             ))
            
#             # Get the snapshot ID
#             snapshot_id = cursor.lastrowid
            
#             # Delete existing category data for this snapshot
#             cursor.execute('DELETE FROM snapshot_categories WHERE snapshot_id = ?', (snapshot_id,))
            
#             # Save category data
#             for category_name, category_data in snapshot.category_data.items():
#                 cursor.execute('''
#                     INSERT INTO snapshot_categories 
#                     (snapshot_id, category_name, budgeted_amount, actual_amount, category_notes)
#                     VALUES (?, ?, ?, ?, ?)
#                 ''', (
#                     snapshot_id,
#                     category_name,
#                     category_data['budgeted'],
#                     category_data['actual'],
#                     category_data.get('notes', '')
#                 ))
            
#             conn.commit()
#             conn.close()
#             return True
            
#         except Exception as e:
#             print(f"Failed to save snapshot: {str(e)}")
#             return False
    
#     def load_budget_snapshots(self) -> Dict:
#         """Load all budget snapshots from database"""
#         try:
#             from budget_time_tracker import BudgetPeriod, BudgetSnapshot, PeriodType
#             from datetime import datetime
            
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             # Get all snapshots
#             cursor.execute('''
#                 SELECT id, period_id, period_type, start_date, end_date, display_name,
#                        scenario_name, income, view_mode, total_budgeted, total_spent, 
#                        notes, saved_date
#                 FROM budget_snapshots
#                 ORDER BY start_date DESC
#             ''')
            
#             snapshots = {}
#             snapshot_rows = cursor.fetchall()
            
#             for row in snapshot_rows:
#                 (snapshot_id, period_id, period_type_str, start_date_str, end_date_str, 
#                  display_name, scenario_name, income, view_mode, total_budgeted, 
#                  total_spent, notes, saved_date_str) = row
                
#                 # Create period object
#                 period_type = PeriodType(period_type_str)
#                 start_date = datetime.fromisoformat(start_date_str).date()
#                 end_date = datetime.fromisoformat(end_date_str).date()
                
#                 period = BudgetPeriod(
#                     period_id=period_id,
#                     period_type=period_type,
#                     start_date=start_date,
#                     end_date=end_date,
#                     display_name=display_name
#                 )
                
#                 # Get category data for this snapshot
#                 cursor.execute('''
#                     SELECT category_name, budgeted_amount, actual_amount, category_notes
#                     FROM snapshot_categories
#                     WHERE snapshot_id = ?
#                 ''', (snapshot_id,))
                
#                 category_data = {}
#                 for cat_row in cursor.fetchall():
#                     cat_name, budgeted, actual, cat_notes = cat_row
#                     category_data[cat_name] = {
#                         'budgeted': budgeted,
#                         'actual': actual,
#                         'notes': cat_notes or ''
#                     }
                
#                 # Parse saved date
#                 saved_date = datetime.fromisoformat(saved_date_str.replace(' ', 'T'))
                
#                 # Create snapshot object
#                 snapshot = BudgetSnapshot(
#                     period=period,
#                     scenario_name=scenario_name,
#                     income=income,
#                     view_mode=view_mode,
#                     category_data=category_data,
#                     total_budgeted=total_budgeted,
#                     total_spent=total_spent,
#                     saved_date=saved_date,
#                     notes=notes or ''
#                 )
                
#                 snapshots[period_id] = snapshot
            
#             conn.close()
#             return snapshots
            
#         except Exception as e:
#             print(f"Failed to load snapshots: {str(e)}")
#             return {}
    
#     def delete_budget_snapshot(self, period_id: str) -> bool:
#         """Delete a budget snapshot from database"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             # Delete snapshot and related category data (CASCADE should handle categories)
#             cursor.execute('DELETE FROM budget_snapshots WHERE period_id = ?', (period_id,))
            
#             conn.commit()
#             conn.close()
#             return True
            
#         except Exception as e:
#             print(f"Failed to delete snapshot: {str(e)}")
#             return False

# budget_database.py - COMPLETE FIXED VERSION
import sqlite3
import os
import sys
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from pathlib import Path

class BudgetDatabase:
    def __init__(self, db_filename: str = "budget.db"):
        self.db_filename = db_filename
        
        # Fix for PyInstaller - get the correct data directory
        self.data_dir = self.get_data_directory()
        self.db_path = os.path.join(self.data_dir, db_filename)
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        print(f"Database will be saved to: {self.db_path}")  # Debug info
        self.init_database()
        self.upgrade_database_schema()  # Handle existing databases
    
    def get_data_directory(self):
        """Get the correct directory for saving data files"""
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            # Save data in the user's Documents folder
            documents_path = os.path.expanduser("~/Documents")
            return os.path.join(documents_path, "Personal Budget Manager")
        else:
            # Running as Python script - save in current directory
            return os.path.dirname(os.path.abspath(__file__))
    
    def upgrade_database_schema(self):
        """Upgrade existing database to support individual paychecks"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if new columns exist in budget_data
            cursor.execute("PRAGMA table_info(budget_data)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'first_paycheck' not in columns:
                print("Upgrading budget_data table to support individual paychecks...")
                
                # Add new columns
                cursor.execute('ALTER TABLE budget_data ADD COLUMN first_paycheck REAL')
                cursor.execute('ALTER TABLE budget_data ADD COLUMN second_paycheck REAL')
                
                # Migrate existing data (split existing paycheck_amount in half)
                cursor.execute('''
                    UPDATE budget_data 
                    SET first_paycheck = paycheck_amount / 2,
                        second_paycheck = paycheck_amount / 2
                    WHERE first_paycheck IS NULL
                ''')
                
                print("Budget data table upgraded successfully!")
            
            # Check if new columns exist in budget_snapshots
            cursor.execute("PRAGMA table_info(budget_snapshots)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'first_paycheck' not in columns:
                print("Upgrading budget_snapshots table to support individual paychecks...")
                
                # Add new columns
                cursor.execute('ALTER TABLE budget_snapshots ADD COLUMN first_paycheck REAL')
                cursor.execute('ALTER TABLE budget_snapshots ADD COLUMN second_paycheck REAL')
                
                # Migrate existing data (split existing income in half)
                cursor.execute('''
                    UPDATE budget_snapshots 
                    SET first_paycheck = income / 2,
                        second_paycheck = income / 2
                    WHERE first_paycheck IS NULL
                ''')
                
                print("Budget snapshots table upgraded successfully!")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Warning: Could not upgrade database schema: {str(e)}")
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create budget_data table with individual paycheck support
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budget_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT NOT NULL,
                    paycheck_amount REAL NOT NULL,
                    first_paycheck REAL,
                    second_paycheck REAL,
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
            
            # Create budget_snapshots table with individual paycheck support
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
                    first_paycheck REAL,
                    second_paycheck REAL,
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
    
    def save_budget_data(self, scenario: str, total_income: float, 
                        category_spending: Dict[str, float]) -> bool:
        """Save budget data to database with individual paycheck amounts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract paycheck amounts from category_spending
            first_paycheck = category_spending.get('first_paycheck', total_income / 2)
            second_paycheck = category_spending.get('second_paycheck', total_income / 2)
            
            for category, actual_spent in category_spending.items():
                # Skip the paycheck metadata when saving categories
                if category in ['first_paycheck', 'second_paycheck']:
                    continue
                    
                cursor.execute('''
                    INSERT OR REPLACE INTO budget_data 
                    (scenario, paycheck_amount, first_paycheck, second_paycheck, 
                     category, actual_spent, date_updated)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (scenario, total_income, first_paycheck, second_paycheck, category, actual_spent))
            
            conn.commit()
            conn.close()
            
            # Also create CSV backup on each save
            self.create_csv_backup()
            
            return True
            
        except Exception as e:
            print(f"Failed to save data: {str(e)}")
            return False
    
    def load_budget_data(self, scenario: str) -> Optional[Tuple[float, Dict[str, float]]]:
        """Load budget data from database with individual paycheck amounts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, actual_spent, paycheck_amount, first_paycheck, second_paycheck
                FROM budget_data 
                WHERE scenario = ?
            ''', (scenario,))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return None
            
            # Get paycheck amounts from first record
            _, _, total_income, first_paycheck, second_paycheck = results[0]
            
            # Build category spending dictionary
            category_spending = {}
            for category, actual_spent, _, _, _ in results:
                category_spending[category] = float(actual_spent)
            
            # Add paycheck amounts to the dictionary
            if first_paycheck is not None and second_paycheck is not None:
                category_spending['first_paycheck'] = float(first_paycheck)
                category_spending['second_paycheck'] = float(second_paycheck)
            else:
                # Fallback for old data
                category_spending['first_paycheck'] = float(total_income) / 2
                category_spending['second_paycheck'] = float(total_income) / 2
            
            return float(total_income), category_spending
            
        except Exception as e:
            print(f"Failed to load data: {str(e)}")
            return None
    
    def save_budget_snapshot(self, snapshot) -> bool:
        """Save a budget snapshot to database with individual paycheck amounts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save main snapshot data
            cursor.execute('''
                INSERT OR REPLACE INTO budget_snapshots 
                (period_id, period_type, start_date, end_date, display_name, 
                 scenario_name, income, first_paycheck, second_paycheck, view_mode, 
                 total_budgeted, total_spent, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot.period.period_id,
                snapshot.period.period_type.value,
                snapshot.period.start_date.isoformat(),
                snapshot.period.end_date.isoformat(),
                snapshot.period.display_name,
                snapshot.scenario_name,
                snapshot.total_income,
                snapshot.first_paycheck,
                snapshot.second_paycheck,
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
        """Load all budget snapshots from database with individual paycheck amounts"""
        try:
            from budget_time_tracker import BudgetPeriod, BudgetSnapshot, PeriodType
            from datetime import datetime
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all snapshots
            cursor.execute('''
                SELECT id, period_id, period_type, start_date, end_date, display_name,
                       scenario_name, income, first_paycheck, second_paycheck, view_mode, 
                       total_budgeted, total_spent, notes, saved_date
                FROM budget_snapshots
                ORDER BY start_date DESC
            ''')
            
            snapshots = {}
            snapshot_rows = cursor.fetchall()
            
            for row in snapshot_rows:
                (snapshot_id, period_id, period_type_str, start_date_str, end_date_str, 
                 display_name, scenario_name, income, first_paycheck, second_paycheck, 
                 view_mode, total_budgeted, total_spent, notes, saved_date_str) = row
                
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
                
                # Handle missing paycheck data (from old snapshots)
                if first_paycheck is None or second_paycheck is None:
                    first_paycheck = income / 2
                    second_paycheck = income / 2
                
                # Create snapshot object
                snapshot = BudgetSnapshot(
                    period=period,
                    scenario_name=scenario_name,
                    first_paycheck=first_paycheck,
                    second_paycheck=second_paycheck,
                    total_income=income,
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
    
    def create_csv_backup(self, backup_filename: str = None) -> bool:
        """Create a CSV backup of all budget data with individual paycheck amounts"""
        try:
            if backup_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"budget_backup_{timestamp}.csv"
            
            backup_path = os.path.join(self.data_dir, backup_filename)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all budget data with individual paycheck amounts
            cursor.execute('''
                SELECT scenario, paycheck_amount, first_paycheck, second_paycheck, 
                       category, actual_spent, date_updated 
                FROM budget_data 
                ORDER BY scenario, category
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            # Write to CSV
            import csv
            with open(backup_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Scenario', 'Total Income', 'First Paycheck', 'Second Paycheck', 
                               'Category', 'Actual Spent', 'Date Updated'])
                writer.writerows(results)
            
            print(f"CSV backup created: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Failed to create CSV backup: {str(e)}")
            return False
    
    def load_from_csv_backup(self, csv_filename: str) -> bool:
        """Load data from a CSV backup file with individual paycheck support"""
        try:
            csv_path = os.path.join(self.data_dir, csv_filename)
            
            if not os.path.exists(csv_path):
                print(f"CSV file not found: {csv_path}")
                return False
            
            import csv
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM budget_data')
            
            # Load from CSV
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Handle both old and new CSV formats
                    first_paycheck = row.get('First Paycheck', float(row.get('Total Income', 0)) / 2)
                    second_paycheck = row.get('Second Paycheck', float(row.get('Total Income', 0)) / 2)
                    
                    cursor.execute('''
                        INSERT INTO budget_data 
                        (scenario, paycheck_amount, first_paycheck, second_paycheck, 
                         category, actual_spent, date_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Scenario'],
                        float(row.get('Total Income', row.get('Paycheck Amount', 0))),
                        float(first_paycheck),
                        float(second_paycheck),
                        row['Category'],
                        float(row['Actual Spent']),
                        row['Date Updated']
                    ))
            
            conn.commit()
            conn.close()
            
            print(f"Data loaded from CSV: {csv_path}")
            return True
            
        except Exception as e:
            print(f"Failed to load from CSV: {str(e)}")
            return False
    
    def get_available_csv_backups(self) -> List[str]:
        """Get list of available CSV backup files"""
        try:
            csv_files = []
            for file in os.listdir(self.data_dir):
                if file.endswith('.csv') and 'budget' in file.lower():
                    csv_files.append(file)
            return sorted(csv_files, reverse=True)  # Most recent first
        except Exception:
            return []
    
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
            
            # Create backup directory
            backup_dir = Path(self.data_dir) / backup_directory
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