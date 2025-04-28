# smart_grid_fuzzy_system.py

import random
import tkinter as tk
from tkinter import messagebox

# ---- Fuzzification Functions ----
def fuzzify_voltage(voltage):
    if voltage < 210:
        return "Low"
    elif 210 <= voltage <= 230:
        return "Medium"
    else:
        return "High"

def fuzzify_frequency(frequency):
    if 49.8 <= frequency <= 50.2:
        return "Stable"
    else:
        return "Unstable"

def fuzzify_load(load_balance):
    if load_balance < 0.1:
        return "Balanced"
    else:
        return "Unbalanced"

# ---- Fuzzy Rules Processing ----
def apply_fuzzy_rules(voltage_status, frequency_status, load_status):
    if voltage_status == "High" and frequency_status == "Unstable" and load_status == "Unbalanced":
        return "High"
    elif voltage_status == "Medium" and frequency_status == "Stable" and load_status == "Balanced":
        return "Low"
    elif voltage_status == "Low" and frequency_status == "Unstable":
        return "Moderate"
    else:
        return "Low"

# ---- Defuzzification (Decision Making) ----
def decide_action(severity):
    if severity == "High":
        return "Isolate faulty section"
    elif severity == "Moderate":
        return "Balance loads dynamically"
    else:
        return "Monitor only"

# ---- Simulate Grid Data ----
def generate_anomaly_case():
    voltage = random.uniform(200, 250)          # Simulated voltage (V)
    frequency = random.uniform(49.0, 51.0)       # Simulated frequency (Hz)
    load_balance = random.uniform(0.0, 0.3)      # Simulated load imbalance (0 to 0.3)
    return voltage, frequency, load_balance

# ---- Console Mode (Optional) ----
def run_console_mode():
    voltage, frequency, load = generate_anomaly_case()

    print(f"Simulated Data -> Voltage: {voltage:.2f}V, Frequency: {frequency:.2f}Hz, Load imbalance: {load:.2f}")

    voltage_status = fuzzify_voltage(voltage)
    frequency_status = fuzzify_frequency(frequency)
    load_status = fuzzify_load(load)

    print(f"Fuzzified Data -> Voltage: {voltage_status}, Frequency: {frequency_status}, Load: {load_status}")

    severity = apply_fuzzy_rules(voltage_status, frequency_status, load_status)
    action = decide_action(severity)

    print(f"Detected Severity: {severity}")
    print(f"Recommended Action: {action}")

# ---- UI Dashboard Mode ----
def detect_and_correct():
    voltage, frequency, load = generate_anomaly_case()

    voltage_status = fuzzify_voltage(voltage)
    frequency_status = fuzzify_frequency(frequency)
    load_status = fuzzify_load(load)

    severity = apply_fuzzy_rules(voltage_status, frequency_status, load_status)
    action = decide_action(severity)

    voltage_label.config(text=f"Voltage: {voltage:.2f}V ({voltage_status})")
    frequency_label.config(text=f"Frequency: {frequency:.2f}Hz ({frequency_status})")
    load_label.config(text=f"Load Imbalance: {load:.2f} ({load_status})")
    severity_label.config(text=f"Detected Severity: {severity}")
    action_label.config(text=f"Recommended Action: {action}")

    if severity == "High":
        messagebox.showwarning("High Severity Fault", "Immediate action needed: Isolate faulty section!")

# ---- Run UI Dashboard ----
def run_dashboard():
    global voltage_label, frequency_label, load_label, severity_label, action_label

    window = tk.Tk()
    window.title("Smart Grid Anomaly Detection System")

    frame = tk.Frame(window, padx=20, pady=20)
    frame.pack()

    title = tk.Label(frame, text="Smart Grid Monitoring", font=("Helvetica", 20))
    title.pack(pady=10)

    voltage_label = tk.Label(frame, text="Voltage:", font=("Helvetica", 14))
    voltage_label.pack()

    frequency_label = tk.Label(frame, text="Frequency:", font=("Helvetica", 14))
    frequency_label.pack()

    load_label = tk.Label(frame, text="Load Imbalance:", font=("Helvetica", 14))
    load_label.pack()

    severity_label = tk.Label(frame, text="Detected Severity:", font=("Helvetica", 14))
    severity_label.pack()

    action_label = tk.Label(frame, text="Recommended Action:", font=("Helvetica", 14))
    action_label.pack()

    detect_button = tk.Button(frame, text="Run Detection", command=detect_and_correct, bg="green", fg="white", font=("Helvetica", 14))
    detect_button.pack(pady=20)

    window.mainloop()

# ---- Main Execution ----
if __name__ == "__main__":
    mode = input("Choose mode: (1) Console  (2) Dashboard UI  --> ")

    if mode.strip() == "1":
        run_console_mode()
    elif mode.strip() == "2":
        run_dashboard()
    else:
        print("Invalid option. Please choose 1 or 2.")
