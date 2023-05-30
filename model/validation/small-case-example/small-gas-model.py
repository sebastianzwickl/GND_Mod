import pyomo.environ as py

model = py.ConcreteModel()
model.name = "small-gas-model"

nodes = ["N1", "N2", "N3"]
lines = ["L1", "L2"]
years = list(range(2020, 2031, 1))
time = list(range(0, 1, 1))

model.set_nodes = py.Set(initialize=nodes)
model.set_lines = py.Set(initialize=lines)
model.set_years = py.Set(initialize=years)
model.set_time = py.Set(initialize=time)

node_imp = {"N2" : ["L1", "L2"]}

node_exp = {"N1" : ["L1"],
            "N3" : ["L2"]}

model.node_exp = node_exp
model.node_imp = node_imp

def init_gamma(model, line, year):
    """Init gamma constraint."""
    if year < 2025:
        return 100
    else:
        return 0

def init_pi(model, line, year):
    val = 100 - 20 * (year - 2020)
    if val >= 0:
        return val
    else:
        return 0  

def init_f_inv(model, year):
    if year < 2025:
        return 0
    else:
        return 1 - 0.2 * (year - 2025)
    
def init_demand(model, node, year, hour):
    if year < 2025:
        return 20
    else:
        return 2

def init_source(model, node, year, hour):
    if node == "N1":
        return 100
    else:
        return 0
    
model.par_gamma_init = py.Param(model.set_lines, model.set_years, initialize=init_gamma)
model.par_pi_init = py.Param(model.set_lines, model.set_years, initialize=init_pi)
model.par_f_inv = py.Param(model.set_years, initialize=init_f_inv)
model.par_wacc = py.Param(initialize=0.01)
model.par_c_inv = py.Param(initialize=1)
model.par_q_demand = py.Param(
    model.set_nodes, model.set_years, model.set_time, initialize=init_demand)

model.par_q_source = py.Param(model.set_nodes, model.set_years, model.set_time, 
                              initialize=init_source)

"""DECISION VARIABLES"""
model.var_gamma = py.Var(model.set_lines, model.set_years, domain=py.PositiveReals)
model.var_gamma_inv = py.Var(model.set_lines, model.set_years, domain=py.PositiveReals)
model.var_pi = py.Var(model.set_lines, model.set_years, domain=py.PositiveReals)
model.var_pi_inv = py.Var(model.set_lines, model.set_years, domain=py.PositiveReals)
model.var_c = py.Var(model.set_lines, model.set_years, domain=py.PositiveReals)

model.var_source = py.Var(model.set_nodes, model.set_years, model.set_time, domain=py.PositiveReals)
model.var_demand = py.Var(model.set_nodes, model.set_years, model.set_time, domain=py.PositiveReals)
model.var_exp = py.Var(model.set_nodes, model.set_years, model.set_time)
model.var_imp = py.Var(model.set_nodes, model.set_years, model.set_time)

model.var_q = py.Var(model.set_lines, model.set_years, model.set_time)

model.var_revenues = py.Var(model.set_nodes, model.set_years, model.set_time, domain=py.PositiveReals)

"""CONSTRAINTS"""

def constraint_capacity(model, line, year):
    return model.var_gamma[line, year] == model.par_gamma_init[line, year] + model.var_gamma_inv[line, year]
model.con1 = py.Constraint(model.set_lines, model.set_years, rule=constraint_capacity)


def constraint_book_value(model, line, year):
    return model.var_pi[line, year] == model.par_pi_init[line, year] + model.par_f_inv[year] * model.var_pi_inv[line, 2025]
model.con2 = py.Constraint(model.set_lines, model.set_years, rule=constraint_book_value)


def constraint_capex(model, line, year):
    return model.var_c[line, year] == model.par_wacc * model.var_pi[line, year]
model.con3 = py.Constraint(model.set_lines, model.set_years, rule=constraint_capex)


def constraint_expansion(model, line, year):
    if year == 2025:    
        return model.var_pi_inv[line, year] == model.par_c_inv * model.var_gamma_inv[line, year]
    else:
        return py.Constraint.Skip
model.con4 = py.Constraint(model.set_lines, model.set_years, rule=constraint_expansion)


def constraint_keep(model, line, year):
    if year > 2025:
        return model.var_gamma_inv[line, year] == model.var_gamma_inv[line, year-1]
    elif year < 2025:
        return model.var_gamma_inv[line, year] == 0
    else:
        return py.Constraint.Skip
model.con5 = py.Constraint(model.set_lines, model.set_years, rule=constraint_keep)


def balance_per_node_constraint(model, node, year, time):
    return 0 == model.var_source[node, year, time] - model.var_demand[node, year, time] - model.var_exp[node, year, time] + model.var_imp[node, year, time]
model.con6 = py.Constraint(model.set_nodes, model.set_years, model.set_time, rule=balance_per_node_constraint)


def limit_source_value(model, node, year, time):
    return model.var_source[node, year, time] <= model.par_q_source[node, year, time]
model.con7 = py.Constraint(model.set_nodes, model.set_years, model.set_time, rule=limit_source_value)


def limit_demand_value(model, node, year, time):
    return model.var_demand[node, year, time] <= model.par_q_demand[node, year, time]
model.con8 = py.Constraint(model.set_nodes, model.set_years, model.set_time, rule=limit_demand_value)


def define_export_per_node(model, node, year, time):
    _value = 0
    if node in model.node_exp.keys():
        for line in model.node_exp[node]:
            _value += model.var_q[line, year, time]
        return _value == model.var_exp[node, year, time]
    else:
        return _value == model.var_exp[node, year, time]
    
model.con9 = py.Constraint(model.set_nodes, model.set_years, model.set_time, rule=define_export_per_node)


def define_import_per_node(model, node, year, time):
    _value = 0
    if node in model.node_imp.keys():
        for line in model.node_imp[node]:
            _value += model.var_q[line, year, time]
        return _value == model.var_imp[node, year, time]
    else:
        return _value == model.var_imp[node, year, time]
model.con10 = py.Constraint(model.set_nodes, model.set_years, model.set_time, rule=define_import_per_node)


def limit_max_line_capacity(model, line, year, time):
    return model.var_q[line, year, time] <= model.var_gamma[line, year]
model.con11 = py.Constraint(model.set_lines, model.set_years, model.set_time, rule=limit_max_line_capacity)


def limit_min_line_capacity(model, line, year, time):
    return -model.var_q[line, year, time] <= model.var_gamma[line, year]
model.con12 = py.Constraint(model.set_lines, model.set_years, model.set_time, rule=limit_min_line_capacity)


def calculate_revenues(model, node, year, time):
    return model.var_revenues[node, year, time] == model.var_demand[node, year, time] * 0.1
model.con13 = py.Constraint(model.set_nodes, model.set_years, model.set_time, rule=calculate_revenues)

def objective_function_minimize_costs(m):
    """Model's objective function minimizing governance's net present value."""
    _CAPEX = sum(model.var_c[line, year]
                 for line in model.set_lines
                 for year in model.set_years)
    _REVENUES = sum(model.var_revenues[node, year, time]
                    for node in model.set_nodes
                    for year in model.set_years
                    for time in model.set_time                    
        )
    return _CAPEX - _REVENUES
model.objective_function = py.Objective(expr = objective_function_minimize_costs, sense=py.minimize)

solver = py.SolverFactory("gurobi")
solution = solver.solve(model)
print("\n************************************")
print("Objective function value:", int(model.objective_function()))

result = dict()
for node in model.set_nodes:
    _values = []
    for year in model.set_years:
        _values.append(py.value(model.var_demand[node, year, 0]))
    result[node] = _values

# print('')
# print(f'N1')
# print(f'Demand: {model.var_demand["N1", 2030, 0]()}')
# print(f'Source: {model.var_source["N1", 2030, 0]()}')
# print(f'Export: {model.var_exp["N1", 2030, 0]()}')
# print(f'Import: {model.var_imp["N1", 2030, 0]()}')

# print('')
# print(f'N2')
# print(f'Demand: {model.var_demand["N2", 2030, 0]()}')
# print(f'Source: {model.var_source["N2", 2030, 0]()}')
# print(f'Export: {model.var_exp["N2", 2030, 0]()}')
# print(f'Import: {model.var_imp["N2", 2030, 0]()}')


# print('')
# print(f'N3')
# print(f'Demand: {model.var_demand["N3", 2030, 0]()}')
# print(f'Source: {model.var_source["N3", 2030, 0]()}')
# print(f'Export: {model.var_exp["N3", 2030, 0]()}')
# print(f'Import: {model.var_imp["N3", 2030, 0]()}')

# print('')
# print(f'Lines')
# print(f'L1: {model.var_q["L1", 2030, 0]()}')
# print(f'L2: {model.var_q["L2", 2030, 0]()}')




