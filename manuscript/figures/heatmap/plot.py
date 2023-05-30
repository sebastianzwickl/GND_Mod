import pandas
import pyam
import matplotlib.pyplot as plt
import matplotlib.colors as c
import matplotlib


def prepare_ax(ax=None):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    return


colors = {
    0: "#edf8fb",
    1: "#bfd3e6",
    2: "#9ebcda",
    3: "#8c96c6",
    4: "#8856a7",
    5: "#810f7c",
}

cmap = c.ListedColormap([colors.get(x, 0) for x in range(0, 6, 1)])
bound = list(range(0, 6, 1))
norm = c.BoundaryNorm(bound, cmap.N)


def get_range(x):
    share = x["2050"] / x["today"]
    if share == 0:
        return 0
    elif share <= 0.25:
        return 1
    elif share <= 0.5:
        return 2
    elif share <= 0.75:
        return 3
    elif share >= 0.75:
        return 4


plt.style.use(["science"])

"""READ IN DATA"""
_init = pandas.read_excel("InitCapacities2025.xlsx")

transmission = _init.loc[_init.variable == "Transmission|Pipeline capacity|Max"]
high = _init.loc[_init.variable == "High-Pressure|Pipeline capacity|Max"]
mid = _init.loc[_init.variable == "Mid-Pressure|Pipeline capacity|Max"]

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


length_tra = len(transmission.index)
length_high = len(high.index)
length_mid = len(mid.index)

total_length = sum([length_tra, length_high, length_mid])
l1 = 0.9 * length_tra / total_length
l2 = 0.9 * length_high / total_length
l3 = 0.9 * length_mid / total_length

transmission["Share"] = transmission.apply(lambda x: get_range(x), axis=1)
high["Share"] = high.apply(lambda x: get_range(x), axis=1)
mid["Share"] = mid.apply(lambda x: get_range(x), axis=1)

fig, axes = plt.subplots(
    nrows=1, ncols=4, gridspec_kw={"width_ratios": [l1, l2, l3, 0.05]}
)

if length_tra == 1:
    axes[0].bar(
        x=0,
        height=1,
        width=0.5 / 2,
        color=[colors.get(x, 0) for x in transmission.Share],
    )
else:
    axes[0].bar(
        x=0, height=1, width=0.5, color=[colors.get(x, 0) for x in transmission.Share]
    )
axes[0].set_ylim([0, 1])
axes[0].set_xlim([-0.25, length_tra - 1 + 0.25])
prepare_ax(axes[0])
axes[0].set_title(r"\underline{CB}", fontsize=8)
for i in transmission.index:
    _string1 = transmission.loc[i]["Node 1"]
    axes[0].text(
        x=i, y=0.05, s=_string1, rotation=90, ha="center", va="bottom", fontsize=4
    )
    _string2 = transmission.loc[i]["Node 2"]
    axes[0].text(
        x=i, y=0.95, s=_string2, rotation=90, ha="center", va="top", fontsize=4
    )


axes[1].bar(
    x=range(0, length_high, 1),
    height=1,
    width=0.5,
    color=[colors.get(x, 0) for x in high.Share],
)
axes[1].set_ylim([0, 1])
axes[1].set_xlim([-0.25, length_high - 1 + 0.25])
prepare_ax(axes[1])
axes[1].set_title(r"\underline{High-Pressure}", fontsize=8)
x_val = 0
for i in high.index:
    _string1 = high.loc[i]["Node 1"]
    axes[1].text(
        x=x_val, y=0.05, s=_string1, rotation=90, ha="center", va="bottom", fontsize=4
    )
    _string2 = high.loc[i]["Node 2"]
    axes[1].text(
        x=x_val, y=0.95, s=_string2, rotation=90, ha="center", va="top", fontsize=4
    )
    x_val += 1

axes[2].bar(
    x=range(0, length_mid, 1),
    height=1,
    width=0.5,
    color=[colors.get(x, 0) for x in mid.Share],
)
axes[2].set_ylim([0, 1])
axes[2].set_xlim([-0.25, length_mid - 1 + 0.25])
prepare_ax(axes[2])
axes[2].set_title(r"\underline{Mid-Pressure}", fontsize=8)

x_val = 0
for i in mid.index:
    _string1 = mid.loc[i]["Node 1"]
    axes[2].text(
        x=x_val, y=0.05, s=_string1, rotation=90, ha="center", va="bottom", fontsize=4
    )
    _string2 = mid.loc[i]["Node 2"]
    axes[2].text(
        x=x_val, y=0.95, s=_string2, rotation=90, ha="center", va="top", fontsize=4
    )
    x_val += 1


cb = matplotlib.colorbar.ColorbarBase(
    axes[3],
    cmap=cmap,
    norm=norm,
    spacing="proportional",
    ticks=[0.5, 1.5, 2.5, 3.5, 4.5],
)

axes[3].tick_params(axis="y", which="major", pad=-6.5)
cb.ax.set_yticklabels(
    ["0\%", "1-25\%", "26-50\%", "51-75\%", "76-100\%"],
    fontsize=5,
    rotation=90,
    va="center",
)
axes[3].set_ylabel("Ratio between today's and 2050's\npipeline capacity", size=6)
axes[3].minorticks_off()
labels = ["blue", "orange"]
axes[3].tick_params(right=False)

plt.tight_layout()

fig.savefig("Heat_Bar.png", dpi=1000)
fig.savefig("Heat_Bar.eps", format="eps")



