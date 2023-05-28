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


def write_iamc_format_with_month(output_df, model, scenario, region, variable, unit, year, month, values):
    if isinstance(values, list):
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": year,
                "month": month,
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
                "year": year,
                "month": month,
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
    
    
    df_out = pd.DataFrame()
    regions = ['Nenzing', 'Bregenz', 'Schlins']
    for region in regions:
        dem_hp = model.var_demand_high[region, 2050, 1]()
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            str(region),
            'Gas|Demand|Supplied|High-Pressure',
            'MWh',
            '2050-01',
            dem_hp)
        
        dem_hp_ex = model.par_demand_high[region, 2050, 1]
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            str(region),
            'Gas|Demand|Available|High-Pressure',
            'MWh',
            '2050-01',
            dem_hp_ex)
        
        gas_imp = model.var_import_high[region, 2050, 1]() * model.par_total_peak_factor[1]
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            str(region),
            'Gas|Import|High-Pressure',
            'MWh',
            '2050-01',
            gas_imp)
        
        gas_exp = model.var_export_high[region, 2050, 1]() * model.par_total_peak_factor[1]
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            str(region),
            'Gas|Export|High-Pressure',
            'MWh',
            '2050-01',
            gas_exp)
        
        if region in model.set_delivery_hp_mp:
            gas_del_to_mid = model.var_del_high_mid[region, 2050, 1]()
            df_out = write_IAMC(
                df_out,
                _model,
                _scenario,
                str(region),
                'Gas|Deliver|High-Pressure|Mid-Pressure',
                'MWh',
                '2050-01',
                gas_del_to_mid)
        
        if region in model.set_delivery_tra_hp:
            df_out = write_IAMC(df_out,
                                _model, 
                                _scenario,
                                str(region),
                                'Gas|Deliver|Transmission|High-Pressure',
                                'MWh',
                                '2050-01',
                                model.var_del_tra_high[region, 2050, 1]()
                                )
    
    # HÖRBRANZ
    df_out = write_IAMC(df_out,
                        _model,
                        _scenario,
                        'Hörbranz',
                        'Gas|Source|Transmission',
                        'MWh',
                        '2050-01',
                        model.var_source_tra['Hörbranz', 2050, 1]()
                        )
    
    df_out = write_IAMC(df_out,
                        _model, 
                        _scenario,
                        'Hörbranz',
                        'Gas|Export|Transmission',
                        'MWh',
                        '2050-01',
                        model.var_export_tra['Hörbranz', 2050, 1]()
                        )
    
    # BLUDESCH
    df_out = write_IAMC(df_out,
                        _model,
                        _scenario,
                        'Bludesch',
                        'Gas|Import|Mid-Pressure',
                        'MWh',
                        '2050-01',
                        model.var_import_mid['Bludesch', 2050, 1]()
                        )
    
    df_out = write_IAMC(df_out,
                        _model, 
                        _scenario,
                        'Bludesch',
                        'Gas|Demand|Mid-Pressure',
                        'MWh',
                        '2050-01',
                        model.var_demand_mid['Bludesch', 2050, 1]()
                        )

    df_out.to_excel(os.path.join(path, "Dispatch.xlsx"), index=False)
            
    
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


    '''WRITE DEMAND SUPPLIED AND NOT SUPPLIED TO IAMC FORMAT'''
    df_out = pd.DataFrame()
    for year in model.set_year:
        for month in model.set_time_unit:
            for node in model.set_node_hp:
                supplied = py.value(model.var_demand_high[node, year, month])
                df_out = write_iamc_format_with_month(df_out, _model, _scenario, node, "Gas|Demand|High-Pressure|Supplied", "MWh", year, month, supplied)
                notsupplied = model.par_demand_high[node, year, month] - py.value(model.var_demand_high[node, year, month])
                df_out = write_iamc_format_with_month(df_out, _model, _scenario, node, "Gas|Demand|High-Pressure|Not Supplied", "MWh", year, month, notsupplied)
            for node in model.set_node_mp:
                supplied = py.value(model.var_demand_mid[node, year, month])
                df_out = write_iamc_format_with_month(df_out, _model, _scenario, node, "Gas|Demand|Mid-Pressure|Supplied", "MWh", year, month, supplied)
                notsupplied = model.par_demand_mid[node, year, month] - py.value(model.var_demand_mid[node, year, month])
                df_out = write_iamc_format_with_month(df_out, _model, _scenario, node, "Gas|Demand|Mid-Pressure|Not Supplied", "MWh", year, month, notsupplied)
    df_out.to_excel(os.path.join(path, "Demands.xlsx"), index=False)
    return
