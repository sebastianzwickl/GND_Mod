from datetime import datetime
import os
import pandas as pd
import numpy as np
import pyomo.environ as py


def write_IAMC(output_df, model, scenario, region, variable, unit, time, values):
    if isinstance(values, list):
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            }
        )
    else:
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            },
            index=[0],
        )
    output_df = output_df.append(_df)
    return output_df


def get_values_from_model(variable, index=None):
    value = []
    # key = dict()
    if type(index) == list:
        if len(index) == 2:
            for i1 in index[0]:
                for i2 in index[1]:
                    value.append(np.around(py.value(variable[i1, i2]), 3))
                    # key[(i1, i2)] = np.around(py.value(variable[i1, i2]), 3)
        elif len(index) == 3:
            for i1 in index[0]:
                for i2 in index[1]:
                    for i3 in index[2]:
                        value.append(np.around(py.value(variable[i1, i2, i3]), 3))
                        # key[(i1, i2, i3)] = np.around(py.value(variable[i1, i2, i3]), 3)
    return value


def write_results_to_folder(model=None, scenario=None):
    time = datetime.now().strftime("%Y%m%dT%H%M")
    path = os.path.join("solution", "{}-{}".format(scenario, time))

    if not os.path.exists(path):
        os.makedirs(path)

    df_out = pd.DataFrame()
    _scenario = scenario
    _model = model.name

    _value = np.around(py.value(model.objective), 0)
    output_iamc = write_IAMC(
        df_out, _model, _scenario, "Vorarlberg", "NPV", "EUR", "2025", _value
    )

    output_iamc.to_excel(os.path.join(path, "Values.xlsx"), index=False)

    var = get_values_from_model(
        variable=model.var_gamma_tra_line, index=[model.set_year, model.set_line_tra]
    )


    """
    PRELIMINRARY DISPATCH RESULTS 
    """
    output_iamc = pd.DataFrame()
    _region = 'Lauterach'
    
    for month in model.set_time_unit:    
        demand = model.var_demand_mid[_region, 2025, month]()
        output_iamc = write_IAMC(
            output_iamc,
            _model,
            _scenario,
            _region,
            "Demand",
            "MWh",
            month,
            demand)
        
        source = model.var_source_mid[_region, 2025, month]()
        output_iamc = write_IAMC(
            output_iamc,
            _model,
            _scenario,
            _region,
            "Source",
            "MWh",
            month,
            source)
        
        var_import = model.var_import_mid[_region, 2025, month]() * model.par_total_peak_factor[month]
        output_iamc = write_IAMC(
            output_iamc,
            _model,
            _scenario,
            _region,
            "Import",
            "MWh",
            month,
            var_import)
        
        var_export = model.var_export_mid[_region, 2025, month]() * model.par_total_peak_factor[month]
        output_iamc = write_IAMC(
            output_iamc,
            _model,
            _scenario,
            _region,
            "Export",
            "MWh",
            month,
            var_export)
    
    output_iamc.to_excel(os.path.join(path, "Dispatch_Lauterach.xlsx"), index=False)
    
    
    """WRITE LINE CAPACITIES TO IAMC FORMAT"""
    df_out = pd.DataFrame()
    for tline in model.set_line_tra:
        for year in model.set_year:
            df_out = write_IAMC(df_out, _model, _scenario, tline, "Transmission|Pipeline capacity", "MW", year, py.value(model.var_gamma_tra_line[year, tline]))
    for hline in model.set_line_high:
        for year in model.set_year:
            df_out = write_IAMC(df_out, _model, _scenario, hline, "High-Pressure|Pipeline capacity", "MW", year, py.value(model.var_gamma_high_line[year, hline]))
    for mline in model.set_line_mid:
        for year in model.set_year:
            df_out = write_IAMC(df_out, _model, _scenario, mline, "Mid-Pressure|Pipeline capacity", "MW", year, py.value(model.var_gamma_mid_line[year, mline]))
    df_out.to_excel(os.path.join(path, "PipCapacity.xlsx"), index=False)


    """WRITE MAXIMUM DISPATCH CAPACITY TO IAMC FORMAT"""
    _out = pd.DataFrame()
    for tline in model.set_line_tra:
        _max = 0
        for month in model.set_time_unit:
            _val = py.value(model.var_transported_tra[tline, 2025, month])
            if np.absolute(_val) > _max:
                _max = np.absolute(_val)
        _out = write_IAMC(_out, _model, _scenario, tline, "Transmission|Pipeline capacity|Max", "MW", 2025, _max)
    
    for hline in model.set_line_high:
        _max = 0
        for month in model.set_time_unit:
            _val = py.value(model.var_transported_high[hline, 2025, month])
            if np.absolute(_val) > _max:
                _max = np.absolute(_val)
        _out = write_IAMC(_out, _model, _scenario, hline, "High-Pressure|Pipeline capacity|Max", "MW", 2025, _max)
    
    for mline in model.set_line_mid:
        _max = 0
        for month in model.set_time_unit:
            _val = py.value(model.var_transported_mid[mline, 2025, month])
            if np.absolute(_val) > _max:
                _max = np.absolute(_val)
        _out = write_IAMC(_out, _model, _scenario, mline, "Mid-Pressure|Pipeline capacity|Max", "MW", 2025, _max)
            
    _out.to_excel(os.path.join(path, "InitCapacities2025.xlsx"), index=False)            
            

            

                 

    return
