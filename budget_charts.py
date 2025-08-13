"""
Budget Charts Module
Clean, minimalistic chart creation with proper side-by-side layouts
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import calendar

class BudgetCharts:
    def __init__(self, parent_frame, sv_ttk_available=False):
        self.parent_frame = parent_frame
        self.sv_ttk_available = sv_ttk_available
        self.setup_matplotlib_style()
    
    def setup_matplotlib_style(self):
        """Setup clean matplotlib styling"""
        if self.sv_ttk_available:
            plt.style.use('dark_background')
            self.plot_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        else:
            plt.style.use('default')
            self.plot_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    def clear_charts(self):
        """Clear existing charts"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
    
    def create_monthly_trends_chart(self, data):
        """Create clean monthly spending trends chart"""
        if not data:
            self.show_no_data_message("No data available for Monthly Spending Trends")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))  # Side by side
        fig.suptitle('Monthly Spending Trends', fontsize=14, fontweight='bold')
        
        months = list(data.keys())
        total_spending = [sum(data[month]['categories'].values()) for month in months]
        incomes = [data[month]['income'] for month in months]
        
        # Left chart - Spending trend
        ax1.plot(months, total_spending, marker='o', linewidth=2, markersize=6, color=self.plot_colors[0])
        ax1.set_title('Total Monthly Spending')
        ax1.set_ylabel('Amount ($)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Right chart - Income vs Spending
        x_pos = np.arange(len(months))
        width = 0.35
        
        ax2.bar(x_pos - width/2, incomes, width, label='Income', color=self.plot_colors[1], alpha=0.7)
        ax2.bar(x_pos + width/2, total_spending, width, label='Spending', color=self.plot_colors[0], alpha=0.7)
        
        ax2.set_title('Income vs Spending')
        ax2.set_ylabel('Amount ($)')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(months, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        self.embed_chart(fig)
    
    def create_category_breakdown_chart(self, categories, current_month, current_year):
        """Create clean category breakdown"""
        category_names = []
        amounts = []
        colors = []
        
        for i, (category_name, data) in enumerate(categories.items()):
            try:
                spent = data['spending'].get()
            except:
                spent = 0
            
            if spent > 0:
                category_names.append(category_name)
                amounts.append(spent)
                colors.append(self.plot_colors[i % len(self.plot_colors)])
        
        if not amounts:
            self.show_no_data_message("No spending data for current month")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))  # Side by side
        fig.suptitle(f'Category Breakdown - {calendar.month_name[current_month]} {current_year}', 
                    fontsize=14, fontweight='bold')
        
        # Left - Pie chart
        ax1.pie(amounts, labels=category_names, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Spending by Category')
        
        # Right - Bar chart  
        ax2.barh(category_names, amounts, color=colors, alpha=0.7)
        ax2.set_title('Spending Amounts')
        ax2.set_xlabel('Amount ($)')
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        self.embed_chart(fig)
    
    def create_budget_vs_actual_chart(self, categories, first_paycheck, second_paycheck, view_mode, current_month, current_year):
        """Create clean budget vs actual comparison"""
        category_names = []
        budgeted_amounts = []
        actual_amounts = []
        
        for category_name, data in categories.items():
            category = data['category']
            budgeted, _ = category.calculate_budgeted_amount(first_paycheck, second_paycheck, view_mode)
            
            try:
                actual = data['spending'].get()
            except:
                actual = 0
            
            category_names.append(category_name)
            budgeted_amounts.append(budgeted)
            actual_amounts.append(actual)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle(f'Budget vs Actual - {calendar.month_name[current_month]} {current_year}', 
                    fontsize=14, fontweight='bold')
        
        x_pos = np.arange(len(category_names))
        width = 0.35
        
        ax.bar(x_pos - width/2, budgeted_amounts, width, label='Budgeted', 
               color=self.plot_colors[1], alpha=0.7)
        ax.bar(x_pos + width/2, actual_amounts, width, label='Actual', 
               color=self.plot_colors[0], alpha=0.7)
        
        ax.set_xlabel('Categories')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Budgeted vs Actual Spending')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(category_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        self.embed_chart(fig)
    
    def create_savings_progress_chart(self, data):
        """Create clean savings progress chart"""
        if not data:
            self.show_no_data_message("No data available for Savings Progress")
            return
        
        months = list(data.keys())
        savings_categories = ['Roth IRA', 'General Savings']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))  # Side by side
        fig.suptitle('Savings Progress Over Time', fontsize=14, fontweight='bold')
        
        # Left - Individual categories
        for i, savings_cat in enumerate(savings_categories):
            amounts = []
            for month in months:
                amount = data[month]['categories'].get(savings_cat, 0)
                amounts.append(amount)
            
            ax1.plot(months, amounts, marker='o', linewidth=2, markersize=6, 
                    label=savings_cat, color=self.plot_colors[i])
        
        ax1.set_title('Individual Savings Categories')
        ax1.set_ylabel('Amount ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Right - Total savings
        total_savings = []
        for month in months:
            month_total = sum(data[month]['categories'].get(cat, 0) for cat in savings_categories)
            total_savings.append(month_total)
        
        ax2.bar(months, total_savings, color=self.plot_colors[2], alpha=0.7)
        ax2.set_title('Total Monthly Savings')
        ax2.set_ylabel('Amount ($)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        self.embed_chart(fig)
    
    def create_income_vs_expenses_chart(self, data):
        """Create clean income vs expenses chart"""
        if not data:
            self.show_no_data_message("No data available for Income vs Expenses")
            return
        
        months = list(data.keys())
        incomes = []
        expenses = []
        savings = []
        
        savings_categories = ['Roth IRA', 'General Savings']
        
        for month in months:
            month_data = data[month]
            income = month_data['income']
            
            month_expenses = 0
            month_savings = 0
            
            for category, amount in month_data['categories'].items():
                if category in savings_categories:
                    month_savings += amount
                else:
                    month_expenses += amount
            
            incomes.append(income)
            expenses.append(month_expenses)
            savings.append(month_savings)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))  # Side by side
        fig.suptitle('Income vs Expenses Analysis', fontsize=14, fontweight='bold')
        
        # Left - Stacked bar chart
        x_pos = np.arange(len(months))
        ax1.bar(x_pos, expenses, label='Expenses', color=self.plot_colors[0], alpha=0.7)
        ax1.bar(x_pos, savings, bottom=expenses, label='Savings', color=self.plot_colors[1], alpha=0.7)
        ax1.plot(x_pos, incomes, marker='o', linewidth=2, markersize=6, 
                color=self.plot_colors[3], label='Income', linestyle='--')
        
        ax1.set_title('Monthly Breakdown')
        ax1.set_ylabel('Amount ($)')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(months, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Right - Net remaining
        net_remaining = [inc - exp - sav for inc, exp, sav in zip(incomes, expenses, savings)]
        colors = ['green' if x >= 0 else 'red' for x in net_remaining]
        
        ax2.bar(months, net_remaining, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_title('Net Remaining')
        ax2.set_ylabel('Amount ($)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        self.embed_chart(fig)
    
    def show_no_data_message(self, message):
        """Show simple no data message"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, transform=ax.transAxes, fontsize=16, 
                ha='center', va='center', fontweight='bold')
        ax.text(0.5, 0.4, "Add some budget data to see charts!", transform=ax.transAxes, 
                fontsize=12, ha='center', va='center', style='italic')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.embed_chart(fig)
    
    def embed_chart(self, fig):
        """Embed matplotlib figure in tkinter"""
        canvas = FigureCanvasTkAgg(fig, self.parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)