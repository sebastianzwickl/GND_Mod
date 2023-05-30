import pandas
import pyam
import matplotlib.pyplot as plt
import matplotlib.colors as c
import matplotlib
import geopandas as gpd
from pyproj import Geod
from shapely import geometry, ops
from matplotlib.lines import Line2D
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.colors as c


"""PREAMBLE AND DEFINITIONS"""

_color_pressure = {'Transmission line': '#9B0000',
                   "High-Pressure": "#9B0000",
                   "Mid-Pressure": "#A6CF98"}

plt.style.use(["science"])
plt.rcParams['xtick.labelsize'] = 6
plt.rcParams['ytick.labelsize'] = 6
plt.rcParams["figure.figsize"] = (4.5, 3)

"""FUNCTIONS"""

def create_lines_between_centroids(LAU=None, Nodes=None):
    _res_df = pandas.DataFrame(columns=["Pressure", "Geometry", "Length"])

    geod = Geod(ellps="WGS84")

    for index, row in Nodes.iterrows():
        if row['2050'] != 0:
            point1 = LAU.loc[LAU.LAU_NAME == row["Node 1"]].geometry.item().centroid
            point2 = LAU.loc[LAU.LAU_NAME == row["Node 2"]].geometry.item().centroid
            LineString = geometry.LineString([point1, point2])
            Length = geod.geometry_length(LineString) / 1000
            item = {
                "Pressure": [row["Pressure level"]],
                "Geometry": [LineString],
                "Length": [Length],
            }
            _new = pandas.DataFrame(data=item)
            _res_df = pandas.concat([_res_df, _new])

    _res_df = gpd.GeoDataFrame(_res_df, geometry=_res_df["Geometry"])
    _res_df.set_crs(epsg=4326, inplace=True)
    _res_df.reset_index(inplace=True)
    _res_df.drop(columns=["Geometry", "index"], inplace=True)

    return _res_df

# _init = pandas.read_excel("InitCapacities2025.xlsx")
# initial = _init

_init = pyam.IamDataFrame('PipCapacity.xlsx').filter(year=2025).data






fig = plt.figure(constrained_layout=True)
gs = GridSpec(6, 8, figure=fig)
ax_net = fig.add_subplot(gs[:, 0:4])
ax_cap = fig.add_subplot(gs[0:2, 5:8])
ax_supdem = fig.add_subplot(gs[2:4, 4:8])
ax_notdem = fig.add_subplot(gs[4:6, 4:8])


"""NETWORK"""
# ax_net.set_title('Gas network', fontsize=8)
districts = gpd.read_file('at_lau/at_lau.shp')
filt_districts = districts.loc[districts["GISCO_ID"].str.contains('AT_8')]
transmission = _init.loc[_init.variable == "Transmission|Pipeline capacity"]
high = _init.loc[_init.variable == "High-Pressure|Pipeline capacity"]
mid = _init.loc[_init.variable == "Mid-Pressure|Pipeline capacity"]

_init_names = pandas.read_excel("Pipelines.xlsx")
_transmission_names = _init_names.loc[
    _init_names["Pressure level"] == "Transmission line"
].reset_index()
_transmission_names.drop(columns="index", inplace=True)
_high_names = _init_names.loc[
    _init_names["Pressure level"] == "High-Pressure"
].reset_index()
_high_names.drop(columns="index", inplace=True)
_mid_names = _init_names.loc[
    _init_names["Pressure level"] == "Mid-Pressure"
].reset_index()
_mid_names.drop(columns="index", inplace=True)

transmission = pandas.merge(
    transmission, _transmission_names, left_on="region", right_index=True
)
transmission.rename(columns={"value": "today"}, inplace=True)
high = pandas.merge(high, _high_names, left_on="region", right_index=True)
high.rename(columns={"value": "today"}, inplace=True)
mid = pandas.merge(mid, _mid_names, left_on="region", right_index=True)
mid.rename(columns={"value": "today"}, inplace=True)

_cap_2050 = pyam.IamDataFrame("PipCapacity.xlsx").filter(year=2050)
_transmission2050 = _cap_2050.filter(variable="Transmission|Pipeline capacity").data
_high2050 = _cap_2050.filter(variable="High-Pressure|Pipeline capacity").data
_mid2050 = _cap_2050.filter(variable="Mid-Pressure|Pipeline capacity").data

transmission = pandas.merge(
    transmission, _transmission2050, left_on="region", right_on="region"
)
transmission.rename(columns={"value": "2050"}, inplace=True)
transmission.drop(transmission[transmission.today == 0].index, inplace=True)

high = pandas.merge(high, _high2050, left_on="region", right_on="region")
high.rename(columns={"value": "2050"}, inplace=True)
high.drop(high[high.today == 0].index, inplace=True)

mid = pandas.merge(mid, _mid2050, left_on="region", right_on="region")
mid.rename(columns={"value": "2050"}, inplace=True)
mid.drop(mid[mid.today == 0].index, inplace=True)

shape_tra = create_lines_between_centroids(filt_districts, transmission)
shape_high = create_lines_between_centroids(filt_districts, high)
shape_mid = create_lines_between_centroids(filt_districts, mid)

filt_districts.boundary.plot(ax=ax_net, color="gray", linewidth=0.05, zorder=-200)

ax_net.spines["top"].set_visible(False)
ax_net.spines["right"].set_visible(False)
ax_net.spines["bottom"].set_visible(False)
ax_net.spines["left"].set_visible(False)
ax_net.get_xaxis().set_ticks([])
ax_net.get_yaxis().set_ticks([])

shape_tra.plot(ax=ax_net, 
                color=[_color_pressure.get(x, "#116530") for x in shape_tra.Pressure],
                zorder=100)
shape_high.plot(ax=ax_net, color=[_color_pressure.get(x, "#116530") for x in shape_high.Pressure], zorder=100)
shape_mid.plot(ax=ax_net, color=[_color_pressure.get(x, "#116530") for x in shape_mid.Pressure], zorder=-100)

"""ADD LEGENDS"""
_patches = []
_line = Line2D(
    [0],
    [0],
    label="High-Pressure",
    color=_color_pressure["High-Pressure"],
    linewidth=2,
    linestyle="solid",
)
_patches.extend([_line])
_line = Line2D(
    [0],
    [0],
    label="Mid-Pressure",
    color=_color_pressure["Mid-Pressure"],
    linewidth=2,
    linestyle="solid",
)
_patches.extend([_line])

leg = ax_net.legend(
    handles=_patches,
    loc="upper center",
    fontsize=5,
    framealpha=1,
    handlelength=1,
    handletextpad=1,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="#161616",
    frameon=True,
    bbox_to_anchor=(0.5, 1.05),
    ncol=2,
)

leg.get_frame().set_linewidth(0.15)



LineString = geometry.LineString([[9.5,0], [10,0]])
geod = Geod(ellps="WGS84")
Ref_Length = geod.geometry_length(LineString) / 1000
    
scale1 = ScaleBar(
    dx=1,
    location='lower left',
    label_loc='left', scale_loc='bottom',
    label_formatter=lambda value, unit: '20km',
    height_fraction=0.005,
    length_fraction=1/Ref_Length*20,
    font_properties={'size': 6},
    pad=0)
    
ax_net.add_artist(scale1)


"""Capacity table"""
max_high = np.round(max(high['2050']), 2)
max_mid = np.round(max(mid['2050']), 2)
_add = [str(max_high), str(max_mid)]
cell_text = [_add]
len_high = np.round(sum(shape_high['Length']), 1)
len_mid = np.round(sum(shape_mid['Length']), 1)
cell_text.append([str(len_high), str(len_mid)])

share_dec_high = int((84 - len_high)/84*100)
share_dec_mid = int((97 - len_mid)/97*100) 

share_ref_high = 100 - share_dec_high
share_ref_mid = 100 - share_dec_mid

cell_text.append([str(share_dec_high), str(share_dec_mid)])
cell_text.append([str(share_ref_high), str(share_ref_mid)])


columns = ('High-Pres.', 'Mid-Pres.')
rows = ['Max. [MW]', 'Length [km]', 'Decom. [\%]', 'Refurb. [\%]']

the_table = ax_cap.table(cellText=cell_text,
                      rowLabels=rows,
                      colLabels=columns,
                      loc="center")

the_table.auto_set_font_size(False)

for k, cell in the_table._cells.items():
    if k[0] == 0 or k[1] < 0:    
        cell.set_facecolor('#F7F7F7')
        cell.set_fontsize(5)
    else:
        cell.set_text_props(weight='bold', color='black')
        cell.set_fontsize(5)
    cell.set_linewidth(0.05)

ax_cap.spines["top"].set_visible(False)
ax_cap.spines["right"].set_visible(False)
ax_cap.spines["bottom"].set_visible(False)
ax_cap.spines["left"].set_visible(False)
ax_cap.get_xaxis().set_ticks([])
ax_cap.get_yaxis().set_ticks([])

'''DEMAND SUPPLIED / NOT SUPPLIED'''
data = pyam.IamDataFrame('Demands.xlsx')
High_Supplied = data.filter(variable='Gas|Demand|High-Pressure|Supplied').aggregate_region('Gas|Demand|High-Pressure|Supplied')
High_Supplied.convert_unit(current='MWh', to='TWh', factor=1/1000000, inplace=True)
High_Aggregated = High_Supplied.data.groupby('year').agg(value_per_year = ('value', 'sum'))

High_Not_Supplied = data.filter(variable='Gas|Demand|High-Pressure|Not Supplied')
High_Not_Supplied.convert_unit(current='MWh', to='TWh', factor=1/1000000, inplace=True)
High_Aggregated_Not = High_Not_Supplied.data.groupby('year').agg(value_per_year = ('value', 'sum'))









colors = {0: "#9B0000"}
cmap = c.ListedColormap([colors.get(x, 0) for x in range(0, 1, 1)])
bound = list(range(0, 2, 1))
norm = c.BoundaryNorm(bound, cmap.N)
High_Aggregated.plot(ax=ax_supdem, title=None, legend=None, color='#9B0000', linewidth=1.5)

Mid_Supplied = data.filter(variable='Gas|Demand|Mid-Pressure|Supplied').aggregate_region('Gas|Demand|Mid-Pressure|Supplied')
Mid_Supplied.convert_unit(current='MWh', to='TWh', factor=1/1000000, inplace=True)
Mid_Aggregated = Mid_Supplied.data.groupby('year').agg(value_per_year = ('value', 'sum'))
Mid_Aggregated.plot(ax=ax_supdem, title=None, legend=None, color='#A6CF98', linewidth=1.5)

colors = {0: "#A6CF98"}
cmap = c.ListedColormap([colors.get(x, 0) for x in range(0, 1, 1)])
bound = list(range(0, 2, 1))
norm = c.BoundaryNorm(bound, cmap.N)

ax_supdem.set_ylabel('')
ax_supdem.set_xlabel('')
ax_supdem.set_title('Demand supplied [TWh]', fontsize=7)
ax_supdem.set_ylim([-0.1, 1.5])

ax_notdem.set_ylabel('')
ax_notdem.set_title('Demand not supplied [TWh]', fontsize=7)
ax_notdem.set_xlabel('')
ax_notdem.set_ylim([-0.1, 1.5])

High_Not_Supplied = data.filter(variable='Gas|Demand|High-Pressure|Not Supplied').aggregate_region('Gas|Demand|High-Pressure|Not Supplied')
Mid_Not_Supplied = data.filter(variable='Gas|Demand|Mid-Pressure|Not Supplied').aggregate_region('Gas|Demand|Mid-Pressure|Not Supplied')
High_Not_Supplied.convert_unit(current='MWh', to='TWh', factor=1/1000000, inplace=True)
Mid_Not_Supplied.convert_unit(current='MWh', to='TWh', factor=1/1000000, inplace=True)




Mid_Not_Aggregated = Mid_Not_Supplied.data.groupby('year').agg(value_per_year = ('value', 'sum'))
Mid_Not_Aggregated.plot(ax=ax_notdem, title=None, legend=None, color='#A6CF98', linewidth=1.5)







colors = {0: "#9B0000"}
cmap = c.ListedColormap([colors.get(x, 0) for x in range(0, 1, 1)])
bound = list(range(0, 2, 1))
# High_Not_Supplied.plot(ax=ax_notdem, legend=False, color='scenario', fill_between=True, title=None, cmap=cmap, linewidth=1.5)
High_Aggregated_Not.plot(ax=ax_notdem, legend=False, title=None, linewidth=1.5, color='#9B0000', linestyle='dashed', dashes=(5, 5))
colors = {0: "#A6CF98"}
cmap = c.ListedColormap([colors.get(x, 0) for x in range(0, 1, 1)])
bound = list(range(0, 2, 1))
# Mid_Not_Supplied.plot(ax=ax_notdem, legend=False, color='scenario', fill_between=True, title=None, cmap=cmap, linewidth=1.5)
ax_notdem.set_ylabel('')
ax_notdem.set_xlabel('')
ax_notdem.set_ylim([-0.025, 0.075])
ax_notdem.set_yticklabels(labels=['', '0', '', '', ''])

label = ax_notdem.xaxis.get_ticklabels()[2]
label.set_bbox(dict(facecolor='none', edgecolor='#92A9BD', pad=0.75, linewidth=0.5))
label = ax_supdem.xaxis.get_ticklabels()[2]
label.set_bbox(dict(facecolor='none', edgecolor='#92A9BD', pad=0.75, linewidth=0.5))

ax_net.text(x=0.5, y=0.0, s='(a)', transform=ax_net.transAxes, fontsize=6)
ax_cap.text(x=1.05, y=0.825, s='(b)', transform=ax_net.transAxes, fontsize=6)
ax_cap.text(x=1.05, y=0.485, s='(c)', transform=ax_net.transAxes, fontsize=6)
ax_cap.text(x=1.05, y=0.1025, s='(d)', transform=ax_net.transAxes, fontsize=6)

fig.savefig('network.png', dpi=1000)
fig.savefig('network.eps', format='eps')

