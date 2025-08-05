# # budget_time_tracker.py
# from dataclasses import dataclass
# from datetime import datetime, date, timedelta
# from typing import Dict, List, Optional, Tuple
# from enum import Enum
# import calendar

# class PeriodType(Enum):
#     MONTHLY = "Monthly"
#     BIWEEKLY = "Biweekly" 
#     WEEKLY = "Weekly"
#     CUSTOM = "Custom Range"

# @dataclass
# class BudgetPeriod:
#     """Represents a specific time period for budget tracking"""
#     period_id: str
#     period_type: PeriodType
#     start_date: date
#     end_date: date
#     display_name: str
    
#     def __str__(self):
#         return self.display_name
    
#     def contains_date(self, check_date: date) -> bool:
#         """Check if a date falls within this period"""
#         return self.start_date <= check_date <= self.end_date
    
#     def days_in_period(self) -> int:
#         """Get number of days in this period"""
#         return (self.end_date - self.start_date).days + 1

# @dataclass
# class BudgetSnapshot:
#     """A snapshot of budget data for a specific period"""
#     period: BudgetPeriod
#     scenario_name: str
#     income: float
#     view_mode: str
#     category_data: Dict[str, dict]  # category_name -> {budgeted, actual, notes}
#     total_budgeted: float
#     total_spent: float
#     saved_date: datetime
#     notes: str = ""
    
#     def get_category_actual(self, category: str) -> float:
#         """Get actual spending for a category"""
#         return self.category_data.get(category, {}).get('actual', 0.0)
    
#     def get_category_budgeted(self, category: str) -> float:
#         """Get budgeted amount for a category"""
#         return self.category_data.get(category, {}).get('budgeted', 0.0)

# class TimeTracker:
#     """Manages time-based budget tracking and historical data"""
    
#     def __init__(self, database=None):
#         self.database = database  # BudgetDatabase instance
#         self.snapshots: Dict[str, BudgetSnapshot] = {}  # period_id -> snapshot
        
#         # Load existing snapshots from database if available
#         if self.database:
#             self.load_snapshots_from_db()
    
#     def generate_monthly_periods(self, start_year: int = None, num_months: int = 12) -> List[BudgetPeriod]:
#         """Generate monthly periods starting from a given year"""
#         if start_year is None:
#             start_year = datetime.now().year
        
#         periods = []
#         current_date = date(start_year, 1, 1)
        
#         for i in range(num_months):
#             year = current_date.year
#             month = current_date.month
            
#             # First day of month
#             start_date = date(year, month, 1)
            
#             # Last day of month
#             last_day = calendar.monthrange(year, month)[1]
#             end_date = date(year, month, last_day)
            
#             period_id = f"monthly_{year}_{month:02d}"
#             display_name = f"{calendar.month_name[month]} {year}"
            
#             period = BudgetPeriod(
#                 period_id=period_id,
#                 period_type=PeriodType.MONTHLY,
#                 start_date=start_date,
#                 end_date=end_date,
#                 display_name=display_name
#             )
            
#             periods.append(period)
            
#             # Move to next month
#             if month == 12:
#                 current_date = date(year + 1, 1, 1)
#             else:
#                 current_date = date(year, month + 1, 1)
        
#         return periods
    
#     def generate_biweekly_periods(self, start_date: date = None, num_periods: int = 26) -> List[BudgetPeriod]:
#         """Generate biweekly periods (every 2 weeks)"""
#         if start_date is None:
#             # Start from beginning of current year
#             start_date = date(datetime.now().year, 1, 1)
        
#         periods = []
#         current_start = start_date
        
#         for i in range(num_periods):
#             current_end = current_start + timedelta(days=13)  # 14 days total (0-13)
            
#             period_id = f"biweekly_{current_start.strftime('%Y_%m_%d')}"
#             display_name = f"Biweekly {current_start.strftime('%b %d')} - {current_end.strftime('%b %d, %Y')}"
            
#             period = BudgetPeriod(
#                 period_id=period_id,
#                 period_type=PeriodType.BIWEEKLY,
#                 start_date=current_start,
#                 end_date=current_end,
#                 display_name=display_name
#             )
            
#             periods.append(period)
#             current_start = current_end + timedelta(days=1)
        
#         return periods
    
#     def generate_weekly_periods(self, start_date: date = None, num_weeks: int = 52) -> List[BudgetPeriod]:
#         """Generate weekly periods"""
#         if start_date is None:
#             # Start from beginning of current year
#             start_date = date(datetime.now().year, 1, 1)
#             # Adjust to start on Monday
#             days_since_monday = start_date.weekday()
#             start_date = start_date - timedelta(days=days_since_monday)
        
#         periods = []
#         current_start = start_date
        
#         for i in range(num_weeks):
#             current_end = current_start + timedelta(days=6)  # 7 days total
            
#             period_id = f"weekly_{current_start.strftime('%Y_%m_%d')}"
#             display_name = f"Week of {current_start.strftime('%b %d, %Y')}"
            
#             period = BudgetPeriod(
#                 period_id=period_id,
#                 period_type=PeriodType.WEEKLY,
#                 start_date=current_start,
#                 end_date=current_end,
#                 display_name=display_name
#             )
            
#             periods.append(period)
#             current_start = current_end + timedelta(days=1)
        
#         return periods
    
#     def create_custom_period(self, start_date: date, end_date: date, name: str = None) -> BudgetPeriod:
#         """Create a custom date range period"""
#         if name is None:
#             name = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        
#         period_id = f"custom_{start_date.strftime('%Y_%m_%d')}_{end_date.strftime('%Y_%m_%d')}"
        
#         return BudgetPeriod(
#             period_id=period_id,
#             period_type=PeriodType.CUSTOM,
#             start_date=start_date,
#             end_date=end_date,
#             display_name=name
#         )
    
#     def get_current_period(self, period_type: PeriodType) -> BudgetPeriod:
#         """Get the period that contains today's date"""
#         today = date.today()
        
#         if period_type == PeriodType.MONTHLY:
#             periods = self.generate_monthly_periods(today.year, 12)
#         elif period_type == PeriodType.BIWEEKLY:
#             # Generate periods starting from beginning of year
#             start_of_year = date(today.year, 1, 1)
#             periods = self.generate_biweekly_periods(start_of_year, 26)
#         elif period_type == PeriodType.WEEKLY:
#             start_of_year = date(today.year, 1, 1)
#             periods = self.generate_weekly_periods(start_of_year, 52)
#         else:
#             # For custom, return a period for current month
#             return self.generate_monthly_periods(today.year, 1)[0]
        
#         # Find period containing today
#         for period in periods:
#             if period.contains_date(today):
#                 return period
        
#         # Fallback: return current month
#         return self.generate_monthly_periods(today.year, 1)[0]
    
#     def save_snapshot(self, snapshot: BudgetSnapshot):
#         """Save a budget snapshot for a period"""
#         self.snapshots[snapshot.period.period_id] = snapshot
        
#         # Also save to database if available
#         if self.database:
#             self.database.save_budget_snapshot(snapshot)
    
#     def load_snapshots_from_db(self):
#         """Load all snapshots from database"""
#         if self.database:
#             self.snapshots = self.database.load_budget_snapshots()
    
#     def get_snapshot(self, period_id: str) -> Optional[BudgetSnapshot]:
#         """Get a saved snapshot by period ID"""
#         return self.snapshots.get(period_id)
    
#     def get_snapshots_by_date_range(self, start_date: date, end_date: date) -> List[BudgetSnapshot]:
#         """Get all snapshots within a date range"""
#         matching_snapshots = []
        
#         for snapshot in self.snapshots.values():
#             # Check if snapshot period overlaps with date range
#             if (snapshot.period.start_date <= end_date and 
#                 snapshot.period.end_date >= start_date):
#                 matching_snapshots.append(snapshot)
        
#         # Sort by start date
#         matching_snapshots.sort(key=lambda s: s.period.start_date)
#         return matching_snapshots
    
#     def get_available_periods(self) -> List[BudgetPeriod]:
#         """Get all periods that have saved snapshots"""
#         periods = [snapshot.period for snapshot in self.snapshots.values()]
#         periods.sort(key=lambda p: p.start_date, reverse=True)  # Most recent first
#         return periods
    
#     def delete_snapshot(self, period_id: str) -> bool:
#         """Delete a snapshot"""
#         # Remove from memory
#         if period_id in self.snapshots:
#             del self.snapshots[period_id]
        
#         # Remove from database if available
#         if self.database:
#             return self.database.delete_budget_snapshot(period_id)
        
#         return True

# class SpendingAnalyzer:
#     """Analyzes spending patterns and trends over time"""
    
#     def __init__(self, time_tracker: TimeTracker):
#         self.time_tracker = time_tracker
    
#     def calculate_category_trends(self, category: str, num_periods: int = 6) -> Dict[str, float]:
#         """Calculate trends for a specific category over recent periods"""
#         # Get recent snapshots
#         snapshots = list(self.time_tracker.snapshots.values())
#         snapshots.sort(key=lambda s: s.period.start_date, reverse=True)
#         recent_snapshots = snapshots[:num_periods]
        
#         if len(recent_snapshots) < 2:
#             return {"trend": 0.0, "average": 0.0, "variance": 0.0}
        
#         # Get spending amounts
#         amounts = [s.get_category_actual(category) for s in recent_snapshots]
#         amounts.reverse()  # Chronological order
        
#         # Calculate statistics
#         average = sum(amounts) / len(amounts)
        
#         # Simple trend calculation (difference between recent and older periods)
#         if len(amounts) >= 2:
#             recent_avg = sum(amounts[-2:]) / 2  # Last 2 periods
#             older_avg = sum(amounts[:2]) / 2    # First 2 periods
#             trend = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
#         else:
#             trend = 0
        
#         # Variance calculation
#         variance = sum((x - average) ** 2 for x in amounts) / len(amounts)
        
#         return {
#             "trend": trend,  # Percentage change
#             "average": average,
#             "variance": variance,
#             "min": min(amounts),
#             "max": max(amounts),
#             "periods_analyzed": len(amounts)
#         }
    
#     def get_spending_summary(self, num_periods: int = 6) -> Dict[str, any]:
#         """Get overall spending summary across recent periods"""
#         snapshots = list(self.time_tracker.snapshots.values())
#         snapshots.sort(key=lambda s: s.period.start_date, reverse=True)
#         recent_snapshots = snapshots[:num_periods]
        
#         if not recent_snapshots:
#             return {"error": "No data available"}
        
#         # Calculate totals
#         total_budgeted = sum(s.total_budgeted for s in recent_snapshots)
#         total_spent = sum(s.total_spent for s in recent_snapshots)
        
#         # Get all categories from all snapshots
#         all_categories = set()
#         for snapshot in recent_snapshots:
#             all_categories.update(snapshot.category_data.keys())
        
#         # Calculate category summaries
#         category_summaries = {}
#         for category in all_categories:
#             amounts = [s.get_category_actual(category) for s in recent_snapshots]
#             budgeted_amounts = [s.get_category_budgeted(category) for s in recent_snapshots]
            
#             category_summaries[category] = {
#                 "total_spent": sum(amounts),
#                 "total_budgeted": sum(budgeted_amounts),
#                 "average_spent": sum(amounts) / len(amounts),
#                 "average_budgeted": sum(budgeted_amounts) / len(budgeted_amounts)
#             }
        
#         return {
#             "periods_analyzed": len(recent_snapshots),
#             "total_budgeted": total_budgeted,
#             "total_spent": total_spent,
#             "average_budgeted_per_period": total_budgeted / len(recent_snapshots),
#             "average_spent_per_period": total_spent / len(recent_snapshots),
#             "overall_savings_rate": ((total_budgeted - total_spent) / total_budgeted * 100) if total_budgeted > 0 else 0,
#             "categories": category_summaries
#         }
    
#     def compare_periods(self, period1_id: str, period2_id: str) -> Dict[str, any]:
#         """Compare spending between two specific periods"""
#         snapshot1 = self.time_tracker.get_snapshot(period1_id)
#         snapshot2 = self.time_tracker.get_snapshot(period2_id)
        
#         if not snapshot1 or not snapshot2:
#             return {"error": "One or both periods not found"}
        
#         # Get all categories from both periods
#         all_categories = set(snapshot1.category_data.keys()) | set(snapshot2.category_data.keys())
        
#         category_comparisons = {}
#         for category in all_categories:
#             actual1 = snapshot1.get_category_actual(category)
#             actual2 = snapshot2.get_category_actual(category)
            
#             change = actual2 - actual1
#             percent_change = (change / actual1 * 100) if actual1 > 0 else 0
            
#             category_comparisons[category] = {
#                 f"{snapshot1.period.display_name}_actual": actual1,
#                 f"{snapshot2.period.display_name}_actual": actual2,
#                 "change": change,
#                 "percent_change": percent_change
#             }
        
#         total_change = snapshot2.total_spent - snapshot1.total_spent
#         total_percent_change = (total_change / snapshot1.total_spent * 100) if snapshot1.total_spent > 0 else 0
        
#         return {
#             "period1": snapshot1.period.display_name,
#             "period2": snapshot2.period.display_name,
#             "total_change": total_change,
#             "total_percent_change": total_percent_change,
#             "categories": category_comparisons
#         }

# budget_time_tracker.py - UPDATED VERSION COMPATIBLE WITH ENHANCED DATABASE
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import calendar
from budget_database import BudgetDatabase


class PeriodType(Enum):
    MONTHLY = "Monthly"
    BIWEEKLY = "Biweekly" 
    WEEKLY = "Weekly"
    CUSTOM = "Custom Range"

@dataclass
class BudgetPeriod:
    """Represents a specific time period for budget tracking"""
    period_id: str
    period_type: PeriodType
    start_date: date
    end_date: date
    display_name: str
    
    def __str__(self):
        return self.display_name
    
    def contains_date(self, check_date: date) -> bool:
        """Check if a date falls within this period"""
        return self.start_date <= check_date <= self.end_date
    
    def days_in_period(self) -> int:
        """Get number of days in this period"""
        return (self.end_date - self.start_date).days + 1

@dataclass
class BudgetSnapshot:
    """A snapshot of budget data for a specific period - UPDATED FOR INDIVIDUAL PAYCHECKS"""
    period: BudgetPeriod
    scenario_name: str
    first_paycheck: float  # Individual paycheck amounts
    second_paycheck: float
    total_income: float    # Total monthly income (calculated)
    view_mode: str
    category_data: Dict[str, dict]  # category_name -> {budgeted, actual, notes}
    total_budgeted: float
    total_spent: float
    saved_date: datetime
    notes: str = ""
    
    def __post_init__(self):
        """Ensure total_income matches individual paychecks"""
        if self.total_income != self.first_paycheck + self.second_paycheck:
            self.total_income = self.first_paycheck + self.second_paycheck
    
    def get_category_actual(self, category: str) -> float:
        """Get actual spending for a category"""
        return self.category_data.get(category, {}).get('actual', 0.0)
    
    def get_category_budgeted(self, category: str) -> float:
        """Get budgeted amount for a category"""
        return self.category_data.get(category, {}).get('budgeted', 0.0)
    
    @property
    def income(self) -> float:
        """Backward compatibility - returns total_income"""
        return self.total_income

class TimeTracker:
    """Manages time-based budget tracking and historical data"""
    
    def __init__(self, database=None):
        if database is None:
            self.database = BudgetDatabase()  # Create one if not provided
        else:
            self.database = database
        
        self.snapshots: Dict[str, BudgetSnapshot] = {}
        
        if self.database:
            self.load_snapshots_from_db()
    
    def generate_monthly_periods(self, start_year: int = None, num_months: int = 12) -> List[BudgetPeriod]:
        """Generate monthly periods starting from a given year"""
        if start_year is None:
            start_year = datetime.now().year
        
        periods = []
        current_date = date(start_year, 1, 1)
        
        for i in range(num_months):
            year = current_date.year
            month = current_date.month
            
            # First day of month
            start_date = date(year, month, 1)
            
            # Last day of month
            last_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, last_day)
            
            period_id = f"monthly_{year}_{month:02d}"
            display_name = f"{calendar.month_name[month]} {year}"
            
            period = BudgetPeriod(
                period_id=period_id,
                period_type=PeriodType.MONTHLY,
                start_date=start_date,
                end_date=end_date,
                display_name=display_name
            )
            
            periods.append(period)
            
            # Move to next month
            if month == 12:
                current_date = date(year + 1, 1, 1)
            else:
                current_date = date(year, month + 1, 1)
        
        return periods
    
    def generate_biweekly_periods(self, start_date: date = None, num_periods: int = 26) -> List[BudgetPeriod]:
        """Generate biweekly periods (every 2 weeks)"""
        if start_date is None:
            # Start from beginning of current year
            start_date = date(datetime.now().year, 1, 1)
        
        periods = []
        current_start = start_date
        
        for i in range(num_periods):
            current_end = current_start + timedelta(days=13)  # 14 days total (0-13)
            
            period_id = f"biweekly_{current_start.strftime('%Y_%m_%d')}"
            display_name = f"Biweekly {current_start.strftime('%b %d')} - {current_end.strftime('%b %d, %Y')}"
            
            period = BudgetPeriod(
                period_id=period_id,
                period_type=PeriodType.BIWEEKLY,
                start_date=current_start,
                end_date=current_end,
                display_name=display_name
            )
            
            periods.append(period)
            current_start = current_end + timedelta(days=1)
        
        return periods
    
    def generate_weekly_periods(self, start_date: date = None, num_weeks: int = 52) -> List[BudgetPeriod]:
        """Generate weekly periods"""
        if start_date is None:
            # Start from beginning of current year
            start_date = date(datetime.now().year, 1, 1)
            # Adjust to start on Monday
            days_since_monday = start_date.weekday()
            start_date = start_date - timedelta(days=days_since_monday)
        
        periods = []
        current_start = start_date
        
        for i in range(num_weeks):
            current_end = current_start + timedelta(days=6)  # 7 days total
            
            period_id = f"weekly_{current_start.strftime('%Y_%m_%d')}"
            display_name = f"Week of {current_start.strftime('%b %d, %Y')}"
            
            period = BudgetPeriod(
                period_id=period_id,
                period_type=PeriodType.WEEKLY,
                start_date=current_start,
                end_date=current_end,
                display_name=display_name
            )
            
            periods.append(period)
            current_start = current_end + timedelta(days=1)
        
        return periods
    
    def create_custom_period(self, start_date: date, end_date: date, name: str = None) -> BudgetPeriod:
        """Create a custom date range period"""
        if name is None:
            name = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        
        period_id = f"custom_{start_date.strftime('%Y_%m_%d')}_{end_date.strftime('%Y_%m_%d')}"
        
        return BudgetPeriod(
            period_id=period_id,
            period_type=PeriodType.CUSTOM,
            start_date=start_date,
            end_date=end_date,
            display_name=name
        )
    
    def get_current_period(self, period_type: PeriodType) -> BudgetPeriod:
        """Get the period that contains today's date"""
        today = date.today()
        
        if period_type == PeriodType.MONTHLY:
            periods = self.generate_monthly_periods(today.year, 12)
        elif period_type == PeriodType.BIWEEKLY:
            # Generate periods starting from beginning of year
            start_of_year = date(today.year, 1, 1)
            periods = self.generate_biweekly_periods(start_of_year, 26)
        elif period_type == PeriodType.WEEKLY:
            start_of_year = date(today.year, 1, 1)
            periods = self.generate_weekly_periods(start_of_year, 52)
        else:
            # For custom, return a period for current month
            return self.generate_monthly_periods(today.year, 1)[0]
        
        # Find period containing today
        for period in periods:
            if period.contains_date(today):
                return period
        
        # Fallback: return current month
        return self.generate_monthly_periods(today.year, 1)[0]
    
    def save_snapshot(self, snapshot: BudgetSnapshot):
        """Save a budget snapshot for a period"""
        self.snapshots[snapshot.period.period_id] = snapshot

        print(f"🔍 Debug - self.database type: {type(self.database)}")
        print(f"🔍 Debug - self.database is None: {self.database is None}")
        
        if self.database:
            print(f"🔍 Debug - About to save snapshot: {snapshot.period.period_id}")
            success = self.database.save_budget_snapshot(snapshot)
            print(f"🔍 Debug - Save result: {success}")
        
        # Save to database with proper error handling
        if self.database:
            success = self.database.save_budget_snapshot(snapshot)
            if not success:
                print(f"❌ Failed to save snapshot {snapshot.period.period_id} to database!")
                # You might want to raise an exception here or show a user message
            else:
                print(f"✅ Successfully saved snapshot {snapshot.period.period_id} to database")
        else:
            print("⚠️ No database connection - snapshot only saved in memory")
    
    def load_snapshots_from_db(self):
        """Load all snapshots from database"""
        if self.database:
            self.snapshots = self.database.load_budget_snapshots()
    
    def get_snapshot(self, period_id: str) -> Optional[BudgetSnapshot]:
        """Get a saved snapshot by period ID"""
        return self.snapshots.get(period_id)
    
    def get_snapshots_by_date_range(self, start_date: date, end_date: date) -> List[BudgetSnapshot]:
        """Get all snapshots within a date range"""
        matching_snapshots = []
        
        for snapshot in self.snapshots.values():
            # Check if snapshot period overlaps with date range
            if (snapshot.period.start_date <= end_date and 
                snapshot.period.end_date >= start_date):
                matching_snapshots.append(snapshot)
        
        # Sort by start date
        matching_snapshots.sort(key=lambda s: s.period.start_date)
        return matching_snapshots
    
    def get_available_periods(self) -> List[BudgetPeriod]:
        """Get all periods that have saved snapshots"""
        periods = [snapshot.period for snapshot in self.snapshots.values()]
        periods.sort(key=lambda p: p.start_date, reverse=True)  # Most recent first
        return periods
    
    def delete_snapshot(self, period_id: str) -> bool:
        """Delete a snapshot"""
        # Remove from memory
        if period_id in self.snapshots:
            del self.snapshots[period_id]
        
        # Remove from database if available
        if self.database:
            return self.database.delete_budget_snapshot(period_id)
        
        return True
    
    def should_start_fresh_for_new_month(self, period_id: str) -> bool:
        """
        Determine if this is a new month that should start with fresh data
        (as opposed to reviewing a historical month)
        """
        today = date.today()
        current_month_id = f"monthly_{today.year}_{today.month:02d}"
        
        # If this is the current month and we have no snapshot for it yet,
        # we should start fresh (not copy previous month's actual spending)
        return (period_id == current_month_id and period_id not in self.snapshots)
    
    def get_previous_month_overages(self, current_period_id: str) -> Dict[str, float]:
        """
        Get overage amounts from the previous month for categories that went over budget.
        This can be used to seed the current month's starting values.
        """
        today = date.today()
        
        # Calculate previous month
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year
        
        prev_month_id = f"monthly_{prev_year}_{prev_month:02d}"
        prev_snapshot = self.get_snapshot(prev_month_id)
        
        overages = {}
        if prev_snapshot:
            for category_name, category_data in prev_snapshot.category_data.items():
                budgeted = category_data.get('budgeted', 0.0)
                actual = category_data.get('actual', 0.0)
                if actual > budgeted:  # Only categories that went over
                    overages[category_name] = actual - budgeted
        
        return overages
    
    def get_previous_month_snapshot(self) -> Optional[BudgetSnapshot]:
        """Get the previous month's snapshot"""
        today = date.today()
        
        # Calculate previous month
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year
        
        prev_month_id = f"monthly_{prev_year}_{prev_month:02d}"
        return self.get_snapshot(prev_month_id)

class SpendingAnalyzer:
    """Analyzes spending patterns and trends over time"""
    
    def __init__(self, time_tracker: TimeTracker):
        self.time_tracker = time_tracker
    
    def calculate_category_trends(self, category: str, num_periods: int = 6) -> Dict[str, float]:
        """Calculate trends for a specific category over recent periods"""
        # Get recent snapshots
        snapshots = list(self.time_tracker.snapshots.values())
        snapshots.sort(key=lambda s: s.period.start_date, reverse=True)
        recent_snapshots = snapshots[:num_periods]
        
        if len(recent_snapshots) < 2:
            return {"trend": 0.0, "average": 0.0, "variance": 0.0}
        
        # Get spending amounts
        amounts = [s.get_category_actual(category) for s in recent_snapshots]
        amounts.reverse()  # Chronological order
        
        # Calculate statistics
        average = sum(amounts) / len(amounts)
        
        # Simple trend calculation (difference between recent and older periods)
        if len(amounts) >= 2:
            recent_avg = sum(amounts[-2:]) / 2  # Last 2 periods
            older_avg = sum(amounts[:2]) / 2    # First 2 periods
            trend = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            trend = 0
        
        # Variance calculation
        variance = sum((x - average) ** 2 for x in amounts) / len(amounts)
        
        return {
            "trend": trend,  # Percentage change
            "average": average,
            "variance": variance,
            "min": min(amounts),
            "max": max(amounts),
            "periods_analyzed": len(amounts)
        }
    
    def get_spending_summary(self, num_periods: int = 6) -> Dict[str, any]:
        """Get overall spending summary across recent periods"""
        snapshots = list(self.time_tracker.snapshots.values())
        snapshots.sort(key=lambda s: s.period.start_date, reverse=True)
        recent_snapshots = snapshots[:num_periods]
        
        if not recent_snapshots:
            return {"error": "No data available"}
        
        # Calculate totals
        total_budgeted = sum(s.total_budgeted for s in recent_snapshots)
        total_spent = sum(s.total_spent for s in recent_snapshots)
        
        # Get all categories from all snapshots
        all_categories = set()
        for snapshot in recent_snapshots:
            all_categories.update(snapshot.category_data.keys())
        
        # Calculate category summaries
        category_summaries = {}
        for category in all_categories:
            amounts = [s.get_category_actual(category) for s in recent_snapshots]
            budgeted_amounts = [s.get_category_budgeted(category) for s in recent_snapshots]
            
            category_summaries[category] = {
                "total_spent": sum(amounts),
                "total_budgeted": sum(budgeted_amounts),
                "average_spent": sum(amounts) / len(amounts),
                "average_budgeted": sum(budgeted_amounts) / len(budgeted_amounts)
            }
        
        return {
            "periods_analyzed": len(recent_snapshots),
            "total_budgeted": total_budgeted,
            "total_spent": total_spent,
            "average_budgeted_per_period": total_budgeted / len(recent_snapshots),
            "average_spent_per_period": total_spent / len(recent_snapshots),
            "overall_savings_rate": ((total_budgeted - total_spent) / total_budgeted * 100) if total_budgeted > 0 else 0,
            "categories": category_summaries
        }
    
    def compare_periods(self, period1_id: str, period2_id: str) -> Dict[str, any]:
        """Compare spending between two specific periods"""
        snapshot1 = self.time_tracker.get_snapshot(period1_id)
        snapshot2 = self.time_tracker.get_snapshot(period2_id)
        
        if not snapshot1 or not snapshot2:
            return {"error": "One or both periods not found"}
        
        # Get all categories from both periods
        all_categories = set(snapshot1.category_data.keys()) | set(snapshot2.category_data.keys())
        
        category_comparisons = {}
        for category in all_categories:
            actual1 = snapshot1.get_category_actual(category)
            actual2 = snapshot2.get_category_actual(category)
            
            change = actual2 - actual1
            percent_change = (change / actual1 * 100) if actual1 > 0 else 0
            
            category_comparisons[category] = {
                f"{snapshot1.period.display_name}_actual": actual1,
                f"{snapshot2.period.display_name}_actual": actual2,
                "change": change,
                "percent_change": percent_change
            }
        
        total_change = snapshot2.total_spent - snapshot1.total_spent
        total_percent_change = (total_change / snapshot1.total_spent * 100) if snapshot1.total_spent > 0 else 0
        
        return {
            "period1": snapshot1.period.display_name,
            "period2": snapshot2.period.display_name,
            "total_change": total_change,
            "total_percent_change": total_percent_change,
            "categories": category_comparisons
        }