import pandas as pd
import utils
import constraints
import report
from pathlib import Path
from pyomo.environ import Suffix
import numpy as np


"""READ IN SHAPEFILES"""
_trans = utils.read_shapefile(path="transmission", name="transmission.shp")
_high = utils.read_shapefile(path="high", name="high.shp")
_mid = utils.read_shapefile(path="mid", name="mid.shp")


"""READ IN DATA"""
_path = Path("data")

_demand = pd.read_excel(_path / "INPUT_Demand.xlsx")
_pipeline_eco = pd.read_excel(_path / "INPUT_Pipelines_Economic.xlsx")
_pipeline_tec = pd.read_excel(_path / "INPUT_Pipelines_Technical.xlsx")
_refurbishment = pd.read_excel(_path / "INPUT_Refurbishment.xlsx")
_source = pd.read_excel(_path / "INPUT_Source.xlsx")
_storage = pd.read_excel(_path / "INPUT_Storage_Technical.xlsx")
_time_dev = pd.read_excel(_path / "INPUT_Time_Resolution.xlsx")
_prices = pd.read_excel(_path / "INPUT_Prices.xlsx")


"""NODES OF THE NETWORK"""
_nodes = utils.get_nodes_from_lines(
    transmission=_trans, high_pressure=_high, mid_pressure=_mid
)


"""PYOMO.CONCRETEMODEL()"""
model = utils.create_model()

model.transmission = _trans
model.high = _high
model.mid = _mid

utils.add_import_and_export_lines_per_node(model=model)

model.demand = _demand
model.pipeline_economic = _pipeline_eco
model.pipeline_technical = _pipeline_tec
model.refurbishment = _refurbishment
model.source = _source
model.storage = _storage
model.temporal_demand = _time_dev
model.prices = _prices

utils.add_nodal_sets(model=model, nodes=_nodes)

utils.add_line_sets(model=model, data=[_trans, _high, _mid])
utils.add_time_horizon(model=model, year=2050, temporal=12)
utils.add_parameter_to_model(model=model)
utils.add_decision_variables(model=model)

constraints.add(model=model)
utils.add_objective_function(model=model)

"""PRINT AND DISPLAY THE MODEL"""
utils.print_model(model)

model.dual = Suffix(direction=Suffix.IMPORT)

"""START TO SOLVE THE MODEL"""
Solver = utils.set_solver_for_the_model(model)
solution = Solver.solve(model, tee=True)

solution.write()
model.objective.display()

"""REPORT RESULTS IN OUTPUT FILES"""
report.write_results_to_folder(model, "CO_MD1")

# """PRINT (NODAL) GAS SHADOW PRICE FOR THE FIRST YEAR"""
# print('NODE / YEAR : VALUE')
# for node in model.set_node_hp:
#     print("{} / {} : {}".format(node, 2050, model.dual[model.c_limit_high_demand[node, 2050, 1]]))
#     print("Covered demand: {}".format(model.var_demand_high[node, 2050, 1].value))
#     print("Available demand: {}".format(model.par_demand_high[node, 2050, 1]))
    
print('SHADOW PRICE : MID-PRESSURE GAS NETWORK DEMAND')
for year in model.set_year:
    print('{} : {}' .format(year, model.dual[model.c_limit_mid_demand['Bludesch', year, 1]]))
    
print('SHADOW PRICE : HIGH-PRESSURE GAS NETWORK DEMAND')
for region in ['Bregenz', 'Nenzing']:
    for year in model.set_year:
        print('{} : {}' .format(year, model.dual[model.c_limit_high_demand[region, year, 1]]))
    