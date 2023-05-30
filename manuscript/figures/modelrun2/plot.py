import pandas
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.colors as c
import matplotlib

# ZUERST GGPLOT UND DANN SCIENCE

plt.style.use('science')

"""HEATMAP"""
cmap = c.ListedColormap(['#f2f0f7', '#cbc9e2', '#9e9ac8', '#6a51a3'])
bound = list(range(0, 5, 1))
norm = c.BoundaryNorm(bound, cmap.N)


midpress = pandas.read_excel('MP_SHD_PRICES.xlsx', header=None)
mid_price = 17.5
for c in midpress.columns:
    for r in midpress.index:
        value = midpress.loc[r, c]
        rou_value = np.round(value, 5)
        ref = np.round(- mid_price / (1.025 ** c), 5)
        
        if np.absolute(rou_value - ref) < 0.001:
            # NO NETWORK EXPANSION / REDUCED (i.e., -17.5)
            midpress.loc[r, c] = 0
        
        elif rou_value == 0:
            # NETWORK EXPANSION / UNAFFECTED (i.e., 0)
            midpress.loc[r, c] = 2
        
        elif rou_value > 0:
            # NETWORK EXPANSION / INCREASED (i.e., > 0)
            midpress.loc[r, c] = 3
        
        else:
            # NETWORK EXPANSION / REDUCED (i.e., > -17.5)
            midpress.loc[r, c] = 1
            

fig, (axes, ax1) = plt.subplots(ncols=2, gridspec_kw={"width_ratios": [1, 0.05]}, figsize=(4,3))
axes.imshow(midpress, cmap=cmap)
axes.set_xlim([0, 25])

axes.axhline(y=32-9-0.5, color='#d8b365', linewidth=1.25)
axes.axhline(y=32-9+0.5, color='#d8b365', linewidth=1.25)

axes.axhline(y=32-14-0.5, color='#5ab4ac', linewidth=1.25)
axes.axhline(y=32-14+0.5, color='#5ab4ac', linewidth=1.25)

axes.set_xticks(ticks=[0, 5, 10, 15, 20, 25])
axes.set_xticklabels(labels=['', '2030', '', '2040', '', '2050'])
# label = axes.xaxis.get_ticklabels()[1]
# label.set_bbox(dict(facecolor='none', edgecolor='#E45826', pad=0.75, linewidth=0.5))
axes.set_xlabel('')
axes.set_yticklabels(labels=[])
axes.set_ylabel('LAUs')
cb = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, ticks=[0.5, 1.5, 2.5, 3.5])
cb.ax.set_yticklabels(
    ["No expan.\n(reduced)", "Expan.\n(reduced)", "Expan.\n(unaffected)", "Expan.\n(increased)"],
    fontsize=7,
    rotation=0,
    va="center")
ax1.minorticks_off()
fig.suptitle('Mid-Pressure', fontsize=12, y=0.925)
plt.tight_layout()
fig.subplots_adjust(wspace=-0.35)
fig.savefig("hm_shdprice.png", dpi=1000)
fig.savefig("hm_shdprice.eps", format="eps")



# midpress = pandas.read_excel('HP_SHD_PRICES.xlsx', header=None)
# mid_price = 0.8
# for c in midpress.columns:
#     for r in midpress.index:
#         value = midpress.loc[r, c]
#         rou_value = np.round(value, 5)
#         ref = np.round(- mid_price / (1.025 ** c), 5)
        
#         if np.absolute(rou_value - ref) < 0.001:
#             # NO NETWORK EXPANSION / REDUCED (i.e., -17.5)
#             midpress.loc[r, c] = 0
        
#         elif rou_value == 0:
#             # NETWORK EXPANSION / UNAFFECTED (i.e., 0)
#             midpress.loc[r, c] = 2
        
#         elif rou_value > 0:
#             # NETWORK EXPANSION / INCREASED (i.e., > 0)
#             midpress.loc[r, c] = 3
        
#         else:
#             # NETWORK EXPANSION / REDUCED (i.e., > -17.5)
#             midpress.loc[r, c] = 1
            

# fig, (axes, ax1) = plt.subplots(ncols=2, gridspec_kw={"width_ratios": [1, 0.05]}, figsize=(4,3))
# axes.imshow(midpress, cmap=cmap, norm=norm)
# axes.set_xlim([0, 25])
# axes.set_xticks(ticks=[0, 5, 10, 15, 20, 25])
# axes.set_xticklabels(labels=['', '2030', '', '2040', '', '2050'])
# label = axes.xaxis.get_ticklabels()[1]
# label.set_bbox(dict(facecolor='none', edgecolor='#E45826', pad=0.75, linewidth=0.5))
# axes.set_xlabel('Year')
# axes.set_yticklabels(labels=[])
# axes.set_ylabel('LAUs')
# cb = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, ticks=[0.5, 1.5, 2.5, 3.5])
# cb.ax.set_yticklabels(
#     ["No expan.\n(reduced)", "Expan.\n(reduced)", "Expan.\n(unaffected)", "Expan.\n(increased)"],
#     fontsize=7,
#     rotation=0,
#     va="center")
# ax1.minorticks_off()
# fig.suptitle('High-Pressure', fontsize=12, y=0.925)

# plt.tight_layout()
# fig.savefig("hm_shdprice1.png", dpi=1000)
# fig.savefig("hm_shdprice1.eps", format="eps")      
        
            
        















# # _color_pressure = {'Transmission line': '#9B0000',
# #                    "High-Pressure": "#9B0000",
# #                    "Mid-Pressure": "#A6CF98"}

# # plt.style.use(["science"])

# # plt.rcParams["figure.autolayout"] = True








# # highprsmean = np.mean(highpress)
# # highpresmax = np.max(highpress)
# # highpresmin = np.min(highpress)

# # midprsmean = np.mean(midpress)
# # midpresmax = np.max(midpress)
# # midpresmin = np.min(midpress)


# # fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(4,3))

# # (markers, stemlines, baseline) = ax1.stem(highprsmean)
# # plt.setp(markers, marker='D', markersize=5, markeredgecolor="#D9CE3F", markeredgewidth=0.3, color=_color_pressure["High-Pressure"])
# # plt.setp(baseline, color='gray', zorder=-100)
# # plt.setp(stemlines, linestyle='dashed', color="gray", linewidth=0.25)

# # # midpresmax.plot(ax=ax2)
# # # midpresmin.plot(ax=ax2)

# # ax1.set_title('Average shadow price [EUR/MWh]')

# # _patches = []
# # _line = Line2D(
# #     [0],
# #     [0],
# #     label="High-Pressure",
# #     color=_color_pressure["High-Pressure"],
# #     linewidth=2,
# #     linestyle="solid",
# # )

# # _patches.extend([_line])
# # leg = ax1.legend(
# #     handles=_patches,
# #     loc="lower right",
# #     fontsize=6,
# #     framealpha=1,
# #     handlelength=1,
# #     handletextpad=1,
# #     borderpad=0.5,
# #     columnspacing=1,
# #     edgecolor="#161616",
# #     frameon=True,
# #     ncol=2,
# # )

# # leg.get_frame().set_linewidth(0.15)





# # (markers, stemlines, baseline) = ax2.stem(midprsmean)
# # plt.setp(markers, marker='D', markersize=5, markeredgecolor="#0E3EDA", markeredgewidth=0.3, color=_color_pressure["Mid-Pressure"])
# # plt.setp(baseline, color='gray', zorder=-100)
# # plt.setp(stemlines, linestyle='dashed', color="gray", linewidth=0.25)

# # ax2.set_ylim([-30, 40])

# # _patches = []
# # _line = Line2D(
# #     [0],
# #     [0],
# #     label="Mid-Pressure",
# #     color=_color_pressure["Mid-Pressure"],
# #     linewidth=2,
# #     linestyle="solid",
# # )
# # _patches.extend([_line])
# # leg = ax2.legend(
# #     handles=_patches,
# #     loc="upper right",
# #     fontsize=6,
# #     framealpha=1,
# #     handlelength=1,
# #     handletextpad=1,
# #     borderpad=0.5,
# #     columnspacing=1,
# #     edgecolor="#161616",
# #     frameon=True,
# #     ncol=2,
# # )

# # leg.get_frame().set_linewidth(0.15)

# # ax2.set_xticklabels(labels=[str(x) for x in range(2020, 2055, 5)])

# # label = ax2.xaxis.get_ticklabels()[2]
# # label.set_bbox(dict(facecolor='none', edgecolor='#92A9BD', pad=0.75, linewidth=0.5))

# # label = ax2.get_xticklabels()[3]
# # box = label.set_bbox(dict(facecolor='none', edgecolor='#92A9BD', pad=0.75, linewidth=0.5, linestyle='dashed'))
# # fig.subplots_adjust(hspace=0.05)
# # fig.savefig('shdprice.png', dpi=1000)
# # fig.savefig('shdprice.eps', format='eps')

# # fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(4,3))
# # ax2.boxplot(midpress)




# # # ax2.bar(x=x_val, height=midpresmax-midpresmin, bottom=midpresmin, color='#EEEEEE', width=0.25)
# # # (markers, stemlines, baseline) = ax2.stem(midprsmean)
# # # plt.setp(markers, marker='D', markersize=2, markeredgecolor="#0E3EDA", markeredgewidth=0.3, color=_color_pressure["Mid-Pressure"])
# # # plt.setp(baseline, color='gray', zorder=-100)
# # # plt.setp(stemlines, linestyle='dashed', color="gray", linewidth=0.25)
# # # ax2.set_ylim([-30, 280])

# # # plt.setp(markers, marker='*', markersize=5, markeredgecolor="#D9CE3F", markeredgewidth=0.3, color=_color_pressure["High-Pressure"])
# # # plt.setp(baseline, color='gray', zorder=-100, visible=False)


# # # (markers, stemlines, baseline) = ax2.stem(midpresmax)
# # # plt.setp(markers, marker='D', markersize=5, markeredgecolor="#D9CE3F", markeredgewidth=0.3, color=_color_pressure["High-Pressure"])
# # # plt.setp(baseline, color='gray', zorder=-100)
# # # plt.setp(stemlines, linestyle='dashed', color="gray", linewidth=0.25)


# # fig.savefig('shdpricerange.png', dpi=1000)

