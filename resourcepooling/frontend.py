import tkinter as tk
from tkinter import messagebox
import requests

API_BASE = "http://127.0.0.1:8000"  # Make sure your FastAPI server is running here

class ResourcePoolApp:
    def __init__(self, root):
        self.root = root
        root.title("Resource Pool Manager")

        # Available resources label
        self.available_label = tk.Label(root, text="Available resources: ")
        self.available_label.grid(row=0, column=0, columnspan=2, pady=5)

        # Acquire resource with timeout
        tk.Label(root, text="Acquire Resource (timeout sec):").grid(row=1, column=0, sticky="e")
        self.timeout_entry = tk.Entry(root)
        self.timeout_entry.insert(0, "5")  # default timeout
        self.timeout_entry.grid(row=1, column=1)

        self.acquire_btn = tk.Button(root, text="Acquire", command=self.acquire_resource)
        self.acquire_btn.grid(row=2, column=0, columnspan=2, pady=5)

        # Release resource by ID
        tk.Label(root, text="Release Resource (ID):").grid(row=3, column=0, sticky="e")
        self.release_entry = tk.Entry(root)
        self.release_entry.grid(row=3, column=1)

        self.release_btn = tk.Button(root, text="Release", command=self.release_resource)
        self.release_btn.grid(row=4, column=0, columnspan=2, pady=5)

        # Add new resource
        self.add_btn = tk.Button(root, text="Add Resource", command=self.add_resource)
        self.add_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Response display
        self.response_text = tk.Text(root, height=8, width=50)
        self.response_text.grid(row=6, column=0, columnspan=2, pady=10)

        self.refresh_available()

    def refresh_available(self):
        try:
            response = requests.get(f"{API_BASE}/available/")
            if response.status_code == 200:
                available = response.json().get("available_resources", 0)
                self.available_label.config(text=f"Available resources: {available}")
            else:
                self.available_label.config(text="Failed to fetch available resources")
        except Exception as e:
            self.available_label.config(text="Error connecting to API")

    def acquire_resource(self):
        timeout = self.timeout_entry.get()
        try:
            timeout_val = float(timeout)
        except ValueError:
            messagebox.showerror("Input Error", "Timeout must be a number")
            return

        try:
            response = requests.post(f"{API_BASE}/acquire/", json={"timeout": timeout_val})
            if response.status_code == 200:
                msg = response.json().get("message", "Resource acquired")
                self.response_text.insert(tk.END, msg + "\n")
                self.refresh_available()
            else:
                error = response.json().get("detail", "Failed to acquire resource")
                self.response_text.insert(tk.END, "Error: " + error + "\n")
        except Exception as e:
            self.response_text.insert(tk.END, f"Connection error: {e}\n")

    def release_resource(self):
        resource_id = self.release_entry.get()
        if not resource_id.isdigit():
            messagebox.showerror("Input Error", "Resource ID must be an integer")
            return

        try:
            response = requests.post(f"{API_BASE}/release/?resource_id={resource_id}")
            if response.status_code == 200:
                msg = response.json().get("message", "Resource released")
                self.response_text.insert(tk.END, msg + "\n")
                self.refresh_available()
            else:
                error = response.json().get("detail", "Failed to release resource")
                self.response_text.insert(tk.END, "Error: " + error + "\n")
        except Exception as e:
            self.response_text.insert(tk.END, f"Connection error: {e}\n")

    def add_resource(self):
        try:
            response = requests.post(f"{API_BASE}/add_resource/")
            if response.status_code == 200:
                msg = response.json().get("message", "Resource added")
                self.response_text.insert(tk.END, msg + "\n")
                self.refresh_available()
            else:
                error = response.json().get("detail", "Failed to add resource")
                self.response_text.insert(tk.END, "Error: " + error + "\n")
        except Exception as e:
            self.response_text.insert(tk.END, f"Connection error: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResourcePoolApp(root)
    root.mainloop()
