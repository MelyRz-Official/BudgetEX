# budget_dashboard.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BudgetDashboard:
    """Handles the dashboard tab with charts and visualizations"""
    
    def __init__(self, parent_frame, config):
        self.parent_frame = parent_frame
        self.config = config
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Setup the dashboard with charts"""
        # Set matplotlib style
        plt.style.use(self.config.chart_style)
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 7))
        self.fig.patch.set_facecolor('#1c1c1c' if self.config.theme == 'dark' else '#ffffff')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        self.refresh_button = ttk.Button(self.parent_frame, text="Refresh Charts", 
                                        command=self.update_charts)
        self.refresh_button.pack(pady=5)
        
        # Initialize with empty charts
        self.update_charts()
    
    def update_charts(self, category_results=None, view_mode=None):
        """Update dashboard charts with current data"""
        self.ax1.clear()
        self.ax2.clear()
        
        if not category_results:
            # Show empty state
            self.ax1.text(0.5, 0.5, 'No Data Available\nEnter budget amounts to see charts', 
                         ha='center', va='center', transform=self.ax1.transAxes, fontsize=12)
            self.ax2.text(0.5, 0.5, 'No Data Available\nEnter budget amounts to see charts', 
                         ha='center', va='center', transform=self.ax2.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        # Prepare data for charts
        categories = []
        budgeted_amounts = []
        actual_amounts = []
        
        for name, result in category_results.items():
            if result.budgeted > 0:  # Only show categories with budget
                categories.append(name.replace(' ', '\n'))  # Line breaks for better display
                budgeted_amounts.append(result.budgeted)
                actual_amounts.append(result.actual)
        
        if not categories:
            # No data to show
            self.ax1.text(0.5, 0.5, 'No Budget Data', ha='center', va='center', 
                         transform=self.ax1.transAxes, fontsize=12)
            self.ax2.text(0.5, 0.5, 'No Budget Data', ha='center', va='center', 
                         transform=self.ax2.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        # Create pie chart of budgeted amounts
        self._create_pie_chart(categories, budgeted_amounts, view_mode)
        
        # Create bar chart comparison
        self._create_bar_chart(categories, budgeted_amounts, actual_amounts, view_mode)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _create_pie_chart(self, categories, budgeted_amounts, view_mode):
        """Create pie chart showing budget allocation"""
        colors = plt.cm.Set3(range(len(categories)))
        
        # Only show slices for categories with non-zero amounts
        non_zero_categories = []
        non_zero_amounts = []
        non_zero_colors = []
        
        for i, amount in enumerate(budgeted_amounts):
            if amount > 0:
                non_zero_categories.append(categories[i])
                non_zero_amounts.append(amount)
                non_zero_colors.append(colors[i])
        
        if non_zero_amounts:
            wedges, texts, autotexts = self.ax1.pie(
                non_zero_amounts, 
                labels=non_zero_categories, 
                autopct='%1.1f%%',
                startangle=90, 
                colors=non_zero_colors
            )
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontsize(8)
                autotext.set_weight('bold')
        
        # Set title based on view mode
        view_text = view_mode.value if view_mode else "Budget"
        chart_title = f"Budget Allocation ({view_text})"
        self.ax1.set_title(chart_title, fontsize=14, fontweight='bold')
    
    def _create_bar_chart(self, categories, budgeted_amounts, actual_amounts, view_mode):
        """Create bar chart comparing budgeted vs actual spending"""
        x_pos = range(len(categories))
        width = 0.35
        
        # Create bars
        bars1 = self.ax2.bar(
            [x - width/2 for x in x_pos], 
            budgeted_amounts, 
            width,
            label='Budgeted', 
            alpha=0.8, 
            color=self.config.chart_colors.get("budgeted", "#1f77b4")
        )
        
        bars2 = self.ax2.bar(
            [x + width/2 for x in x_pos], 
            actual_amounts, 
            width,
            label='Actual', 
            alpha=0.8, 
            color=self.config.chart_colors.get("actual", "#ff7f0e")
        )
        
        # Customize chart
        self.ax2.set_xlabel('Categories', fontweight='bold')
        view_text = view_mode.value if view_mode else "Amount"
        self.ax2.set_ylabel(f'Amount ($) - {view_text}', fontweight='bold')
        
        title = f'Budgeted vs Actual Spending ({view_text})'
        self.ax2.set_title(title, fontsize=14, fontweight='bold')
        
        self.ax2.set_xticks(x_pos)
        self.ax2.set_xticklabels(categories, rotation=45, ha='right')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        self._add_bar_labels(bars1)
        self._add_bar_labels(bars2)
    
    def _add_bar_labels(self, bars):
        """Add value labels on top of bars"""
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                self.ax2.text(
                    bar.get_x() + bar.get_width()/2., 
                    height + height*0.01,
                    f'${height:.0f}', 
                    ha='center', 
                    va='bottom', 
                    fontsize=8
                )
    
    def set_refresh_callback(self, callback):
        """Set callback function for refresh button"""
        self.refresh_button.config(command=callback)
    
    def update_theme(self, theme):
        """Update chart theme"""
        self.fig.patch.set_facecolor('#1c1c1c' if theme == 'dark' else '#ffffff')
        self.canvas.draw()