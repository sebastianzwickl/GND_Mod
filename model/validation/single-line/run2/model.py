import pandas as pd
import utils
import constraints
import report
from pathlib import Path
from pyomo.environ import Suffix
import numpy as np
import pandas as pd
import pyam


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

_opt_demand = pyam.IamDataFrame("Demands.xlsx")



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
model.opt_demand = _opt_demand

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
report.write_results_to_folder(model, "CO_MD2")

shadow_high = np.empty([len(model.set_year), len(model.set_node_hp)])
for index1, year in enumerate(model.set_year):
    for index2, node in enumerate(model.set_node_hp):
        shadow_high[index1][index2] = model.dual[model.c_opt_bound_high[node, year, 1]]

df = pd.DataFrame(shadow_high).T
df.to_excel('HP_SHD_PRICES.xlsx', header=None, index=None)

shadow_mid = np.empty([len(model.set_year), len(model.set_node_mp)])
for index1, year in enumerate(model.set_year):
    for index2, node in enumerate(model.set_node_mp):
        shadow_mid[index1][index2] = model.dual[model.c_opt_bound_mid[node, year, 1]]
    
df = pd.DataFrame(shadow_mid).T
df.to_excel('MP_SHD_PRICES.xlsx', header=None, index=None)
