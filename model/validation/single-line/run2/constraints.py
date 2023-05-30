import pyomo.environ as py


def cal_capex_per_year(model, year):
    if year != 2050:
        return model.var_capex[year] == model.var_pi[year] * model.par_wacc
    else:
        return model.var_capex[year] == model.var_pi[year]


def cal_total_fixed_costs_per_year(model, year):
    return (
        model.var_opex[year]
        == model.var_lambda_tra[year]
        + model.var_lambda_high[year]
        + model.var_lambda_mid[year]
    )


def cal_fixed_costs_tra(model, year):
    return model.var_lambda_tra[year] == model.var_gamma_tra[year] * model.par_fixed_tra


def cal_fixed_costs_high(model, year):
    return (
        model.var_lambda_high[year] == model.var_gamma_high[year] * model.par_fixed_high
    )


def cal_fixed_costs_mid(model, year):
    return model.var_lambda_mid[year] == model.var_gamma_mid[year] * model.par_fixed_mid


def cal_total_tra_capacity(model, year):
    return model.var_gamma_tra[year] == sum(
        model.var_gamma_tra_line[year, line] for line in model.set_line_tra
    )


def cal_total_high_capacity(model, year):
    return model.var_gamma_high[year] == sum(
        model.var_gamma_high_line[year, line] for line in model.set_line_high
    )


def cal_total_mid_capacity(model, year):
    return model.var_gamma_mid[year] == sum(
        model.var_gamma_mid_line[year, line] for line in model.set_line_mid
    )


def cal_cap_per_tra_line(model, year, line):
    return (
        model.var_gamma_tra_line[year, line]
        == model.par_tra_capacity[line, year] + model.var_gamma_tra_line_inv[year, line]
    )


def cal_cap_per_hp_line(model, year, line):
    return (
        model.var_gamma_high_line[year, line]
        == model.par_high_capacity[line, year]
        + model.var_gamma_high_line_inv[year, line]
    )


def cal_cap_per_mp_line(model, year, line):
    return (
        model.var_gamma_mid_line[year, line]
        == model.par_mid_capacity[line, year] + model.var_gamma_mid_line_inv[year, line]
    )


def cal_total_book_value_per_year(model, year):
    """
    SUM BOOK VALUE OF ALL PIPELINES AT THE TRANSMISSION, HIGH-PRESSURE, AND MID-PRESSURE NETWORK LEVEL.
    For each year.
    """
    return (
        model.var_pi[year]
        == model.var_pi_tra[year] + model.var_pi_high[year] + model.var_pi_mid[year]
    )


def cal_book_value_tra_per_year(model, year):
    """SUM ALL PIPELINES AT THE TRANSMISSION NETWORK LEVEL (PER YEAR)"""
    return model.var_pi_tra[year] == sum(
        model.var_pi_tra_line[line, year] for line in model.set_line_tra
    )


def cal_book_value_high_per_year(model, year):
    """SUM ALL PIPELINES AT THE HIGH-PRESSURE NETWORK LEVEL (PER YEAR)"""
    return model.var_pi_high[year] == sum(
        model.var_pi_high_line[line, year] for line in model.set_line_high
    )


def cal_book_value_mid_per_year(model, year):
    """SUM ALL PIPELINES AT THE MID-PRESSURE NETWORK LEVEL (PER YEAR)"""
    return model.var_pi_mid[year] == sum(
        model.var_pi_mid_line[line, year] for line in model.set_line_mid
    )


def cal_book_value_tra_line(model, year, line):
    """TOTAL BOOK VALUE == EXISTING + REFURBISHMENT"""
    return (
        model.var_pi_tra_line[line, year]
        == model.par_book_value_tra[line, year]
        + model.par_depreciation_tra[line, year] * model.var_pi_tra_line_inv[line]
    )


def cal_book_value_high_line(model, year, line):
    """TOTAL BOOK VALUE == EXISTING + REFURBISHMENT"""
    return (
        model.var_pi_high_line[line, year]
        == model.par_book_value_high[line, year]
        + model.par_depreciation_high[line, year] * model.var_pi_high_line_inv[line]
    )


def cal_book_value_mid_line(model, year, line):
    """TOTAL BOOK VALUE == EXISTING + REFURBISHMENT"""
    return (
        model.var_pi_mid_line[line, year]
        == model.par_book_value_mid[line, year]
        + model.par_depreciation_mid[line, year] * model.var_pi_mid_line_inv[line]
    )


def cal_investment_costs_per_tra_line(model, line):
    _inv_year = model.par_year_of_inv_tra[line]
    return (
        model.var_pi_tra_line_inv[line]
        == model.par_ref_tra
        * model.par_tra_length[line]
        * model.var_gamma_tra_line_inv[_inv_year, line]
    )


def cal_investment_costs_per_high_line(model, line):
    _inv_year = model.par_year_of_inv_hp[line]
    return (
        model.var_pi_high_line_inv[line]
        == model.par_ref_high
        * model.par_high_length[line]
        * model.var_gamma_high_line_inv[_inv_year, line]
    )


def cal_investment_costs_per_mid_line(model, line):
    _inv_year = model.par_year_of_inv_mp[line]
    return (
        model.var_pi_mid_line_inv[line]
        == model.par_ref_mid
        * model.par_mid_length[line]
        * model.var_gamma_mid_line_inv[_inv_year, line]
    )


def set_bounds_of_gamma_inv_transmission(model, line, year):
    """
    - Refurbished pipeline capacity set to 0 before year of investment
    - Constant capacity after year of investment
    """
    _inv_year = model.par_year_of_inv_tra[line]
    if year < _inv_year:
        return model.var_gamma_tra_line_inv[year, line] == 0
    elif year > _inv_year:
        return (
            model.var_gamma_tra_line_inv[year, line]
            == model.var_gamma_tra_line_inv[year - 1, line]
        )
    else:
        return py.Constraint.Skip


def set_bounds_of_gamma_inv_high(model, line, year):
    """
    - Refurbished pipeline capacity set to 0 before year of investment
    - Constant capacity after year of investment
    """
    _inv_year = model.par_year_of_inv_hp[line]
    if year < _inv_year:
        return model.var_gamma_high_line_inv[year, line] == 0
    elif year > _inv_year:
        return (
            model.var_gamma_high_line_inv[year, line]
            == model.var_gamma_high_line_inv[year - 1, line]
        )
    else:
        return py.Constraint.Skip


def set_bounds_of_gamma_inv_mid(model, line, year):
    """
    - Refurbished pipeline capacity set to 0 before year of investment
    - Constant capacity after year of investment
    """
    _inv_year = model.par_year_of_inv_mp[line]
    if year < _inv_year:
        return model.var_gamma_mid_line_inv[year, line] == 0
    elif year > _inv_year:
        return (
            model.var_gamma_mid_line_inv[year, line]
            == model.var_gamma_mid_line_inv[year - 1, line]
        )
    else:
        return py.Constraint.Skip


def export_from_transmission_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the transmission network level (compressor stations)
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.tra_export_lines.keys():
        lines = model.tra_export_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_export_tra[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_export_tra[n, y, m] == model.var_transported_tra[lines[0], y, m]
        )
    else:
        return model.var_export_tra[n, y, m] == sum(
            model.var_transported_tra[line, y, m] for line in lines
        )


def import_from_transmission_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the transmission network level (compressor stations)
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.tra_import_lines.keys():
        lines = model.tra_import_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_import_tra[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_import_tra[n, y, m] == model.var_transported_tra[lines[0], y, m]
        )
    else:
        return model.var_import_tra[n, y, m] == sum(
            model.var_transported_tra[line, y, m] for line in lines
        )


def export_from_high_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the high-pressure network level
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.high_export_lines.keys():
        lines = model.high_export_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_export_high[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_export_high[n, y, m] == model.var_transported_high[lines[0], y, m]
        )
    else:
        return model.var_export_high[n, y, m] == sum(
            model.var_transported_high[line, y, m] for line in lines
        )


def import_from_high_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the high-pressure network level
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.high_import_lines.keys():
        lines = model.high_import_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_import_high[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_import_high[n, y, m] == model.var_transported_high[lines[0], y, m]
        )
    else:
        return model.var_import_high[n, y, m] == sum(
            model.var_transported_high[line, y, m] for line in lines
        )


def export_from_mid_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the high-pressure network level
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.mid_export_lines.keys():
        lines = model.mid_export_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_export_mid[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_export_mid[n, y, m] == model.var_transported_mid[lines[0], y, m]
        )
    else:
        return model.var_export_mid[n, y, m] == sum(
            model.var_transported_mid[line, y, m] for line in lines
        )


def import_from_mid_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the high-pressure network level
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.mid_import_lines.keys():
        lines = model.mid_import_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_import_mid[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_import_mid[n, y, m] == model.var_transported_mid[lines[0], y, m]
        )
    else:
        return model.var_import_mid[n, y, m] == sum(
            model.var_transported_mid[line, y, m] for line in lines
        )


def positive_bound_per_tra_line(model, p, y, m):
    return model.var_transported_tra[p, y, m] <= model.var_gamma_tra_line[y, p]


def positive_bound_per_high_line(model, p, y, m):
    return model.var_transported_high[p, y, m] <= model.var_gamma_high_line[y, p]


def positive_bound_per_mid_line(model, p, y, m):
    return model.var_transported_mid[p, y, m] <= model.var_gamma_mid_line[y, p]


def negative_bound_per_tra_line(model, p, y, m):
    return -model.var_transported_tra[p, y, m] <= model.var_gamma_tra_line[y, p]


def negative_bound_per_high_line(model, p, y, m):
    return -model.var_transported_high[p, y, m] <= model.var_gamma_high_line[y, p]


def negative_bound_per_mid_line(model, p, y, m):
    return -model.var_transported_mid[p, y, m] <= model.var_gamma_mid_line[y, p]


def gas_balance_constraint_transmission(model, n, y, m):
    if n not in model.set_delivery_tra_hp:
        """Consequently, node n is only connected to the transmission network level"""
        return (
            model.var_source_tra[n, y, m]
            - model.var_demand_tra[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_tra[n, y, m] - model.var_import_tra[n, y, m])
            == 0
        )
    elif n in model.set_delivery_tra_hp:
        """Node n is connected to both, the transmission and high-pressure network level"""
        return (
            model.var_source_tra[n, y, m]
            - model.var_demand_tra[n, y, m]
            - model.var_del_tra_high[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_tra[n, y, m] - model.var_import_tra[n, y, m])
            == 0
        )


def gas_balance_con_high_pressure(model, n, y, m):
    if (n in model.set_delivery_tra_hp) and (n not in model.set_delivery_hp_mp):
        """Node n is only connected to the transmission and high-pressure network level. Consequently, this node does not supply mid-pressure gas demand"""
        if n in model.set_storage:
            return (
                model.var_source_high[n, y, m]
                + model.var_del_tra_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                + model.var_storage_in_out[n, y, m]
                == 0
            )
        else:
            return (
                model.var_source_high[n, y, m]
                + model.var_del_tra_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                == 0
            )

    elif (n not in model.set_delivery_tra_hp) and (n not in model.set_delivery_hp_mp):
        if n in model.set_storage:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                + model.var_storage_in_out[n, y, m]
                == 0
            )
        else:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                == 0
            )

    elif (n not in model.set_delivery_tra_hp) and (n in model.set_delivery_hp_mp):
        if n in model.set_storage:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.var_del_high_mid[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                + model.var_storage_in_out[n, y, m]
                == 0
            )
        else:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.var_del_high_mid[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                == 0
            )


def gas_balance_con_mid_pressure(model, n, y, m):
    if n not in model.set_delivery_hp_mp:
        """Node is only connected to the mid-pressure network level"""
        return (
            model.var_source_mid[n, y, m]
            - model.var_demand_mid[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_mid[n, y, m] - model.var_import_mid[n, y, m])
            == 0
        )
    else:
        return (
            model.var_source_mid[n, y, m]
            + model.var_del_high_mid[n, y, m]
            - model.var_demand_mid[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_mid[n, y, m] - model.var_import_mid[n, y, m])
            == 0
        )


"""STORAGE CONSTRAINTS"""


def gas_balance_con_storage(model, n, y, m):
    if (y == 2025) and (m == 1):
        return model.var_storage_soc[n, y, m] == model.var_storage_in_out[n, y, m]
    elif m != 1:
        return (
            model.var_storage_soc[n, y, m]
            == 0.99 * model.var_storage_soc[n, y, m - 1]
            + model.var_storage_in_out[n, y, m]
        )
    elif m == 1:
        return (
            model.var_storage_soc[n, y, m]
            == 0.99 * model.var_storage_soc[n, y - 1, 12]
            + model.var_storage_in_out[n, y, m]
        )


def state_of_charge_upper_bound(model, n, y, m):
    _data = model.storage
    return (
        model.var_storage_soc[n, y, m] <= _data.loc[_data.Node == n]["Capacity"].item()
    )


"""REVENUES CONSTRAINTS"""


def revenues_high_pressure_level(model, n, y, m):
    return model.var_revenues_high[n, y, m] == model.var_demand_high[n, y, m] * (0.5 + model.par_gas_prices[y, m])


def revenues_mid_pressure_level(model, n, y, m):
    return model.var_revenues_mid[n, y, m] == model.var_demand_mid[n, y, m] * (15 + model.par_gas_prices[y, m])


def revenues_per_year(model, y):
    _high = sum(
        model.var_revenues_high[n, y, m]
        for n in model.set_node_hp
        for m in model.set_time_unit
    )
    _mid = sum(
        model.var_revenues_mid[n, y, m]
        for n in model.set_node_mp
        for m in model.set_time_unit
    )
    return model.var_rev[y] == _high + _mid


"""DEMAND SATISFACTION CONSTRAINTS"""


def meet_tra_gas_demand(model, n, y, m):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Since no revenues are gained by supplying gas demand at the transmission network level, the corresponding (transmission)
    demand has to be covered (hard constrained).

    Returns
    -------
    pyomo.Constraint.

    """

    return model.var_demand_tra[n, y, m] == model.par_demand_tra[n, y, m]


def demand_upper_bound_high(model, n, y, m):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Since the supplied demand at the high-pressure network level results in revenues which are considered in the objective function, the covered demand needs to be limited by the demand paramater.

    Returns
    -------
    pyomo.Constraint.

    """

    return model.var_demand_high[n, y, m] <= model.par_demand_high[n, y, m]

def lower_bound_high_gas_covered(model, n, y, m):
    return model.var_demand_high[n, y, m] >= model.p_opt_high_gas[n, y, m]

def ensure_declining_gas_supply(model, n, y, m):
    if y != 2050:
        return model.var_demand_high[n, y + 1, m] <= model.var_demand_high[n, y, m]
    else:
        return py.Constraint.Skip
    
def ensure_declining_gas_supply_mid(model, n, y, m):
    if y != 2050:
        return model.var_demand_mid[n, y + 1, m] <= model.var_demand_mid[n, y, m]
    else:
        return py.Constraint.Skip


def demand_upper_bound_mid(model, n, y, m):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Since the supplied demand at the high-pressure network level results in revenues which are considered in the objective function, the covered demand needs to be limited by the demand paramater.

    Returns
    -------
    pyomo.Constraint.

    """

    return model.var_demand_mid[n, y, m] <= model.par_demand_mid[n, y, m]

def lower_bound_mid_gas_covered(model, n, y, m):
    return model.var_demand_mid[n, y, m] >= model.p_opt_mid_gas[n, y, m]


def max_annual_source_per_node_tra(model, n, y):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Returns
    -------
    pyomo.Constraint.

    """

    return (
        sum(model.var_source_tra[n, y, month] for month in model.set_time_unit)
        <= model.par_source_tra[n, y]
    )


def max_annual_source_per_node_high(model, n, y):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Returns
    -------
    pyomo.Constraint.

    """

    return (
        sum(model.var_source_high[n, y, month] for month in model.set_time_unit)
        <= model.par_source_hp[n, y]
    )


def max_annual_source_per_node_mid(model, n, y):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Returns
    -------
    pyomo.Constraint.

    """

    return (
        sum(model.var_source_mid[n, y, month] for month in model.set_time_unit)
        <= model.par_source_mp[n, y]
    )


def total_spendings_per_year(model, year):
    return model.var_gas_purchase[year] == sum(
        model.var_del_tra_high[node, year, month] * model.par_gas_prices[year, month]
        for node in model.set_delivery_tra_hp
        for month in model.set_time_unit)


def add(model=None):

    """ADD CONSTRAINTS TO MODEL INSTANCE"""
    model.con_capex = py.Constraint(
        model.set_year, rule=cal_capex_per_year, doc="Capex = WACC x Book-Value"
    )
    model.con_fixed = py.Constraint(
        model.set_year,
        rule=cal_total_fixed_costs_per_year,
        doc="Opex = Fix_Tra + Fix_High + Fix_Mid",
    )
    model.con_fixed_tra = py.Constraint(
        model.set_year, rule=cal_fixed_costs_tra, doc="Fix_Tra = c_fix x Total capacity"
    )
    model.con_fixed_high = py.Constraint(
        model.set_year,
        rule=cal_fixed_costs_high,
        doc="Fix_High = c_fix x Total capacity",
    )
    model.con_fixed_mid = py.Constraint(
        model.set_year, rule=cal_fixed_costs_mid, doc="Fix_Mid = c_fix x Total capacity"
    )

    model.con_total_tra_cap = py.Constraint(
        model.set_year,
        rule=cal_total_tra_capacity,
        doc="Calculate total transmission pipeline capacity",
    )
    model.con_total_high_cap = py.Constraint(
        model.set_year,
        rule=cal_total_high_capacity,
        doc="Calculate total high-pressure pipeline capacity",
    )
    model.con_total_mid_cap = py.Constraint(
        model.set_year,
        rule=cal_total_mid_capacity,
        doc="Calculate total mid-pressure pipeline capacity",
    )

    model.con_total_tra_cap_line = py.Constraint(
        model.set_year,
        model.set_line_tra,
        rule=cal_cap_per_tra_line,
        doc="Total pipeline capacity = Initial + Refurbished",
    )
    model.con_total_high_cap_line = py.Constraint(
        model.set_year,
        model.set_line_high,
        rule=cal_cap_per_hp_line,
        doc="Total pipeline capacity = Initial + Refurbished",
    )
    model.con_total_mid_cap_line = py.Constraint(
        model.set_year,
        model.set_line_mid,
        rule=cal_cap_per_mp_line,
        doc="Total pipeline capacity = Initial + Refurbished",
    )

    model.con_total_book_val = py.Constraint(
        model.set_year,
        rule=cal_total_book_value_per_year,
        doc="Book-Value = BV_Tra + BV_High + BV_Mid",
    )
    model.con_book_value_tra = py.Constraint(
        model.set_year,
        rule=cal_book_value_tra_per_year,
        doc="Total (Transmission) Book Value",
    )
    model.con_book_value_high = py.Constraint(
        model.set_year,
        rule=cal_book_value_high_per_year,
        doc="Total (High-Pressure) Book Value",
    )
    model.con_book_value_mid = py.Constraint(
        model.set_year,
        rule=cal_book_value_mid_per_year,
        doc="Total (Mid-Pressure) Book Value",
    )

    model.con_book_value_tra_line = py.Constraint(
        model.set_year,
        model.set_line_tra,
        rule=cal_book_value_tra_line,
        doc="Transmission: Book value of pipeline = Existing + Refurbished",
    )
    model.con_book_value_high_line = py.Constraint(
        model.set_year,
        model.set_line_high,
        rule=cal_book_value_high_line,
        doc="High-Pressure: Book value of pipeline = Existing + Refurbished",
    )
    model.con_book_value_mid_line = py.Constraint(
        model.set_year,
        model.set_line_mid,
        rule=cal_book_value_mid_line,
        doc="Mid-Pressure: Book value of pipeline = Existing + Refurbished",
    )

    model.con_inv_tra_line = py.Constraint(
        model.set_line_tra,
        rule=cal_investment_costs_per_tra_line,
        doc="Transmission: Ref. Investment = [EUR/MW/km] x Length x Capacity",
    )
    model.con_inv_high_line = py.Constraint(
        model.set_line_high,
        rule=cal_investment_costs_per_high_line,
        doc="High-Pressure: Ref. Investment = [EUR/MW/km] x Length x Capacity",
    )
    model.con_inv_mid_line = py.Constraint(
        model.set_line_mid,
        rule=cal_investment_costs_per_mid_line,
        doc="Mid-Pressure: Ref. Investment = [EUR/MW/km] x Length x Capacity",
    )

    model.con_gamma_inv_tra_bounds = py.Constraint(
        model.set_line_tra,
        model.set_year,
        rule=set_bounds_of_gamma_inv_transmission,
        doc="Transmision: Refurbished Capacity. Before investment year 0; after constant.",
    )
    model.con_gamma_inv_high_bounds = py.Constraint(
        model.set_line_high,
        model.set_year,
        rule=set_bounds_of_gamma_inv_high,
        doc="High-Pressure: Refurbished Capacity. Before investment year 0; after constant.",
    )
    model.con_gamma_inv_mid_bounds = py.Constraint(
        model.set_line_mid,
        model.set_year,
        rule=set_bounds_of_gamma_inv_mid,
        doc="Mid-Pressure: Refurbished Capacity. Before investment year 0; after constant.",
    )

    model.con_total_export_per_tra_node = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=export_from_transmission_node,
        doc="Transmission: Total export from one node (sum up all relevant pipelines).",
    )
    model.con_total_export_per_high_node = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=export_from_high_node,
        doc="High-Pressure: Total export from one node (sum up all relevant pipelines).",
    )
    model.con_total_export_per_mid_node = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=export_from_mid_node,
        doc="Mid-Pressure: Total export from one node (sum up all relevant pipelines).",
    )

    model.con_total_import_per_tra_node = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=import_from_transmission_node,
        doc="Transmission: Total import to one node (sum up all relevant pipelines).",
    )
    model.con_total_import_per_high_node = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=import_from_high_node,
        doc="High-Pressure: Total import to one node (sum up all relevant pipelines).",
    )
    model.con_total_import_per_mid_node = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=import_from_mid_node,
        doc="Mid-Pressure: Total import to one node (sum up all relevant pipelines).",
    )

    model.con_positive_capacity_bound_tra = py.Constraint(
        model.set_line_tra,
        model.set_year,
        model.set_time_unit,
        rule=positive_bound_per_tra_line,
        doc="Transmission: transported amount at one pipeline <= Pipeline capacity; Constraint 14.1; Direction 1.",
    )
    model.con_positive_capacity_bound_high = py.Constraint(
        model.set_line_high,
        model.set_year,
        model.set_time_unit,
        rule=positive_bound_per_high_line,
        doc="High-Pressure: transported amount at one pipeline <= Pipeline capacity; Constraint 14.2; Direction 1.",
    )
    model.con_positive_capacity_bound_mid = py.Constraint(
        model.set_line_mid,
        model.set_year,
        model.set_time_unit,
        rule=positive_bound_per_mid_line,
        doc="Mid-Pressure: transported amount at one pipeline <= Pipeline capacity; Constraint 14.3; Direction 1.",
    )
    model.con_negative_capacity_bound_tra = py.Constraint(
        model.set_line_tra,
        model.set_year,
        model.set_time_unit,
        rule=negative_bound_per_tra_line,
        doc="Transmission: transported amount at one pipeline <= Pipeline capacity; Constraint 15.1; Direction 2.",
    )
    model.con_negative_capacity_bound_high = py.Constraint(
        model.set_line_high,
        model.set_year,
        model.set_time_unit,
        rule=negative_bound_per_high_line,
        doc="High-Pressure: transported amount at one pipeline <= Pipeline capacity; Constraint 15.2; Direction 2.",
    )
    model.con_negative_capacity_bound_mid = py.Constraint(
        model.set_line_mid,
        model.set_year,
        model.set_time_unit,
        rule=negative_bound_per_mid_line,
        doc="Mid-Pressure: transported amount at one pipeline <= Pipeline capacity; Constraint 15.3; Direction 2.",
    )

    model.c_gas_balance_tra = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_constraint_transmission,
        doc="Transmission: Gas balance at one node; Constraint 16.1.",
    )
    model.c_gas_balance_hp = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_con_high_pressure,
        doc="High-Pressure: Gas balance at one node; Constraint 16.2.",
    )
    model.c_gas_balance_mp = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_con_mid_pressure,
        doc="Mid-Pressure: Gas balance at one node; Constraint 16.3.",
    )

    model.c_soc_upper_bound = py.Constraint(
        model.set_storage,
        model.set_year,
        model.set_time_unit,
        rule=state_of_charge_upper_bound,
        doc="High-Pressure: Max gas storage capacity at one node; Constraint 19b.",
    )
    model.c_soc_in_and_out = py.Constraint(
        model.set_storage,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_con_storage,
        doc="High-Pressure: State of charge for gas storage at one node; Constraint 19a.",
    )

    model.c_rev_high = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=revenues_high_pressure_level,
        doc="High-Pressure: Revenues = (Supplied) Demand x Factor; Constraint 20.1.",
    )
    model.c_rev_mid = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=revenues_mid_pressure_level,
        doc="Mid-Pressure: Revenues = (Supplied) Demand x Factor; Constraint 20.2.",
    )
    model.c_rev_year = py.Constraint(
        model.set_year,
        rule=revenues_per_year,
        doc="All: Revenues = Sum(Revenues) for all pressure levels; Constraint 21.",
    )
    model.c_equal_tra_demand = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=meet_tra_gas_demand,
        doc="Transmission: Gas demand must be satisfied (since no economic incentive is considered in the Obj. function.",
    )
    model.c_limit_high_demand = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=demand_upper_bound_high,
        doc="Upper limit of the high-pressure gas demand covered is set by the corresponding input parameter.",
    )
    
    model.c_decline_gas_supply = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=ensure_declining_gas_supply,
        doc="Declining gas supply at the high-pressure network level."
    )
    
    model.c_decline_gas_mid_pressure = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=ensure_declining_gas_supply_mid,
        doc='Declining gas demand that is supplied at the mid-pressure network level'
    )

    model.c_limit_mid_demand = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=demand_upper_bound_mid,
        doc="Upper limit of the mid-pressure gas demand covered is set by the corresponding input parameter.",
    )
    model.c_limit_tra_source = py.Constraint(
        model.set_compressor,
        model.set_year,
        rule=max_annual_source_per_node_tra,
        doc="Transmission: Upper limit of annual gas injected at one node.",
    )
    model.c_limit_high_source = py.Constraint(
        model.set_node_hp,
        model.set_year,
        rule=max_annual_source_per_node_high,
        doc="High-Pressure: Upper limit of annual gas injected at one node.",
    )
    model.c_limit_mid_source = py.Constraint(
        model.set_node_mp,
        model.set_year,
        rule=max_annual_source_per_node_mid,
        doc="Mid-Pressure: Upper limit of annual gas injected at one node.",
    )
    
    model.c_gas_purchase = py.Constraint(
        model.set_year,
        rule=total_spendings_per_year,
        doc="Costs for delivering gas from the transmission into the high-pressure network level.")
    
    model.c_opt_bound_high = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=lower_bound_high_gas_covered)
    
    model.c_opt_bound_mid = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=lower_bound_mid_gas_covered)
    
    return
