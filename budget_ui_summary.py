# budget_ui_summary.py - Manages the summary section UI
import tkinter as tk
from tkinter import ttk

class SummaryManager:
    """Manages the summary section at the bottom of the budget tab"""
    
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
        self.summary_labels = {}
    
    def create_summary_section(self):
        """Create the summary section"""
        summary_frame = ttk.LabelFrame(self.parent_frame, text="Summary", padding=10)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        summary_row = ttk.Frame(summary_frame)
        summary_row.pack(fill="x")
        
        # Create summary labels
        labels = ["Total Budgeted:", "Total Spent:", "Remaining:", "Over/Under:"]
        for i, label in enumerate(labels):
            ttk.Label(summary_row, text=label).grid(row=0, column=i*2, padx=10, sticky="e")
            self.summary_labels[label] = ttk.Label(summary_row, text="$0.00", font=("", 11, "bold"))
            self.summary_labels[label].grid(row=0, column=i*2+1, padx=10, sticky="w")
    
    def update_summary_display(self, summary):
        """Update summary display with calculation results"""
        currency = self.app.config.currency_symbol
        decimal_places = self.app.config.decimal_places
        
        self.summary_labels["Total Budgeted:"].config(
            text=f"{currency}{summary.total_budgeted:.{decimal_places}f}")
        self.summary_labels["Total Spent:"].config(
            text=f"{currency}{summary.total_spent:.{decimal_places}f}")
        self.summary_labels["Remaining:"].config(
            text=f"{currency}{summary.remaining:.{decimal_places}f}")
        
        over_under_text = f"{currency}{summary.over_under:.{decimal_places}f} {summary.over_under_status}"
        self.summary_labels["Over/Under:"].config(
            text=over_under_text, foreground=summary.over_under_color)