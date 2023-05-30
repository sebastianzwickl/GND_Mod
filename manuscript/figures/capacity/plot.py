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

plt.rcParams['ytick.labelsize'] = 7

def draw_brace(ax, xspan, text):
    """Draws an annotated brace on the axes."""
    xmin, xmax = xspan
    xspan = xmax - xmin
    ax_xmin, ax_xmax = ax.get_xlim()
    xax_span = ax_xmax - ax_xmin
    ymin, ymax = ax.get_ylim()
    yspan = ymax - ymin
    resolution = int(xspan/xax_span*100)*2+1 # guaranteed uneven
    beta = 300./xax_span # the higher this is, the smaller the radius

    x = np.linspace(xmin, xmax, resolution)
    x_half = x[:resolution//2+1]
    y_half_brace = (1/(1.+np.exp(-beta*(x_half-x_half[0])))
                    + 1/(1.+np.exp(-beta*(x_half-x_half[-1]))))
    y = np.concatenate((y_half_brace, y_half_brace[-2::-1]))
    y = ymin + (.05*y - .01)*yspan # adjust vertical position

    ax.autoscale(False)
    ax.plot(x, y, lw=0.75, color="black")

    ax.text((xmax+xmin)/2., ymin+.15*yspan, text, ha='center', va='bottom',
            fontsize=8, color="black",
            rotation=90,
            bbox=dict(facecolor='none', edgecolor='black', linewidth=0.,
                                 boxstyle="round,pad=0.3"))


_color_pressure = {'Transmission line': '#9B0000', "High-Pressure": "#9B0000", "Mid-Pressure": "#A6CF98"}
plt.style.use(["science"])

_cap_2050 = pyam.IamDataFrame("PipCapacity.xlsx").filter(year=2050)
high2050 = _cap_2050.filter(variable=["High-Pressure|Pipeline capacity", "Transmission|Pipeline capacity"]).data
mid2050 = _cap_2050.filter(variable="Mid-Pressure|Pipeline capacity").data

number_high = high2050.shape[0]
number_mid = mid2050.shape[0]

values_high = np.sort(high2050['value'])[::-1]
values_mid = np.sort(mid2050['value'])[::-1]

fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=False, figsize=(1.6,4))


x1 = range(0, number_high, 1)
ax1.bar(x=x1, height=values_high, color="#9B0000")
ax1.set_xlabel('{} existing pipelines' .format(number_high), fontsize=8, labelpad=0)
ax1.set_xticklabels(labels=[])
_patches = []
_line = Line2D(
    [0],
    [0],
    label='High-Pressure',
    color=_color_pressure["High-Pressure"],
    linewidth=2,
    linestyle="solid",
)
_patches.extend([_line])
leg = ax1.legend(
    handles=_patches,
    loc="upper right",
    fontsize=6,
    framealpha=1,
    handlelength=0.25,
    handletextpad=0.5,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="#161616",
    frameon=True,
    ncol=2,
)
leg.get_frame().set_linewidth(0.25)
draw_brace(ax1, (15, 16),'Decommissioning')
ax1.set_title('Pipeline capacity [MW]', fontsize=8)

x2 = range(0, number_mid, 1)
ax2.bar(x=x2, height=values_mid, color="#A6CF98")
ax2.set_xlabel('{} existing pipelines' .format(number_mid), fontsize=8, labelpad=0)
ax2.set_xticklabels(labels=[])
_patches = []
_line = Line2D(
    [0],
    [0],
    label='Mid-Pressure',
    color=_color_pressure["Mid-Pressure"],
    linewidth=2,
    linestyle="solid",
)
_patches.extend([_line])
leg = ax2.legend(
    handles=_patches,
    loc="upper right",
    fontsize=6,
    framealpha=1,
    handlelength=0.25,
    handletextpad=0.5,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="#161616",
    frameon=True,
    ncol=2,
)



leg.get_frame().set_linewidth(0.25)
draw_brace(ax2, (5, 27),'Decommissioning\n(22 out of 27)')
ax2.bar(x=x2, height=values_mid, color="#A6CF98")
ax2.set_title('Pipeline capacity [MW]', fontsize=8)








plt.tight_layout()



# """ADD LEGENDS"""
# _patches = []
# _line = Line2D(
#     [0],
#     [0],
#     label="High-Pressure",
#     color=_color_pressure["High-Pressure"],
#     linewidth=2,
#     linestyle="solid",
# )
# _patches.extend([_line])
# _line = Line2D(
#     [0],
#     [0],
#     label="Mid-Pressure",
#     color=_color_pressure["Mid-Pressure"],
#     linewidth=2,
#     linestyle="solid",
# )
# _patches.extend([_line])

# leg = ax.legend(
#     handles=_patches,
#     loc="upper center",
#     fontsize=4,
#     framealpha=1,
#     handlelength=1,
#     handletextpad=1,
#     borderpad=0.5,
#     columnspacing=1,
#     edgecolor="#161616",
#     frameon=True,
#     bbox_to_anchor=(0.5, 1.05),
#     ncol=2,
# )

# leg.get_frame().set_linewidth(0.25)

fig.savefig('capacity.png', dpi=1000)
fig.savefig('capacity.eps', format='eps')


# def plot_existing_and_represented_network(LAU=None, Existing=None, MOD_Pipelines=None):
#     _color_pressure = {"High-Pressure": "#9B0000", "Mid-Pressure": "#A6CF98"}
#     
#     _line_pressure = {"High-Pressure": 1, "Mid-Pressure": 0.75}
#     _line_existing = {"HD": 1, "MD": 0.75}





#     Existing.plot(
#         ax=ax,
#         color=[_color_existing.get(x, "#116530") for x in Existing.DRUCKSTUFE],
#         linewidth=[_line_existing.get(x, 0) for x in Existing.DRUCKSTUFE],
#         zorder=99,
#     )



#     LAU.boundary.plot(ax=ax2, color="gray", linewidth=0.05, zorder=0)
#     # LAU.centroid.plot(ax=ax2, color="gray", marker="o", zorder=2, markersize=0.2)

#     prepare_ax(ax2, "Representation in the model")
#     _high = MOD_Pipelines.loc[MOD_Pipelines.Pressure == "High-Pressure"]
#     _mid = MOD_Pipelines.loc[MOD_Pipelines.Pressure == "Mid-Pressure"]

#     _high.plot(
#         ax=ax2,
#         color=[_color_pressure.get(x, "#116530") for x in _high.Pressure],
#         linewidth=[_line_pressure.get(x, 0) for x in _high.Pressure],
#         zorder=2,
#     )

#     _mid.plot(
#         ax=ax2,
#         color=[_color_pressure.get(x, "#116530") for x in _mid.Pressure],
#         linewidth=[_line_pressure.get(x, 0) for x in _mid.Pressure],
#         zorder=1,
#     )



#     geod = Geod(ellps="WGS84")
#     _pip_ex_hp = Existing.loc[Existing.DRUCKSTUFE == "HD"]
#     _length = 0
#     for index, row in _pip_ex_hp.iterrows():
#         _length += geod.geometry_length(row.geometry) / 1000
#     _length = int(_length)

#     _pip_ex_mp = Existing.loc[Existing.DRUCKSTUFE == "MD"]
#     _length2 = 0
#     for index, row in _pip_ex_mp.iterrows():
#         _length2 += geod.geometry_length(row.geometry) / 1000
#     _length2 = int(_length2)
#     _patches = []
#     _line = Line2D(
#         [0],
#         [0],
#         label=str(_length) + "km",
#         color=_color_pressure["High-Pressure"],
#         linewidth=2,
#         linestyle="solid",
#     )
#     _patches.extend([_line])

#     _line = Line2D(
#         [0],
#         [0],
#         label=str(_length2) + "km",
#         color=_color_pressure["Mid-Pressure"],
#         linewidth=2,
#         linestyle="solid",
#     )
#     _patches.extend([_line])

#     leg = ax.legend(
#         handles=_patches,
#         loc="lower left",
#         fontsize=6,
#         framealpha=1,
#         handlelength=1,
#         handletextpad=1,
#         borderpad=0.5,
#         columnspacing=1,
#         edgecolor="#161616",
#         frameon=False,
#         bbox_to_anchor=(0, 0),
#         ncol=1,
#     )

#     high_len = int(
#         sum(MOD_Pipelines.loc[MOD_Pipelines.Pressure == "High-Pressure"]["Length"])
#     )
#     _patches = []
#     _line = Line2D(
#         [0],
#         [0],
#         label=str(high_len) + "km",
#         color=_color_pressure["High-Pressure"],
#         linewidth=2,
#         linestyle="solid",
#     )
#     _patches.extend([_line])
#     mid_len = int(
#         sum(MOD_Pipelines.loc[MOD_Pipelines.Pressure == "Mid-Pressure"]["Length"])
#     )
#     _line = Line2D(
#         [0],
#         [0],
#         label=str(mid_len) + "km",
#         color=_color_pressure["Mid-Pressure"],
#         linewidth=2,
#         linestyle="solid",
#     )
#     _patches.extend([_line])
#     leg1 = ax2.legend(
#         handles=_patches,
#         loc="lower left",
#         fontsize=6,
#         framealpha=1,
#         handlelength=1,
#         handletextpad=1,
#         borderpad=0.5,
#         columnspacing=1,
#         edgecolor="#161616",
#         frameon=False,
#         bbox_to_anchor=(0, 0),
#         ncol=1,
#     )

#     fig.suptitle(
#         "Gas network infrastructure in Vorarlberg, Austria", y=1.025, fontsize=10
#     )
#     plt.tight_layout()

#     fig.savefig("Network_AT8.png", dpi=500)
#     fig.savefig("Network_T8.eps", format="eps")

#     return











# colors = {
#     0: "#edf8fb",
#     1: "#bfd3e6",
#     2: "#9ebcda",
#     3: "#8c96c6",
#     4: "#8856a7",
#     5: "#810f7c",
# }

# cmap = c.ListedColormap([colors.get(x, 0) for x in range(0, 6, 1)])
# bound = list(range(0, 6, 1))
# norm = c.BoundaryNorm(bound, cmap.N)


# def get_range(x):
#     share = x["2050"] / x["today"]
#     if share == 0:
#         return 0
#     elif share <= 0.25:
#         return 1
#     elif share <= 0.5:
#         return 2
#     elif share <= 0.75:
#         return 3
#     elif share >= 0.75:
#         return 4





# length_tra = len(transmission.index)
# length_high = len(high.index)
# length_mid = len(mid.index)

# total_length = sum([length_tra, length_high, length_mid])
# l1 = 0.9 * length_tra / total_length
# l2 = 0.9 * length_high / total_length
# l3 = 0.9 * length_mid / total_length

# transmission["Share"] = transmission.apply(lambda x: get_range(x), axis=1)
# high["Share"] = high.apply(lambda x: get_range(x), axis=1)
# mid["Share"] = mid.apply(lambda x: get_range(x), axis=1)

# fig, axes = plt.subplots(
#     nrows=1, ncols=4, gridspec_kw={"width_ratios": [l1, l2, l3, 0.05]}
# )

# if length_tra == 1:
#     axes[0].bar(
#         x=0,
#         height=1,
#         width=0.5 / 2,
#         color=[colors.get(x, 0) for x in transmission.Share],
#     )
# else:
#     axes[0].bar(
#         x=0, height=1, width=0.5, color=[colors.get(x, 0) for x in transmission.Share]
#     )
# axes[0].set_ylim([0, 1])
# axes[0].set_xlim([-0.25, length_tra - 1 + 0.25])
# prepare_ax(axes[0])
# axes[0].set_title(r"\underline{CB}", fontsize=8)
# for i in transmission.index:
#     _string1 = transmission.loc[i]["Node 1"]
#     axes[0].text(
#         x=i, y=0.05, s=_string1, rotation=90, ha="center", va="bottom", fontsize=4
#     )
#     _string2 = transmission.loc[i]["Node 2"]
#     axes[0].text(
#         x=i, y=0.95, s=_string2, rotation=90, ha="center", va="top", fontsize=4
#     )


# axes[1].bar(
#     x=range(0, length_high, 1),
#     height=1,
#     width=0.5,
#     color=[colors.get(x, 0) for x in high.Share],
# )
# axes[1].set_ylim([0, 1])
# axes[1].set_xlim([-0.25, length_high - 1 + 0.25])
# prepare_ax(axes[1])
# axes[1].set_title(r"\underline{High-Pressure}", fontsize=8)
# x_val = 0
# for i in high.index:
#     _string1 = high.loc[i]["Node 1"]
#     axes[1].text(
#         x=x_val, y=0.05, s=_string1, rotation=90, ha="center", va="bottom", fontsize=4
#     )
#     _string2 = high.loc[i]["Node 2"]
#     axes[1].text(
#         x=x_val, y=0.95, s=_string2, rotation=90, ha="center", va="top", fontsize=4
#     )
#     x_val += 1

# axes[2].bar(
#     x=range(0, length_mid, 1),
#     height=1,
#     width=0.5,
#     color=[colors.get(x, 0) for x in mid.Share],
# )
# axes[2].set_ylim([0, 1])
# axes[2].set_xlim([-0.25, length_mid - 1 + 0.25])
# prepare_ax(axes[2])
# axes[2].set_title(r"\underline{Mid-Pressure}", fontsize=8)

# x_val = 0
# for i in mid.index:
#     _string1 = mid.loc[i]["Node 1"]
#     axes[2].text(
#         x=x_val, y=0.05, s=_string1, rotation=90, ha="center", va="bottom", fontsize=4
#     )
#     _string2 = mid.loc[i]["Node 2"]
#     axes[2].text(
#         x=x_val, y=0.95, s=_string2, rotation=90, ha="center", va="top", fontsize=4
#     )
#     x_val += 1


# cb = matplotlib.colorbar.ColorbarBase(
#     axes[3],
#     cmap=cmap,
#     norm=norm,
#     spacing="proportional",
#     ticks=[0.5, 1.5, 2.5, 3.5, 4.5],
# )

# axes[3].tick_params(axis="y", which="major", pad=-6.5)
# cb.ax.set_yticklabels(
#     ["0\%", "1-25\%", "26-50\%", "51-75\%", "76-100\%"],
#     fontsize=5,
#     rotation=90,
#     va="center",
# )
# axes[3].set_ylabel("Ratio between today's and 2050's\npipeline capacity", size=6)
# axes[3].minorticks_off()
# labels = ["blue", "orange"]
# axes[3].tick_params(right=False)

# plt.tight_layout()

# fig.savefig("Heat_Bar.png", dpi=1000)
# fig.savefig("Heat_Bar.eps", format="eps")
