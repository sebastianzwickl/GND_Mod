"""Plotting script the net present value of the six different sceanrios."""
import pyam
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mlp
import matplotlib.ticker as tkr

plt.style.use(['science'])
plt.rcParams['xtick.labelsize'] = 5
plt.rcParams['ytick.labelsize'] = 5
plt.rc('legend', fontsize=5)

data = pyam.IamDataFrame("pre-results.xlsx")

fig = plt.figure(constrained_layout=False)
gs = fig.add_gridspec(2, 2)

cmap = plt.cm.jet  # define the colormap
# extract all colors from the .jet map
cmaplist = [cmap(i) for i in range(cmap.N)]
# force the first color entry to be grey
cmaplist[0] = (.5, .5, .5, 1.0)

_c = ["#77ACF1", "#D7E9F7", "#FFB319"]
cmap = mlp.colors.LinearSegmentedColormap.from_list(
    'Custom cmap', _c, cmap.N)

fig_left_up = fig.add_subplot(gs[0, 0])
fig_left_up.minorticks_off()
fig_left_down = fig.add_subplot(gs[1, 0])
fig_left_down.minorticks_off()
fig_right_up = fig.add_subplot(gs[0, 1])
fig_right_up.minorticks_off()
fig_right_down = fig.add_subplot(gs[1, 1])
fig_right_down.minorticks_off()

wacc_low_demand_high = data.filter(scenario="high demand, low wacc", region="Node A (src)")
wacc_low_demand_high.plot(ax=fig_left_up, title=None, color="black")
c_background = "#FF96AD"

fig_left_up.text(x=2025, y=10, s='Refurbishment invest.\n(both lines L1 \& L2)',
        rotation=0, fontsize=4, color='#000000',
        ha='center', va='center', bbox=dict(facecolor="#D3E4CD", edgecolor="#66806A", boxstyle='round,pad=1', linestyle='solid',
                                              linewidth=0.25))

fig_left_up.text(x=2022, y=18.5, s='Node A,B,C',
        rotation=0, fontsize=4, color='#000000',
        ha='center', va='center')


fig_left_up.set_xlabel("")
fig_left_up.set_ylabel("")
fig_left_up.set_ylim([0, 25])
fig_left_up.set_title(r'd=20, wacc=1\%', fontsize=6, y=0.925)

wacc_high_demand_low = data.filter(scenario="low demand, high wacc", region=["Node A (src)", "Node C (dem)"])
wacc_high_demand_low.plot(ax=fig_right_down, title=None)
fig_right_down.set_xlabel("")
fig_right_down.set_ylabel("")
fig_right_down.set_ylim([0, 25])
fig_right_down.set_title(r'd=2, wacc=10\%', fontsize=6, y=0.925)
fig_right_down.get_legend().remove()

lines = fig_right_down.get_lines()
lines[0].set_color("#396EB0")
lines[1].set_color("#C37B89")
lines[1].set_zorder(-2)
fig_right_down.text(x=2021.35, y=18.5, s='Node C',
        rotation=0, fontsize=4, color='#9F6470',
        ha='center', va='center')

fig_right_down.text(x=2027.5, y=3.25, s='Node A,B',
        rotation=0, fontsize=4, color='#396EB0',
        ha='center', va='center')

fig_right_down.text(x=2027.5, y=12.5, s='Invest.\ndespite\nlow dem.\n(L1 only)',
        rotation=0, fontsize=4, color='white',
        ha='center', va='center', bbox=dict(facecolor="#396EB0", edgecolor="#66806A", boxstyle='round,pad=1', linestyle='solid',
                                              linewidth=0.25))










wacc_high_demand_high = data.filter(scenario="high demand, high wacc", region=["Node A (src)", "Node C (dem)"])
wacc_high_demand_high.plot(ax=fig_left_down, title=None, legend=None, color="region")

lines = fig_left_down.get_lines()
lines[0].set_color("black")
lines[1].set_color("#C37B89")



fig_left_down.get_legend().remove()

fig_left_down.set_xlabel("")
fig_left_down.set_ylabel("")
fig_left_down.set_ylim([0, 25])
fig_left_down.set_title(r'd=20, wacc=10\%', fontsize=6, y=0.925)
fig_left_down.text(x=2028, y=18.5, s='Node A,B',
        rotation=0, fontsize=4, color='#000000',
        ha='center', va='center')

fig_left_down.text(x=2021.35, y=18.5, s='Node C',
        rotation=0, fontsize=4, color='#9F6470',
        ha='center', va='center')

fig_left_down.text(x=2027.5, y=10, s='No invest.\ninto L2',
        rotation=0, fontsize=4, color='black',
        ha='center', va='center', bbox=dict(facecolor="#C49BA3", edgecolor="#66806A", boxstyle='round,pad=1', linestyle='solid',
                                              linewidth=0.25))



wacc_low_demand_low = data.filter(scenario="low demand, low wacc", region="Node A (src)")
wacc_low_demand_low.plot(ax=fig_right_up, title=None, color="black")
fig_right_up.set_xlabel("")
fig_right_up.set_ylabel("")
fig_right_up.set_ylim([0, 25])
fig_right_up.set_title(r'd=2, wacc=1\%', fontsize=6, y=0.925)

fig_right_up.text(x=2027.5, y=12.5, s='Invest.\ndespite\nlow dem.\n(L1 \& L2)',
        rotation=0, fontsize=4, color='#000000',
        ha='center', va='center', bbox=dict(facecolor="#FBF46D", edgecolor="#66806A", boxstyle='round,pad=1', linestyle='solid',
                                              linewidth=0.25))

fig_right_up.text(x=2022, y=18.5, s='Node A,B,C',
        rotation=0, fontsize=4, color='#000000',
        ha='center', va='center')

fig_right_up.fill_between([2025, 2026, 2027, 2028, 2029, 2030], y1=6*[2],
                          color="#FBF46D")

fig.suptitle("Gas supply for varying demand and WACC", y=0.925, fontsize=8)


plt.tight_layout()
fig.savefig("results.eps", format="eps")
fig.savefig("results.png", dpi=900)
