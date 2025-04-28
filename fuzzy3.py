import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import random

# ---- 1. Define Fuzzy Variables ----
voltage_dev = ctrl.Antecedent(np.arange(-20, 21, 1), 'VoltageDeviation')
frequency_var = ctrl.Antecedent(np.arange(-1.0, 1.01, 0.01), 'FrequencyVariation')
load_imbalance = ctrl.Antecedent(np.arange(0, 0.31, 0.01), 'LoadImbalance')
phase_mismatch = ctrl.Antecedent(np.arange(0, 31, 1), 'PhaseMismatch')

# ---- 2. Define Consequent Variables ----
severity = ctrl.Consequent(np.arange(0, 101, 1), 'Severity')
load_balance = ctrl.Consequent(np.arange(0, 101, 1), 'LoadBalance')
pf_correction = ctrl.Consequent(np.arange(0, 101, 1), 'PFCorrection')
storage_dispatch = ctrl.Consequent(np.arange(0, 101, 1), 'StorageDispatch')

# ---- 3. Membership Functions ----n# Voltage Deviation
voltage_dev['Low']    = fuzz.trimf(voltage_dev.universe, [-20, -20, 0])
voltage_dev['Normal'] = fuzz.trimf(voltage_dev.universe, [-5, 0, 5])
voltage_dev['High']   = fuzz.trimf(voltage_dev.universe, [0, 20, 20])

# Frequency Variation
frequency_var['Stable']       = fuzz.trimf(frequency_var.universe, [-0.2, 0, 0.2])
frequency_var['UnstableLow']  = fuzz.trimf(frequency_var.universe, [-1.0, -1.0, -0.2])
frequency_var['UnstableHigh'] = fuzz.trimf(frequency_var.universe, [0.2, 1.0, 1.0])

# Load Imbalance
load_imbalance['Balanced']   = fuzz.trimf(load_imbalance.universe, [0, 0, 0.1])
load_imbalance['Moderate']   = fuzz.trimf(load_imbalance.universe, [0.05, 0.15, 0.25])
load_imbalance['Unbalanced'] = fuzz.trimf(load_imbalance.universe, [0.2, 0.3, 0.3])

# Phase Mismatch
phase_mismatch['None']     = fuzz.trimf(phase_mismatch.universe, [0, 0, 5])
phase_mismatch['Moderate'] = fuzz.trimf(phase_mismatch.universe, [3, 10, 17])
phase_mismatch['Severe']   = fuzz.trimf(phase_mismatch.universe, [15, 30, 30])

# Severity Output
severity['Low']      = fuzz.trimf(severity.universe, [0, 0, 30])
severity['Moderate'] = fuzz.trimf(severity.universe, [20, 50, 80])
severity['High']     = fuzz.trimf(severity.universe, [70, 100, 100])

# Mitigation Outputs
for out in (load_balance, pf_correction, storage_dispatch):
    out['None']     = fuzz.trimf(out.universe, [0, 0, 30])
    out['Moderate'] = fuzz.trimf(out.universe, [20, 50, 80])
    out['High']     = fuzz.trimf(out.universe, [70, 100, 100])

# ---- 4. Define Fuzzy Rules ----
rules = []
# Severity Rules
rules += [
    ctrl.Rule(voltage_dev['High'] & frequency_var['UnstableHigh'] & load_imbalance['Unbalanced'] & phase_mismatch['Severe'], severity['High']),
    ctrl.Rule(voltage_dev['Low'] & frequency_var['UnstableLow'], severity['Moderate']),
    ctrl.Rule(voltage_dev['Normal'] & frequency_var['Stable'] & load_imbalance['Balanced'] & phase_mismatch['None'], severity['Low']),
    ctrl.Rule(frequency_var['UnstableLow'] | frequency_var['UnstableHigh'], severity['Moderate']),
    ctrl.Rule(load_imbalance['Unbalanced'] | phase_mismatch['Moderate'], severity['Moderate']),
    # Fallback ensures coverage across all voltage states
    ctrl.Rule(voltage_dev['Low'] | voltage_dev['Normal'] | voltage_dev['High'], severity['Low'])
]

# Mitigation Rules: Load Balancing
rules += [
    ctrl.Rule(voltage_dev['Low'] | load_imbalance['Unbalanced'], load_balance['High']),
    ctrl.Rule(load_imbalance['Moderate'], load_balance['Moderate']),
    ctrl.Rule(voltage_dev['Normal'] & load_imbalance['Balanced'], load_balance['Moderate']),
    # Fallback for load_balance
    ctrl.Rule(voltage_dev['Low'] | voltage_dev['Normal'] | voltage_dev['High'], load_balance['None'])
]

# Mitigation Rules: Power Factor Correction
rules += [
    ctrl.Rule(phase_mismatch['Moderate'], pf_correction['Moderate']),
    ctrl.Rule(phase_mismatch['Severe'], pf_correction['High']),
    ctrl.Rule(phase_mismatch['None'], pf_correction['None'])
]

# Mitigation Rules: Storage Dispatch
rules += [
    ctrl.Rule(frequency_var['UnstableLow'] | frequency_var['UnstableHigh'], storage_dispatch['High']),
    ctrl.Rule(frequency_var['Stable'], storage_dispatch['None'])
]

# ---- 5. Build Control System ----
multi_ctrl = ctrl.ControlSystem(rules)

# ---- 6. Simulation Utils ----
def generate_anomaly_case():
    """Generate random grid scenario."""
    return (
        random.uniform(200, 250),   # voltage
        random.uniform(49.0, 51.0),  # frequency
        random.uniform(0.0, 0.3),    # load imbalance
        random.uniform(0.0, 30.0)    # phase mismatch
    )


def simulate_case(voltage, frequency, load, phase):
    """Compute fuzzy outputs for a single case."""
    vd = voltage - 230
    fv = frequency - 50
    sim = ctrl.ControlSystemSimulation(multi_ctrl)
    sim.input['VoltageDeviation']   = vd
    sim.input['FrequencyVariation'] = fv
    sim.input['LoadImbalance']      = load
    sim.input['PhaseMismatch']      = phase
    sim.compute()
    return {
        'Severity':        sim.output['Severity'],
        'LoadBalance':     sim.output['LoadBalance'],
        'PFCorrection':    sim.output['PFCorrection'],
        'StorageDispatch': sim.output['StorageDispatch']
    }


def evaluate_performance(n=500):
    """Quantify detection precision & recall over n samples."""
    tp = fp = fn = tn = 0
    for _ in range(n):
        v, f, l, p = generate_anomaly_case()
        out = simulate_case(v, f, l, p)
        true_fault = abs(v - 230) > 5 or abs(f - 50) > 0.2 or l > 0.15 or p > 5
        pred_fault = out['Severity'] > 30
        if true_fault and pred_fault: tp += 1
        if not true_fault and pred_fault: fp += 1
        if true_fault and not pred_fault: fn += 1
        if not true_fault and not pred_fault: tn += 1
    return {
        'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
        'Precision': tp/(tp+fp+1e-6), 'Recall': tp/(tp+fn+1e-6)
    }

# ---- 7. Main ----
if __name__ == "__main__":
    v, f, l, p = generate_anomaly_case()
    results = simulate_case(v, f, l, p)
    print(f"Sample Case -> V: {v:.2f}V, F: {f:.2f}Hz, Load: {l:.2f}, Phase: {p:.2f}°")
    print("Defuzzified Outputs:")
    for k, val in results.items(): print(f"  {k}: {val:.2f}%")
    metrics = evaluate_performance(500)
    print("\nPerformance Metrics (500 runs):")
    for k, val in metrics.items(): print(f"  {k}: {val:.2f}")
