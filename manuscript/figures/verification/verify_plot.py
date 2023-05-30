import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from matplotlib.lines import Line2D
import pyam
from matplotlib import rc


def prepare_figure_setup(axes=None):
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.spines['left'].set_visible(False)
    axes.get_xaxis().set_ticks([])
    axes.get_yaxis().set_ticks([])
    return axes

color_dem = "#BC8CF2"
color_src = "#FFCC1D"
color_ex = "#6D8299"
c_ref = "#91C483"
c_dec = "#FF6464"

if __name__ == '__main__':

    fig = plt.figure(constrained_layout=False, figsize=(8, 2.5))
    gs = fig.add_gridspec(1, 2)
    
    """UPPER LEFT"""
    demand2025 = pd.read_excel("INPUT_Demand.xlsx")
    source2025 = pd.read_excel("INPUT_Source.xlsx")
    upper_left = fig.add_subplot(gs[0, 0])
    lau = gpd.read_file("LAU_WALDVIERTEL/LAU_WALDVIERTEL.shp")
    dict_demand = dict(zip(demand2025["Node"], demand2025["Yr.-dem."] * 0.5))
    dict_demand2050 = dict(zip(demand2025["Node"], demand2025["Yr.-dem."] * 0.5 * 0.975 ** 25))
    
    
    lau.geometry.boundary.plot(ax=upper_left, linewidth=0.2, color="lightgray", zorder=0)
    lau.geometry.centroid.plot(ax=upper_left, markersize=[dict_demand.get(x, 0) for x in lau.LAU_NAME], zorder=2, color=color_dem)
    lau.loc[lau.LAU_NAME == source2025.Node.item()].centroid.plot(ax=upper_left, marker="v", markersize=100, zorder=2, color=color_src, edgecolor="black", linewidth=0.25)
    
    
    dem = Line2D([], [], color=color_dem, marker="o", linestyle="None", markersize=4, label="Supplied demand")
    src = Line2D([], [], color=color_src, marker="v", linestyle="None", markersize=5, label="Source (intcon.)", markeredgewidth=0.25, markeredgecolor="black")
    ex = Line2D([0], [0], color=color_ex, linestyle="solid", label="Existing network", linewidth=1)
    ref = Line2D([0], [0], color=c_ref, linestyle="solid", label="Refurbished seg.", linewidth=1)
    dec = Line2D([0], [0], color=c_dec, linestyle="solid", label="Decommissioned seg.", linewidth=1)
    undem = Line2D([], [], color=color_src, marker="o", linestyle="None", markersize=5, label="Unsupplied demand", markeredgewidth=0.5, markeredgecolor="black", markerfacecolor="lightgray")
    
    leg = fig.legend(
        handles=[ex, dem, src, ref, dec, undem],
        loc="lower center",
        fontsize=9.5,
        framealpha=1,
        handlelength=0.75,
        handletextpad=0.25,
        borderpad=0.5,
        columnspacing=0.75,
        edgecolor="#161616",
        frameon=True,
        ncol=6,
        bbox_to_anchor=[0.5, -0.015]
    )
    leg.get_frame().set_linewidth(0.25)
    rc('text', usetex=True)
    
    
    
    text1 = upper_left.set_title(r'$\underline{2025}$', fontsize=14)
    # text1.set_bbox(dict(facecolor='none', edgecolor="black", alpha=0.5, boxstyle="round, pad=0.25", linewidth=0.25))
    
    prepare_figure_setup(upper_left)
    
    
    existing = gpd.read_file("Existing_Pipelines/Existing_Pipelines.shp")
    existing.plot(ax=upper_left, linewidth=1, color=color_ex, zorder=1)
    
    
    
    
    
    """UPPER RIGHT"""
    dict_demand2050 = dict(zip(demand2025["Node"], demand2025["Yr.-dem."] * 0.5 * 0.975 ** 25))
    dict_unsupplied = {your_key: dict_demand2050[your_key] for your_key in ["Bad Leonfelden", "Meiseldorf", "Gars am Kamp"]}
    dict_demand2050.pop("Bad Leonfelden", "Meiseldorf")
    dict_demand2050.pop("Gars am Kamp")
    
    upper_right = fig.add_subplot(gs[0, 1])
    prepare_figure_setup(upper_right)
    lau.geometry.boundary.plot(ax=upper_right, linewidth=0.2, color="lightgray", zorder=0)
    lau.geometry.centroid.plot(ax=upper_right, markersize=[dict_demand2050.get(x, 0) for x in lau.LAU_NAME], zorder=2, color=color_dem)
    lau.geometry.centroid.plot(ax=upper_right, markersize=[dict_unsupplied.get(x, 0) for x in lau.LAU_NAME], zorder=2, color="lightgray", edgecolor="black", linewidth=0.75)
    text1 = upper_right.set_title(r'$\underline{2050}$', fontsize=14)
    # text2.set_bbox(dict(facecolor='none', edgecolor="black", alpha=0.5, boxstyle="round, pad=0.25", linewidth=0.25))
    
    
    col = {0: c_ref, 1: c_ref, 2: c_dec, 3: c_dec, 4: c_dec, 5: c_dec, 6:c_ref, 7:c_ref, 8:c_ref, 9:c_ref, 10:c_ref, 11:c_ref, 12:c_ref, 13:c_ref, 14:c_ref, 15:c_ref, 16:c_ref, 17:c_dec, 18:c_ref, 19:c_ref, 20:c_ref}
    wid = {0: 1, 1:1, 6:1, 7:1, 8:1, 9:1, 10:1, 11:1, 12:1, 13:1, 14:1, 15:1, 16:1, 18:1, 19:1, 20:1}
    

    
    existing.plot(ax=upper_right, color=[col.get(x, c_dec) for x in existing.index], zorder=1,
                  linewidth = [wid.get(x, 0.5) for x in existing.index])
    lau.loc[lau.LAU_NAME == source2025.Node.item()].centroid.plot(ax=upper_right, marker="v", markersize=100, zorder=2, color=color_src, edgecolor="black", linewidth=0.25)

     
    
    
    
    
    
    
    fig.suptitle("Verfication of the refurbishment investment and decommissioning decision", y=0.975, color="black", fontsize=16)
    fig.tight_layout()
    fig.savefig("Verify.png", dpi=500)
    fig.savefig("Verify.eps", format="eps")