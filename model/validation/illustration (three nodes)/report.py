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

    # """
    # PRELIMINRARY DISPATCH RESULTS
    # - region : Großgöttfritz
    # """

    # demand = model.var_demand_tra["Großgöttfritz", 2050, 1]()
    # output_iamc = write_IAMC(
    #     df_out,
    #     _model,
    #     _scenario,
    #     "Großgöttfritz",
    #     "Gas demand|Transmission",
    #     "MWh",
    #     "2050-01",
    #     demand,
    # )
    # delivered = model.var_del_tra_high["Großgöttfritz", 2050, 1]()
    # output_iamc = write_IAMC(
    #     output_iamc,
    #     _model,
    #     _scenario,
    #     "Großgöttfritz",
    #     "Gas delivered|Transmission|High-Pressure",
    #     "MWh",
    #     "2050-01",
    #     delivered,
    # )
    # amount_export = (
    #     model.var_export_tra["Großgöttfritz", 2050, 1]()
    #     * model.par_total_peak_factor[1]
    # )
    # output_iamc = write_IAMC(
    #     output_iamc,
    #     _model,
    #     _scenario,
    #     "Großgöttfritz",
    #     "Gas export|Transmission",
    #     "MWh",
    #     "2050-01",
    #     amount_export,
    # )
    # amount_import = (
    #     model.var_import_tra["Großgöttfritz", 2050, 1]()
    #     * model.par_total_peak_factor[1]
    # )
    # output_iamc = write_IAMC(
    #     output_iamc,
    #     _model,
    #     _scenario,
    #     "Großgöttfritz",
    #     "Gas import|Transmission",
    #     "MWh",
    #     "2050-01",
    #     amount_import,
    # )
    # demand_high = model.var_demand_high["Großgöttfritz", 2050, 1]()
    # output_iamc = write_IAMC(
    #     output_iamc,
    #     _model,
    #     _scenario,
    #     "Großgöttfritz",
    #     "Gas demand|High-Pressure",
    #     "MWh",
    #     "2050-01",
    #     demand_high,
    # )
    # amount_export_high = (
    #     model.var_export_high["Großgöttfritz", 2050, 1]()
    #     * model.par_total_peak_factor[1]
    # )
    # output_iamc = write_IAMC(
    #     output_iamc,
    #     _model,
    #     _scenario,
    #     "Großgöttfritz",
    #     "Gas export|High-Pressure",
    #     "MWh",
    #     "2050-01",
    #     amount_export_high,
    # )
    # amount_import_high = (
    #     model.var_import_high["Großgöttfritz", 2050, 1]()
    #     * model.par_total_peak_factor[1]
    # )
    # output_iamc = write_IAMC(
    #     output_iamc,
    #     _model,
    #     _scenario,
    #     "Großgöttfritz",
    #     "Gas import|High-Pressure",
    #     "MWh",
    #     "2050-01",
    #     amount_import_high,
    # )
    # output_iamc.to_excel(os.path.join(path, "Dispatch.xlsx"), index=False)
    
    
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

    return
