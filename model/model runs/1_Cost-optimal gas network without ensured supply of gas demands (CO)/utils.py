from pathlib import Path
import geopandas as gpd
import pyomo.environ as py
import pyomo


def read_shapefile(path=None, name=None):
    """
    Parameters
    ----------
    path : String, required
        Sets the path to the shapefile. The default is None.
    name : String, required
        Name of the shapefile. The default is None.

    Returns
    -------
    _data : GeoDataFrame
        Includes the information of the shapefile input data.

    """
    _path = Path(path)
    _data = gpd.read_file(_path / name)
    return _data


def get_nodes_from_lines(transmission=None, high_pressure=None, mid_pressure=None):
    """
    Parameters
    ----------
    transmission : GeoDataFrame, required
        Includes the transmission lines. The default is None.
    high_pressure : GeoDataFrame, required
        Includes the high-pressure pipelines. The default is None.
    mid_pressure : GeoDataFrame, required
        Includes the low-pressure pipelines. The default is None.

    Returns
    -------
    network : Dict
        Includes a dictionary with compressor, network level, and delivery nodes.

    """
    nodes_tra = []
    nodes_tra = nodes_tra + list(transmission.Start) + list(transmission.End)
    nodes_tra = list(set(nodes_tra))

    nodes_high = []
    nodes_high = nodes_high + list(high_pressure.Start) + list(high_pressure.End)
    nodes_high = list(set(nodes_high))

    nodes_mid = []
    nodes_mid = nodes_mid + list(mid_pressure.Start) + list(mid_pressure.End)
    nodes_mid = list(set(nodes_mid))

    compressors = nodes_tra
    con_tra_high = [x for x in nodes_tra if x in nodes_high]
    con_high_mid = [x for x in nodes_high if x in nodes_mid]

    network = {
        "Compressor": compressors,
        "High-Pressure": nodes_high,
        "Mid-Pressure": nodes_mid,
        "Delivery (transmission_high)": con_tra_high,
        "Delivery (high_mid)": con_high_mid,
    }

    return network


def create_model():
    """
    Returns
    -------
    m : pyomo.ConcreteModel
        Includes the model instance.

    """
    m = py.ConcreteModel()
    m.name = "CANCEL"
    return m


def add_nodal_sets(model=None, nodes=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance.. The default is None.
    nodes : dictionary, required
        Includes a dictionary with compressor, network level, and delivery nodes. The default is None.

    Returns
    -------
    None.

    """
    model.set_compressor = py.Set(initialize=nodes["Compressor"])
    model.set_node_hp = py.Set(initialize=nodes["High-Pressure"])
    model.set_node_mp = py.Set(initialize=nodes["Mid-Pressure"])
    model.set_delivery_tra_hp = py.Set(initialize=nodes["Delivery (transmission_high)"])
    model.set_delivery_hp_mp = py.Set(initialize=nodes["Delivery (high_mid)"])
    _storage = list(set(model.storage["Node"]))
    model.set_storage = py.Set(initialize=_storage)
    return


def add_line_sets(model=None, data=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance. The default is None.
    data : List, required
        Includes the (pipe)line information to be added as a set. The default is None.

    Returns
    -------
    None.

    """
    for _data in data:

        _type = list(set(_data.Type))

        if _type[0] == "Transmission line":
            model.set_line_tra = py.Set(initialize=_data.index)

        if _type[0] == "High-Pressure":
            model.set_line_high = py.Set(initialize=_data.index)

        if _type[0] == "Mid-Pressure":
            model.set_line_mid = py.Set(initialize=_data.index)

    return


def add_time_horizon(model=None, year=None, temporal=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance. The default is None.
    year : integer, required
        Defines the final year of the modeling. The default is None.
    temporal : integer, required
        Defines the time steps per year. The default is None.

    Returns
    -------
    None.

    """

    model.set_year = py.Set(initialize=range(2025, year + 1, 1))
    model.set_time_unit = py.Set(initialize=range(1, temporal + 1, 1))
    return


def transmission_line_capacity_per_year(model, line, year):
    _line = model.transmission.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Transmission"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return _data.Capacity.item()
    else:
        return 0


def high_line_capacity_per_year(model, line, year):
    _line = model.high.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "High-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return _data.Capacity.item()
    else:
        return 0


def mid_line_capacity_per_year(model, line, year):
    _line = model.mid.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Mid-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return _data.Capacity.item()
    else:
        return 0


def init_nodal_demand_at_high_pressure(model, node, year, time):
    _data = model.demand
    _data = _data.loc[(_data.Node == node) & (_data.Type == "High-Pressure")]
    if _data.empty:
        return 0
    else:
        _temp = model.temporal_demand
        _case = _data["Time-res."].item()
        _temp = _temp.loc[time - 1, _data["Time-res."].item()].item()

        _type = _data["Composition"].item()
        if _type == "Typ A (Wohnen)":
            if year > 2040:
                return 0
            else:
                return (_data["Yr.-dem."].item() * _temp) - (
                    (_data["Yr.-dem."].item() * _temp) / 15
                ) * (year - 2025)
        elif _type == "Typ B2 (Wohnen und Dienstleistungen)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.15) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        elif _type == "Typ B3 (Wohnen, Industrie und Gewerbe)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.25) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        elif _type == "Typ C (Dienstleistung)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.2) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        elif _type == "Typ D (Industrie und Gewerbe)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.35) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        else:
            print("Composition of %s not defined", _type)
            return (_data["Yr.-dem."].item() * _temp) * (1) ** (year - 2025)
            

def init_nodal_demand_at_mid_pressure(model, node, year, time):
    _data = model.demand
    _data = _data.loc[(_data.Node == node) & (_data.Type == "Mid-Pressure")]
    if _data.empty:
        return 0
    else:
        _temp = model.temporal_demand
        _case = _data["Time-res."].item()
        _temp = _temp.loc[time - 1, _data["Time-res."].item()].item()

        _type = _data["Composition"].item()
        if _type == "Typ A (Wohnen)":
            if year > 2040:
                return 0
            else:
                return (_data["Yr.-dem."].item() * _temp) - (
                    (_data["Yr.-dem."].item() * _temp) / 15
                ) * (year - 2025)
        elif _type == "Typ B2 (Wohnen und Dienstleistungen)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.15) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        elif _type == "Typ B3 (Wohnen, Industrie und Gewerbe)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.25) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        elif _type == "Typ C (Dienstleistung)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.2) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        elif _type == "Typ D (Industrie und Gewerbe)":
            return (_data["Yr.-dem."].item() * _temp) - (1-0.35) * (_data["Yr.-dem."].item() * _temp) / 25 * (year - 2025)
        else:
            print("Composition of %s not defined", _type)
            return (_data["Yr.-dem."].item() * _temp) * (1) ** (year - 2025)



def init_nodal_demand_at_tra_pressure(model, node, year, time):
    _data = model.demand
    _data = _data.loc[(_data.Node == node) & (_data.Type == "Transmission")]
    if _data.empty:
        return 0
    else:
        _temp = model.temporal_demand
        _case = _data["Time-res."].item()
        _temp = _temp.loc[time - 1, _data["Time-res."].item()].item()
        return (_data["Yr.-dem."].item() * _temp) * (1) ** (year - 2025)


def init_pipeline_length_tra(model, line):
    _line = model.transmission.loc[line]
    return _line.Length.item()


def init_pipeline_length_high(model, line):
    _line = model.high.loc[line]
    return _line.Length.item()


def init_pipeline_length_mid(model, line):
    _line = model.mid.loc[line]
    return _line.Length.item()


def init_refurbishment_inv_costs_tra(model):
    _type = "Transmission"
    _data = model.refurbishment
    _costs = _data.loc[
        (_data.Type == _type) & (_data.Name == "Specific investment costs")
    ]["Costs"]
    return _costs.item()


def init_refurbishment_inv_costs_high(model):
    _type = "High-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[
        (_data.Type == _type) & (_data.Name == "Specific investment costs")
    ]["Costs"]
    return _costs.item()


def init_refurbishment_inv_costs_mid(model):
    _type = "Mid-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[
        (_data.Type == _type) & (_data.Name == "Specific investment costs")
    ]["Costs"]
    return _costs.item()


def init_tra_node_per_type(model, node, year):
    _type = "Transmission"
    _data = model.source
    _data = _data.loc[_data.Node == node]
    if _data.empty:
        return 0
    else:
        return _data.Source.item()


def init_hp_node_per_type(model, node, year):
    _type = "High-Pressure"
    _data = model.source
    _data = _data.loc[_data.Node == node]
    if _data.empty:
        return 0
    else:
        return _data.Source.item()


def init_mp_node_per_type(model, node, year):
    _type = "Mid-Pressure"
    _data = model.source
    _data = _data.loc[_data.Node == node]
    if _data.empty:
        return 0
    else:
        return _data.Source.item()


def high_line_depreciation_factor_per_year(model, line, year):
    _line = model.high.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "High-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return 0
    else:
        return 1 - (year - _end) / 50


def tra_line_depreciation_factor_per_year(model, line, year):
    _line = model.transmission.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Transmission"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return 0
    else:
        return 1 - (year - _end) / 50


def mid_line_depreciation_factor_per_year(model, line, year):
    _line = model.mid.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Mid-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return 0
    else:
        return 1 - (year - _end) / 50


def tra_line_book_value(model, line, year):
    _line = model.transmission.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Transmission"

    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _capacity = _data.Capacity.item()
    _con = _data["Yr.-con."].item()

    _data = model.pipeline_economic
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _c_inv = _data["Inv.-cost"].item()
    _amo = _data["Amort."].item()

    if year > _con + _amo:
        return 0
    else:
        return (_capacity * _c_inv) * (1 - (year - _con) / _amo)


def high_line_book_value(model, line, year):
    _line = model.high.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "High-Pressure"

    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _capacity = _data.Capacity.item()
    _con = _data["Yr.-con."].item()

    _data = model.pipeline_economic
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _c_inv = _data["Inv.-cost"].item()
    _amo = _data["Amort."].item()
    if year > _con + _amo:
        return 0
    else:
        return (_capacity * _c_inv) * (1 - (year - _con) / _amo)


def mid_line_book_value(model, line, year):
    _line = model.mid.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Mid-Pressure"

    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _capacity = _data.Capacity.item()
    _con = _data["Yr.-con."].item()

    _data = model.pipeline_economic
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _c_inv = _data["Inv.-cost"].item()
    _amo = _data["Amort."].item()

    if year > _con + _amo:
        return 0
    else:
        return (_capacity * _c_inv) * (1 - (year - _con) / _amo)


def init_fixed_costs_tra(model, line):
    _type = "Transmission"
    _data = model.refurbishment
    _costs = _data.loc[(_data.Type == _type) & (_data.Name == "Fixed costs")]["Costs"]
    return _costs.item()


def init_fixed_costs_high(model, line):
    _type = "High-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[(_data.Type == _type) & (_data.Name == "Fixed costs")]["Costs"]
    return _costs.item()


def init_fixed_costs_mid(model, line):
    _type = "Mid-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[(_data.Type == _type) & (_data.Name == "Fixed costs")]["Costs"]
    return _costs.item()


def init_year_of_inv_tra(model, line):
    _line = model.transmission.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Transmission"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    return _end


def init_year_of_inv_high(model, line):
    _line = model.high.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "High-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    return _end


def init_year_of_inv_mid(model, line):
    _line = model.mid.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Mid-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    return _end


def init_total_peak_rel_factor(model, month):
    """
    So far, a constant factor between total and peak gas demand per month is implemented.
    However, this should be updated to improve the temporal resolution of the analysis.
    In principle, this factor influences the utilization rate of a pipeline per month.
    """
    return 720


def init_gas_prices_per_year_and_month(model, year, month):
    _data = model.prices
    _val_per_year = _data.loc[_data.Year == year]["Price"].item()
    if (month == 1) or (month == 2) or (month == 3) or (month == 12) or (month == 11):
        return 1.25 * _val_per_year
    elif (month == 6) or (month == 7) or (month == 8) or (month == 9) or (month == 5):
        return 0.75 * _val_per_year
    else:
        return _val_per_year


def add_parameter_to_model(model=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance. The default is None.

    Returns
    -------
    None.

    """
    model.par_tra_capacity = py.Param(
        model.set_line_tra,
        model.set_year,
        initialize=transmission_line_capacity_per_year,
        within=py.NonNegativeReals,
        doc="Pipeline capacity at the transmission network level",
    )

    model.par_high_capacity = py.Param(
        model.set_line_high,
        model.set_year,
        initialize=high_line_capacity_per_year,
        within=py.NonNegativeReals,
        doc="Pipeline capacity at the high-pressure network level",
    )

    model.par_mid_capacity = py.Param(
        model.set_line_mid,
        model.set_year,
        initialize=mid_line_capacity_per_year,
        within=py.NonNegativeReals,
        doc="Pipeline capacity at the mid-pressure network level",
    )

    model.par_demand_high = py.Param(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        initialize=init_nodal_demand_at_high_pressure,
        within=py.NonNegativeReals,
        doc="High-pressure gas demand at node n in year y and month m",
    )

    model.par_demand_mid = py.Param(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        initialize=init_nodal_demand_at_mid_pressure,
        within=py.NonNegativeReals,
        doc="Mid-pressure gas demand at node n in year y and month m",
    )

    model.par_demand_tra = py.Param(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        initialize=init_nodal_demand_at_tra_pressure,
        within=py.NonNegativeReals,
        doc="Nodal gas demand at the transmission network level in year y and month m",
    )

    model.par_tra_length = py.Param(
        model.set_line_tra,
        initialize=init_pipeline_length_tra,
        within=py.NonNegativeReals,
        doc="Length of the tranmission pipeline",
    )

    model.par_high_length = py.Param(
        model.set_line_high,
        initialize=init_pipeline_length_high,
        within=py.NonNegativeReals,
        doc="Lenght of the high-pressure pipeline",
    )

    model.par_mid_length = py.Param(
        model.set_line_mid,
        initialize=init_pipeline_length_mid,
        within=py.NonNegativeReals,
        doc="Lenght of the mid-pressure pipeline",
    )

    model.par_ref_tra = py.Param(
        initialize=init_refurbishment_inv_costs_tra,
        within=py.NonNegativeReals,
        doc="Specific transmission pipeline refurbishment investment costs per MW and km",
    )

    model.par_ref_high = py.Param(
        initialize=init_refurbishment_inv_costs_high,
        within=py.NonNegativeReals,
        doc="Specific high-pressure pipeline refurbishment investment costs per MW and km",
    )

    model.par_ref_mid = py.Param(
        initialize=init_refurbishment_inv_costs_mid,
        within=py.NonNegativeReals,
        doc="Specific mid-pressure pipeline refurbishment investment costs per MW and km",
    )

    model.par_wacc = py.Param(initialize=0.075, doc="Weighted average cost of capital")

    model.par_source_tra = py.Param(
        model.set_compressor,
        model.set_year,
        initialize=init_tra_node_per_type,
        within=py.NonNegativeReals,
        doc="Nodal gas source at the transmission network level in year y and month m",
    )

    model.par_source_hp = py.Param(
        model.set_node_hp,
        model.set_year,
        initialize=init_hp_node_per_type,
        within=py.NonNegativeReals,
        doc="High-pressure gas source at node n in year y",
    )

    model.par_source_mp = py.Param(
        model.set_node_mp,
        model.set_year,
        initialize=init_mp_node_per_type,
        within=py.NonNegativeReals,
        doc="Mid-pressure gas source at node n in year y",
    )

    model.par_depreciation_tra = py.Param(
        model.set_line_tra,
        model.set_year,
        initialize=tra_line_depreciation_factor_per_year,
        within=py.NonNegativeReals,
        doc="Depreciation factor of a refurbished transmission pipeline investment",
    )

    model.par_depreciation_high = py.Param(
        model.set_line_high,
        model.set_year,
        initialize=high_line_depreciation_factor_per_year,
        within=py.NonNegativeReals,
        doc="Depreciation factor of a refurbished high-pressure pipeline investment",
    )

    model.par_depreciation_mid = py.Param(
        model.set_line_mid,
        model.set_year,
        initialize=mid_line_depreciation_factor_per_year,
        within=py.NonNegativeReals,
        doc="Depreciation factor of a refurbished mid-pressure pipeline investment",
    )

    model.par_book_value_tra = py.Param(
        model.set_line_tra,
        model.set_year,
        initialize=tra_line_book_value,
        within=py.NonNegativeReals,
        doc="Book value of a pipeline at the transmission network level in year y",
    )

    model.par_book_value_high = py.Param(
        model.set_line_high,
        model.set_year,
        initialize=high_line_book_value,
        within=py.NonNegativeReals,
        doc="Book value of a pipeline at the high-pressure network level in year y",
    )

    model.par_book_value_mid = py.Param(
        model.set_line_mid,
        model.set_year,
        initialize=mid_line_book_value,
        within=py.NonNegativeReals,
        doc="Book value of a pipeline at the mid-pressure network level in year y",
    )

    model.par_i = py.Param(initialize=0.025, doc="Interest rate: 2.5%")

    model.par_fixed_tra = py.Param(
        initialize=init_fixed_costs_tra,
        within=py.NonNegativeReals,
        doc="Specific fixed costs per transmission pipeline capacity",
    )

    model.par_fixed_high = py.Param(
        initialize=init_fixed_costs_high,
        within=py.NonNegativeReals,
        doc="Specific fixed costs per high-pressure pipeline capacity",
    )

    model.par_fixed_mid = py.Param(
        initialize=init_fixed_costs_mid,
        within=py.NonNegativeReals,
        doc="Specific fixed costs per mid-pressure pipeline capacity",
    )

    model.par_year_of_inv_tra = py.Param(
        model.set_line_tra,
        initialize=init_year_of_inv_tra,
        within=py.NonNegativeReals,
        doc="Planned year of refurbishment investment per transmission line",
    )

    model.par_year_of_inv_hp = py.Param(
        model.set_line_high,
        initialize=init_year_of_inv_high,
        within=py.NonNegativeReals,
        doc="Planned year of refurbishment investment per high-pressure line",
    )

    model.par_year_of_inv_mp = py.Param(
        model.set_line_mid,
        initialize=init_year_of_inv_mid,
        within=py.NonNegativeReals,
        doc="Planned year of refurbishment investment per mid-pressure line",
    )

    model.par_total_peak_factor = py.Param(
        model.set_time_unit,
        initialize=init_total_peak_rel_factor,
        within=py.NonNegativeReals,
        doc="Transforming monthly demand values to max capacity values and vice versa.",
    )

    model.par_gas_prices = py.Param(
        model.set_year,
        model.set_time_unit,
        initialize=init_gas_prices_per_year_and_month,
        within=py.NonNegativeReals,
        doc="Gas price per year and month in order to include saisonale storage into the system.",
    )

    return


def add_decision_variables(model=None):
    """


    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        The model instance that is used to add the decision variables. The default is None.

    Returns
    -------
    None.

    """

    model.var_capex = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="CAPEX: capital expenditures (per year)",
    )

    model.var_opex = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="OPEX: operational expenditures (per year)",
    )

    model.var_rev = py.Var(
        model.set_year, domain=py.NonNegativeReals, doc="REV: revenues (per year)"
    )

    model.var_pi = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of assets (per year)",
    )

    model.var_lambda_tra = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Fixed costs for transmission pipelines (per year)",
    )

    model.var_lambda_high = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Fixed costs for high-pressure pipelines (per year)",
    )

    model.var_lambda_mid = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Fixed costs for mid-pressure pipelines (per year)",
    )

    model.var_gamma_tra = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Total installed transmission pipeline capacity (per year)",
    )

    model.var_gamma_high = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Total installed high-pressure pipeline capacity (per year)",
    )

    model.var_gamma_mid = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Total installed mid-pressure pipeline capacity (per year)",
    )

    model.var_gamma_tra_line = py.Var(
        model.set_year,
        model.set_line_tra,
        domain=py.NonNegativeReals,
        doc="Transmission pipeline capacity (per year)",
    )

    model.var_gamma_high_line = py.Var(
        model.set_year,
        model.set_line_high,
        domain=py.NonNegativeReals,
        doc="High-pressure pipeline capacity (per year)",
    )

    model.var_gamma_mid_line = py.Var(
        model.set_year,
        model.set_line_mid,
        domain=py.NonNegativeReals,
        doc="Mid-pressure pipeline capacity (per year)",
    )

    model.var_gamma_tra_line_inv = py.Var(
        model.set_year,
        model.set_line_tra,
        domain=py.NonNegativeReals,
        doc="Refurbished trans. pipeline capacity (per year)",
    )

    model.var_gamma_high_line_inv = py.Var(
        model.set_year,
        model.set_line_high,
        domain=py.NonNegativeReals,
        doc="Refurbished high-pressure pipeline capacity (per year)",
    )

    model.var_gamma_mid_line_inv = py.Var(
        model.set_year,
        model.set_line_mid,
        domain=py.NonNegativeReals,
        doc="Refurbished mid-pressure pipeline capacity (per year)",
    )

    model.var_pi_tra = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of transmission pipelines (per year)",
    )

    model.var_pi_high = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of high-pressure pipelines (per year)",
    )

    model.var_pi_mid = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of mid-pressure pipelines (per year)",
    )

    model.var_pi_tra_line = py.Var(
        model.set_line_tra,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of a transmission pipeline",
    )

    model.var_pi_high_line = py.Var(
        model.set_line_high,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of a high-pressure pipeline",
    )

    model.var_pi_mid_line = py.Var(
        model.set_line_mid,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of a mid-pressure pipeline",
    )

    model.var_pi_tra_line_inv = py.Var(
        model.set_line_tra,
        domain=py.NonNegativeReals,
        doc="Book value of the transmission pipeline refurbishment investment",
    )

    model.var_pi_high_line_inv = py.Var(
        model.set_line_high,
        domain=py.NonNegativeReals,
        doc="Book value of the high-pressure pipeline refurbishment investment",
    )

    model.var_pi_mid_line_inv = py.Var(
        model.set_line_mid,
        domain=py.NonNegativeReals,
        doc="Book value of the mid-pressure pipeline refurbishment investment",
    )

    """SOURCE AT THE NODAL AND NETWORK LEVEL"""
    model.var_source_tra = py.Var(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Source of natural gas at the transmission network level at a node",
    )

    model.var_source_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Source of natural gas at the high-pressure network level at a node",
    )

    model.var_source_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Source of natural gas at the mid-pressure network level at a node",
    )

    """TRANSPORTATION AT THE PIPELINES"""
    model.var_transported_tra = py.Var(
        model.set_line_tra,
        model.set_year,
        model.set_time_unit,
        domain=py.Reals,
        doc="Gas amount transported at a transmission pipeline (per year and month)",
    )

    model.var_transported_high = py.Var(
        model.set_line_high,
        model.set_year,
        model.set_time_unit,
        domain=py.Reals,
        doc="Gas amount transported at a high-pressure pipeline (per year and month)",
    )

    model.var_transported_mid = py.Var(
        model.set_line_mid,
        model.set_year,
        model.set_time_unit,
        domain=py.Reals,
        doc="Gas amount transported at a mid-pressure pipeline (per year and month)",
    )

    """(SUPPLIED) NODAL DEMAND"""
    model.var_demand_tra = py.Var(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Gas demand at the transmission network level that is covered (per year and month)",
    )
    model.var_demand_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Gas demand at the high-pressure network level that is covered (per year and month)",
    )
    model.var_demand_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Gas demand at the mid-pressure network level that is covered (per year and month)",
    )

    """
    STORAGE INPUT/OUTPUT AND GAS STATE OF CHARGE
    - only at the high-pressure level
    """
    model.var_storage_in_out = py.Var(
        model.set_storage, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_storage_soc = py.Var(
        model.set_storage,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )

    """IMPORT & EXPORT"""
    model.var_export_tra = py.Var(
        model.set_compressor, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_export_high = py.Var(
        model.set_node_hp, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_export_mid = py.Var(
        model.set_node_mp, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_import_tra = py.Var(
        model.set_compressor, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_import_high = py.Var(
        model.set_node_hp, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_import_mid = py.Var(
        model.set_node_mp, model.set_year, model.set_time_unit, domain=py.Reals
    )

    """REVENUES"""
    model.var_revenues_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )
    model.var_revenues_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )

    """SPENDINGS FOR GAS PURCHASE"""
    model.var_gas_purchase = py.Var(model.set_year, domain=py.NonNegativeReals)

    """DELIVERY BETWEEN TRANSMISSION AND HIGH-PRESSURE NETWORK LEVEL"""
    model.var_del_tra_high = py.Var(
        model.set_delivery_tra_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )
    model.var_del_high_mid = py.Var(
        model.set_delivery_hp_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )

    return


def obj_value(model=None):
    """


    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        The model instance that is used to add the decision variables. The default is None.

    Returns
    -------
    Expression of the objective function
        SUM [ (1/(1+i)^(year-2025)) * (Capex + Opex - Revenues) ]

    """

    return sum(
        (1 / (1 + model.par_i) ** (year - 2025))
        * (
            model.var_capex[year]
            + model.var_opex[year]
            - model.var_rev[year]
            + model.var_gas_purchase[year]
        )
        for year in model.set_year
    )


def add_objective_function(model=None):
    """


    Parameters
    ----------
    model : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """

    model.objective = py.Objective(expr=obj_value, sense=py.minimize)

    return


def add_import_and_export_lines_per_node(model=None):
    """TRANSMISSION NETWORK LEVEL"""
    _data = model.transmission
    _dict = dict()
    for node in _data.Start:
        _dict[node] = list(_data.loc[_data.Start == node].index)
    model.tra_export_lines = _dict
    _dict = dict()
    for node in _data.End:
        _dict[node] = list(_data.loc[_data.End == node].index)
    model.tra_import_lines = _dict

    """HIGH-PRESSURE NETWORK LEVEL"""
    _data = model.high
    _dict = dict()
    for node in _data.Start:
        _dict[node] = list(_data.loc[_data.Start == node].index)
    model.high_export_lines = _dict
    _dict = dict()
    for node in _data.End:
        _dict[node] = list(_data.loc[_data.End == node].index)
    model.high_import_lines = _dict

    """MID-PRESSURE NETWORK LEVEL"""
    _data = model.mid
    _dict = dict()
    for node in _data.Start:
        _dict[node] = list(_data.loc[_data.Start == node].index)
    model.mid_export_lines = _dict
    _dict = dict()
    for node in _data.End:
        _dict[node] = list(_data.loc[_data.End == node].index)
    model.mid_import_lines = _dict

    return


def print_model(model=None):

    model.write("CANCEL.lp", io_options={"symbolic_solver_labels": True})

    """PRINT MODEL TO .TXT FILE"""
    _file = open("CANCEL.txt", "w", encoding="utf-8")
    model.pprint(ostream=_file, verbose=False, prefix="")
    _file.close()
    return


def set_solver_for_the_model(model=None):
    Solver = pyomo.opt.SolverFactory("gurobi")
    Solver.options["LogFile"] = str(model.name) + ".log"
    return Solver
