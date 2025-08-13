"""
Budget Database Module
Handles all database operations
"""
import sqlite3
from datetime import datetime

class BudgetDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with month support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create paychecks table with month/year
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paychecks (
                id INTEGER PRIMARY KEY,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                first_paycheck REAL NOT NULL,
                second_paycheck REAL NOT NULL,
                total_income REAL NOT NULL,
                date_saved TEXT NOT NULL,
                UNIQUE(month, year)
            )
        ''')
        
        # Create spending table with month/year
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spending (
                id INTEGER PRIMARY KEY,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date_saved TEXT NOT NULL,
                UNIQUE(month, year, category)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_month_data(self, month, year, first_paycheck, second_paycheck, categories_data):
        """Save data for a specific month"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            total = first_paycheck + second_paycheck
            current_time = datetime.now().isoformat()
            
            # Save paychecks (replace if exists)
            cursor.execute('''
                INSERT OR REPLACE INTO paychecks 
                (month, year, first_paycheck, second_paycheck, total_income, date_saved)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (month, year, first_paycheck, second_paycheck, total, current_time))
            
            # Save spending (replace if exists)
            for category_name, amount in categories_data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO spending 
                    (month, year, category, amount, date_saved)
                    VALUES (?, ?, ?, ?, ?)
                ''', (month, year, category_name, amount, current_time))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_month_data(self, month, year):
        """Load data for a specific month"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load paychecks for this month
            cursor.execute('''
                SELECT first_paycheck, second_paycheck 
                FROM paychecks 
                WHERE month = ? AND year = ?
            ''', (month, year))
            
            paycheck_data = cursor.fetchone()
            
            # Load spending for this month
            cursor.execute('''
                SELECT category, amount 
                FROM spending 
                WHERE month = ? AND year = ?
            ''', (month, year))
            
            spending_data = dict(cursor.fetchall())
            
            conn.close()
            
            if paycheck_data:
                return paycheck_data[0], paycheck_data[1], spending_data
            else:
                return None, None, spending_data
                
        except Exception as e:
            print(f"Error loading month data: {e}")
            return None, None, {}
    
    def delete_month_data(self, month, year):
        """Delete data for a specific month"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM paychecks WHERE month = ? AND year = ?', (month, year))
            cursor.execute('DELETE FROM spending WHERE month = ? AND year = ?', (month, year))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
    
    def get_all_chart_data(self):
        """Get all data for charts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all months with data
            cursor.execute('''
                SELECT DISTINCT p.month, p.year, p.first_paycheck, p.second_paycheck, p.total_income
                FROM paychecks p
                ORDER BY p.year, p.month
            ''')
            months_data = cursor.fetchall()
            
            # Get spending data for all months
            spending_data = {}
            for month, year, first, second, total in months_data:
                cursor.execute('''
                    SELECT category, amount FROM spending 
                    WHERE month = ? AND year = ?
                ''', (month, year))
                
                import calendar
                month_key = f"{calendar.month_name[month][:3]} {year}"
                spending_data[month_key] = {
                    'month': month,
                    'year': year,
                    'income': total,
                    'first_paycheck': first,
                    'second_paycheck': second,
                    'categories': dict(cursor.fetchall())
                }
            
            conn.close()
            return spending_data
            
        except Exception as e:
            print(f"Error getting chart data: {e}")
            return {}
    
    def get_database_contents(self):
        """Get formatted database contents for display"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get paycheck data
            cursor.execute("SELECT * FROM paychecks ORDER BY year DESC, month DESC")
            paychecks = cursor.fetchall()
            
            # Get spending data
            cursor.execute("SELECT * FROM spending ORDER BY year DESC, month DESC, category")
            spending = cursor.fetchall()
            
            conn.close()
            return paychecks, spending
            
        except Exception as e:
            print(f"Error getting database contents: {e}")
            return [], []