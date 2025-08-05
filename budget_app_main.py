# budget_app_main.py - Streamlined main application file
import tkinter as tk
from budget_app_core import BudgetApp

def main():
    """Main entry point for the Budget Application"""
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()