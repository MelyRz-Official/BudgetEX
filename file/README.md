# Personal Budget Manager

A modern desktop budgeting application built with Python and tkinter, featuring a dark theme and intelligent budget calculations with both fixed and percentage-based categories.

## Features

### 🎯 **Smart Budget Categories**
- **Fixed Amount Categories**: HOA, Utilities, Subscriptions, Therapy (marked with "Fixed")
  - Dollar amounts stay constant regardless of paycheck size
  - Percentages automatically adjust when paycheck changes
- **Percentage-Based Categories**: Roth IRA, Savings, Vacation Fund, etc.
  - Percentages stay constant, dollar amounts adjust with paycheck

### 💰 **Real-Time Budget Tracking**
- Enter your paycheck amount for automatic calculations
- Type directly into "Actual Spent" fields - no double-clicking needed
- Live updates as you type
- Color-coded status indicators (Green=Under Budget, Red=Over Budget, Gray=Not Set)

### 📊 **Visual Dashboard**
- Pie chart showing budget allocation
- Bar chart comparing budgeted vs actual spending
- Value labels on all chart elements
- Dark theme optimized charts

### 🗄️ **Data Management**
- SQLite database for reliable data storage
- Multiple budget scenarios (July-Dec 2025, Fresh New Year plans)
- CSV export functionality
- Manual save system (saves only when "Save Data" button is clicked)

### 🎨 **Modern Interface**
- Dark Sun Valley theme
- Clean, organized layout
- Real-time summary calculations
- Intuitive user experience

## Installation

### Prerequisites
```bash
pip install sv-ttk matplotlib
```

### Setup
1. Download the `budget_app.py` file
2. Run the application:
   ```bash
   python budget_app.py
   ```

## Usage

### Getting Started
1. **Select Budget Scenario**: Choose from dropdown (July-December 2025, Fresh New Year scenarios)
2. **Enter Paycheck Amount**: Type your paycheck amount in the top field
3. **Enter Actual Spending**: Type directly in the "Actual Spent ($)" column for each category
4. **Save Your Data**: Click "Save Data" button to persist changes to database

### Key Features

#### Budget Scenarios
- **July-December 2025**: Current year budget plan
- **Fresh New Year (Jan-May)**: High Roth IRA contributions
- **Fresh New Year (June-Dec)**: Post-Roth IRA max-out plan

#### Fixed vs Percentage Categories
- **Fixed categories** (marked with "Fixed"):
  - HOA: $1,078.81
  - Utilities: $60.00
  - Subscriptions: $90.00
  - Therapy: $44.00
- **Percentage categories**: Adjust dollar amounts based on paycheck size

#### Data Persistence
- **Manual Save System**: Data is saved to database ONLY when you click "Save Data"
- **Automatic Load**: Data automatically loads when switching scenarios or restarting app
- **Database File**: Creates `budget_data.db` in the same directory as the script

### Dashboard Charts
- Switch to "Dashboard" tab for visual analysis
- Click "Refresh Charts" to update after making changes
- Charts automatically reflect fixed vs percentage category behavior

### Export & Management
- **Export CSV**: Export current budget state to CSV file
- **Clear All Spending**: Reset all actual spending to $0 for current scenario
- **Scenario Switching**: Seamlessly switch between different budget plans

## File Structure
```
budget_app.py          # Main application file
budget_data.db         # SQLite database (created automatically)
exported_budget_*.csv  # Exported CSV files (when using export)
```

## Database Schema

### budget_data table
- `scenario`: Budget scenario name
- `paycheck_amount`: Your entered paycheck amount
- `category`: Budget category name
- `actual_spent`: Amount actually spent
- `date_updated`: Last update timestamp

### When Data is Saved
- **Manual Save Only**: Data is saved to the database ONLY when you click the "Save Data" button
- **No Auto-Save**: Changes you make are temporary until you click "Save Data"
- **Scenario Switching**: Automatically saves current scenario before switching to new one
- **Load on Startup**: Automatically loads saved data when app starts

## Troubleshooting

### Theme Issues
If the dark theme doesn't apply:
```bash
pip install sv-ttk
```

### Database Issues
- Database file is created automatically in the same directory
- If database gets corrupted, delete `budget_data.db` and restart the app

### Chart Display Issues
- Ensure matplotlib is installed: `pip install matplotlib`
- Charts update automatically when data changes

## Tips
- Use the "Actual Spent" fields to track real spending against your budget
- Fixed categories (HOA, Utilities, etc.) will always maintain their dollar amounts
- Export to CSV for external analysis or record-keeping
- Switch scenarios to plan for different time periods
- Remember to click "Save Data" to persist your changes!

## Support
- Check that all dependencies are installed
- Ensure you have write permissions in the directory for database creation
- For theme issues, verify `sv-ttk` is properly installed