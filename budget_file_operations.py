# budget_file_operations.py - Manages file operations (CSV, backup, import/export)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import subprocess
import platform
from budget_calculator import BudgetCalculator

class FileOperations:
    """Manages all file operations including CSV import/export, backups, and data location"""
    
    def __init__(self, app):
        self.app = app
    
    def export_csv(self):
        """Export current data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"budget_export_{self.app.view_mode.value.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                first_paycheck, second_paycheck = self.app.data_manager.get_safe_paychecks()
                spending = self.app.data_manager.get_safe_spending()
                
                # Get data for export
                scenario = self.app.budget_data.get_scenario(self.app.current_scenario_name)
                calculator = BudgetCalculator(scenario)
                category_results = calculator.calculate_all_categories(first_paycheck, second_paycheck, self.app.view_mode, spending)
                csv_data = calculator.export_to_csv_data(category_results, self.app.view_mode, first_paycheck, second_paycheck)
                
                # Write CSV
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(csv_data)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def manual_csv_backup(self):
        """Create a manual CSV backup"""
        success = self.app.database.create_csv_backup()
        if success:
            messagebox.showinfo("Success", "CSV backup created successfully!")
        else:
            messagebox.showerror("Error", "Failed to create CSV backup")
    
    def import_from_csv(self):
        """Import data from a CSV backup"""
        # Get available CSV files
        csv_files = self.app.database.get_available_csv_backups()
        
        if not csv_files:
            messagebox.showinfo("No Backups", "No CSV backup files found.")
            return
        
        # Show selection dialog
        import_dialog = tk.Toplevel(self.app.root)
        import_dialog.title("Import from CSV Backup")
        import_dialog.geometry("400x300")
        import_dialog.transient(self.app.root)
        import_dialog.grab_set()
        
        ttk.Label(import_dialog, text="Select CSV file to import:").pack(pady=10)
        
        # Listbox for file selection
        listbox = tk.Listbox(import_dialog)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        for csv_file in csv_files:
            listbox.insert(tk.END, csv_file)
        
        def do_import():
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Error", "Please select a file to import")
                return
            
            selected_file = csv_files[selection[0]]
            
            if messagebox.askyesno("Confirm Import", 
                                 f"This will replace all current data with data from {selected_file}. Continue?"):
                success = self.app.database.load_from_csv_backup(selected_file)
                if success:
                    self.app.data_manager.load_initial_data()  # Reload current view
                    messagebox.showinfo("Success", "Data imported successfully!")
                    import_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to import data")
        
        button_frame = ttk.Frame(import_dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Import", command=do_import).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=import_dialog.destroy).pack(side="left", padx=5)
    
    def show_data_location(self):
        """Show where data files are stored"""
        data_dir = self.app.database.data_dir
        
        info_dialog = tk.Toplevel(self.app.root)
        info_dialog.title("Data Storage Location")
        info_dialog.geometry("500x200")
        info_dialog.transient(self.app.root)
        info_dialog.grab_set()
        
        ttk.Label(info_dialog, text="Your budget data is stored in:", font=("", 12, "bold")).pack(pady=10)
        
        # Path display
        path_frame = ttk.Frame(info_dialog)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        path_text = tk.Text(path_frame, height=2, wrap=tk.WORD)
        path_text.insert(1.0, data_dir)
        path_text.config(state="disabled")
        path_text.pack(fill="x")
        
        # Buttons
        button_frame = ttk.Frame(info_dialog)
        button_frame.pack(pady=20)
        
        def open_folder():
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", data_dir])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", data_dir])
                else:  # Linux
                    subprocess.run(["xdg-open", data_dir])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")
        
        ttk.Button(button_frame, text="Open Folder", command=open_folder).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=info_dialog.destroy).pack(side="left", padx=5)