import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import requests
import json
from datetime import datetime

class CSVAPIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("API Call Application")
        self.root.geometry("600x500")
        
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Main content
        ttk.Label(self.frame, text="API Key:").pack()
        self.api_key = tk.StringVar()
        ttk.Entry(self.frame, textvariable=self.api_key, width=50).pack(pady=5)
        
        ttk.Button(self.frame, text="Select CSV file", command=self.load_csv).pack(pady=10)
        
        self.progress = ttk.Progressbar(self.frame, length=300, mode='determinate')
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(self.frame, text="")
        self.status_label.pack(pady=5)
        
        # Developer info at the bottom
        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        dev_frame = ttk.LabelFrame(self.frame, text="Developer Contact", padding="10")
        dev_frame.pack(fill=tk.X)
        ttk.Label(dev_frame, text="This is a simple application to send a request with API key to an API.").pack()
        ttk.Label(dev_frame, text="Samane Sharifi Monfared").pack()
        ttk.Label(dev_frame, text="Personal: samane.sharify@gmail.com").pack()
        ttk.Label(dev_frame, text="Please contact me in case of any issue.").pack()

    def load_csv(self):
        input_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if input_file:
            self.process_file(input_file)
    
    def process_file(self, input_file):
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter API key")
            return
            
        try:
            with open(input_file, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
                total_rows = len(rows) - 1
                
                self.progress['value'] = 0
                self.progress['maximum'] = total_rows
                
                header = rows[0] + ['UPRN', 'ADDRESS', 'POSTCODE', 'X_COORDINATE', 'Y_COORDINATE', 'MATCH', 'API_RESPONSE']
                output_rows = [header]
                
                for i, row in enumerate(rows[1:], 1):
                    self.progress['value'] = i
                    self.status_label.config(text=f"Processing row {i} of {total_rows}")
                    self.root.update()
                    
                    query = ','.join(row[2:11])
                    result = self.call_api(query)
                    
                    if 'results' in result and result['results']:
                        dpa = result['results'][0].get('DPA', {})
                        new_row = row + [
                            str(dpa.get('UPRN', '')),
                            str(dpa.get('ADDRESS', '')),
                            str(dpa.get('POSTCODE', '')),
                            str(dpa.get('X_COORDINATE', '')),
                            str(dpa.get('Y_COORDINATE', '')),
                            str(dpa.get('MATCH', '')),
                            str(result)
                        ]
                    else:
                        new_row = row + ['', '', '', '', '', '', str(result)]
                    
                    output_rows.append(new_row)
            
            self.save_results(input_file, output_rows)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {str(e)}")
    
    def call_api(self, query):
        url = 'https://api.os.uk/search/match/v1/match'
        params = {
            'maxresults': 1,
            'query': query,
            'key': self.api_key.get()
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def save_results(self, input_file, rows):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{input_file.rsplit('.', 1)[0]}_results_{timestamp}.csv"
        
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
            
        messagebox.showinfo("Success", f"Results saved to {output_file}")
        self.status_label.config(text="Processing complete!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVAPIApp(root)
    root.mainloop()