# smart_grid_fuzzy_visual_ui.py

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import random
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

# ---- Define Fuzzy Variables ----

# Input Variables
voltage_deviation = ctrl.Antecedent(np.arange(-20, 21, 1), 'Voltage Deviation')  # -20V to +20V
frequency_variation = ctrl.Antecedent(np.arange(-1, 1.1, 0.1), 'Frequency Variation')  # -1Hz to +1Hz
load_imbalance = ctrl.Antecedent(np.arange(0, 0.31, 0.01), 'Load Imbalance')  # 0% to 30%

# Output Variable
fault_severity = ctrl.Consequent(np.arange(0, 101, 1), 'Fault Severity')  # 0% to 100% severity

# ---- Membership Functions ----

voltage_deviation['Low'] = fuzz.trimf(voltage_deviation.universe, [-20, -20, 0])
voltage_deviation['Normal'] = fuzz.trimf(voltage_deviation.universe, [-5, 0, 5])
voltage_deviation['High'] = fuzz.trimf(voltage_deviation.universe, [0, 20, 20])

frequency_variation['Unstable Low'] = fuzz.trimf(frequency_variation.universe, [-1, -1, -0.2])
frequency_variation['Stable'] = fuzz.trimf(frequency_variation.universe, [-0.2, 0, 0.2])
frequency_variation['Unstable High'] = fuzz.trimf(frequency_variation.universe, [0.2, 1, 1])

load_imbalance['Balanced'] = fuzz.trimf(load_imbalance.universe, [0, 0, 0.1])
load_imbalance['Moderate'] = fuzz.trimf(load_imbalance.universe, [0.05, 0.15, 0.25])
load_imbalance['Unbalanced'] = fuzz.trimf(load_imbalance.universe, [0.2, 0.3, 0.3])

fault_severity['Low'] = fuzz.trimf(fault_severity.universe, [0, 0, 30])
fault_severity['Moderate'] = fuzz.trimf(fault_severity.universe, [20, 50, 80])
fault_severity['High'] = fuzz.trimf(fault_severity.universe, [70, 100, 100])

# ---- Fuzzy Rules ----

rules = [
    ctrl.Rule(voltage_deviation['High'] & frequency_variation['Unstable High'] & load_imbalance['Unbalanced'], fault_severity['High']),
    ctrl.Rule(voltage_deviation['Low'] & frequency_variation['Unstable Low'], fault_severity['Moderate']),
    ctrl.Rule(voltage_deviation['Normal'] & frequency_variation['Stable'] & load_imbalance['Balanced'], fault_severity['Low']),
    ctrl.Rule(load_imbalance['Unbalanced'], fault_severity['Moderate']),
    ctrl.Rule(frequency_variation['Unstable Low'] | frequency_variation['Unstable High'], fault_severity['Moderate']),
]

fault_ctrl = ctrl.ControlSystem(rules)
fault_detector = ctrl.ControlSystemSimulation(fault_ctrl)

# ---- Simulate Grid Data ----

def generate_anomaly_case():
    voltage = random.uniform(200, 250)         # in Volts
    frequency = random.uniform(49.0, 51.0)      # in Hz
    load = random.uniform(0.0, 0.3)             # Load imbalance percentage
    return voltage, frequency, load

# ---- UI Functions ----

def detect_and_display():
    voltage, frequency, load = generate_anomaly_case()

    # Preprocess for fuzzy system
    voltage_dev = voltage - 230    # Assuming 230V is nominal
    freq_var = frequency - 50.0    # Assuming 50Hz is nominal

    # Pass to fuzzy controller
    fault_detector.input['Voltage Deviation'] = voltage_dev
    fault_detector.input['Frequency Variation'] = freq_var
    fault_detector.input['Load Imbalance'] = load
    fault_detector.compute()

    severity_score = fault_detector.output['Fault Severity']

    # Determine action based on severity
    if severity_score >= 70:
        action = "Isolate faulty section immediately"
    elif severity_score >= 30:
        action = "Perform dynamic load balancing"
    else:
        action = "Monitor only"

    # Update UI Labels
    voltage_label.config(text=f"Voltage: {voltage:.2f}V (Deviation: {voltage_dev:+.2f}V)")
    frequency_label.config(text=f"Frequency: {frequency:.2f}Hz (Variation: {freq_var:+.2f}Hz)")
    load_label.config(text=f"Load Imbalance: {load:.2f}")

    severity_label.config(text=f"Fault Severity: {severity_score:.2f}%")
    action_label.config(text=f"Recommended Action: {action}")

    if severity_score >= 70:
        messagebox.showwarning("High Severity Detected", action)

def plot_membership_functions():
    # Plot membership functions
    voltage_deviation.view()
    frequency_variation.view()
    load_imbalance.view()
    fault_severity.view()
    plt.show()

def plot_decision_surface():
    # Plotting surface view of the fuzzy decision
    from mpl_toolkits.mplot3d import Axes3D

    # Create the grid
    x = np.arange(-20, 21, 2)
    y = np.arange(-1, 1.1, 0.2)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            fault_detector.input['Voltage Deviation'] = X[i, j]
            fault_detector.input['Frequency Variation'] = Y[i, j]
            fault_detector.input['Load Imbalance'] = 0.15  # Mid value
            fault_detector.compute()
            Z[i, j] = fault_detector.output['Fault Severity']

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis')
    ax.set_xlabel('Voltage Deviation')
    ax.set_ylabel('Frequency Variation')
    ax.set_zlabel('Fault Severity')
    plt.title('Decision Surface (Load Imbalance fixed at 0.15)')
    plt.show()

# ---- Run UI ----

def run_dashboard():
    global voltage_label, frequency_label, load_label, severity_label, action_label

    window = tk.Tk()
    window.title("Smart Grid Fuzzy Monitoring System")

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

    severity_label = tk.Label(frame, text="Fault Severity:", font=("Helvetica", 14))
    severity_label.pack()

    action_label = tk.Label(frame, text="Recommended Action:", font=("Helvetica", 14))
    action_label.pack()

    detect_button = tk.Button(frame, text="Run Detection", command=detect_and_display, bg="green", fg="white", font=("Helvetica", 14))
    detect_button.pack(pady=10)

    plot_button = tk.Button(frame, text="Plot Membership Functions", command=plot_membership_functions, bg="blue", fg="white", font=("Helvetica", 12))
    plot_button.pack(pady=5)

    surface_button = tk.Button(frame, text="Plot Decision Surface", command=plot_decision_surface, bg="purple", fg="white", font=("Helvetica", 12))
    surface_button.pack(pady=5)

    window.mainloop()

# ---- Main ----

if __name__ == "__main__":
    run_dashboard()
