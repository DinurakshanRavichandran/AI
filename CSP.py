# import the necessary libraries
import gurobipy as gp 
from gurobipy import GRB

# Define the data for the problem 
officers = ['O1', 'O2', 'O3', 'O4']
shifts = ['morning', 'evening']

# Create the model
model = gp.Model('shift_allocation')

# Decision Variables - Total shifts = 10
x = model.addVars(officers, shifts, vtype=GRB.INTEGER, name="x")

# Each officer must have at least two shifts
for officer in officers:
    model.addConstr(x[officer, 'morning'] + x[officer, 'evening'] >= 2)

# Morning and evening shifts must be 5 each 
model.addConstr(gp.quicksum(x[o, 'morning'] for o in officers) == 5)
model.addConstr(gp.quicksum(x[o, 'evening'] for o in officers) == 5)

# Preferences - Soft constraints 
penalty = {
    ('O1', 'morning'): 0, ('O1', 'evening'): 1,
    ('O2', 'morning'): 0, ('O2', 'evening'): 1,
    ('O3', 'morning'): 1, ('O3', 'evening'): 0,
    ('O4', 'morning'): 1, ('O4', 'evening'): 0
}

# Objective Function - Minimize the penalty
model.setObjective(
    gp.quicksum(x[o, s] * penalty[o, s] for o in officers for s in shifts),
    GRB.MINIMIZE
)

# Solve 
model.optimize()

# Display the results 
for o in officers:
    print(f"{o}: Morning = {x[o, 'morning'].X}, Evening = {x[o, 'evening'].X}")
print("Total Penalty:", model.ObjVal)
