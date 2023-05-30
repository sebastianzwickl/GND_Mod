"""Plotting script the net present value of the six different sceanrios."""
import pyam
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mlp
import matplotlib.ticker as tkr
from matplotlib.colors import ListedColormap, LinearSegmentedColormap


cmap = ListedColormap(["#B7CADB", "#beaed4", "#fdc086"])


plt.style.use(['science'])
plt.rcParams['xtick.labelsize'] = 5
plt.rcParams['ytick.labelsize'] = 5
plt.rc('legend', fontsize=5)

fig = plt.figure(constrained_layout=False)
gs = fig.add_gridspec(2, 3)

fig, ax = plt.subplots(
    nrows=2, ncols=2, gridspec_kw={"width_ratios": [1, 1.75]}
)

fig11 = ax[0, 0]
fig12 = ax[0, 1]
fig13 = ax[1, 0]
fig22 = ax[1, 1]

# fig11 = fig.add_subplot(gs[0, 0])
fig11.minorticks_off()
data = pyam.IamDataFrame("(a).xlsx")
data.plot.bar(ax=fig11, title=None, legend=None, cmap=cmap, x='scenario', edgecolor='black', linewidth=0.1)
fig11.set_xlabel('')
fig11.set_ylabel('')
fig11.set_ylim([0, 150])
fig11.text(x=0, y=50, s='100\%', va='center', ha='center', fontsize=4, rotation=90)
fig11.text(x=1, y=50, s='101\%', va='center', ha='center', fontsize=4, rotation=90)
fig11.text(x=2, y=50, s='125\%', va='center', ha='center', fontsize=4, rotation=90)
fig11.set_yticks(ticks=[0, 50, 100, 150])
fig11.set_title('Total costs in \%', fontsize=5)
fig11.set_xticklabels(labels=['CO', 'CO-L', 'ES'], rotation=0)

# fig12 = fig.add_subplot(gs[0, 1:3])
fig12.minorticks_off()
labels = ['CO', 'CO-L', 'ES']
high = [100, 100-23, 100]
mid = [100-41, 100-45, 100-28]
x = np.arange(len(labels))
width = 0.35
rects1 = fig12.barh(x - width/2, high, width, label='High/Ref.', color="#ECB390")
rects2 = fig12.barh(x + width/2, mid, width, label='Mid/Ref.', color='#C3E5AE')
fig12.set_title('Decommissioned / Refurbished in \%', fontsize=5)
fig12.set_yticks(ticks=[0,1,2])
fig12.set_yticklabels(labels=['CO', 'CO-L', 'ES'], rotation=0)
fig12.set_xlim([0, 100])

high_dec = [0, 23, 0]
mid_dec = [41, 45, 28]

rects1 = fig12.barh(x - width/2, high_dec, width, left=high, label='High/Decom.', color="#9B0000", edgecolor='black', linewidth=0.25)
rects2 = fig12.barh(x + width/2, mid_dec, width, left=mid, label='Mid/Decom.', color='#6ECB63', edgecolor='black', linewidth=0.25)

fig12.legend(fontsize=4, frameon=True)

fig12.text(x=100-41/2, y=width/2, s='41\%', va='center', ha='center', fontsize=4, rotation=0)
fig12.text(x=100-45/2, y=1+width/2, s='45\%', va='center', ha='center', fontsize=4, rotation=0)
fig12.text(x=100-23/2, y=1-width/2, s='23\%', va='center', ha='center', fontsize=4, rotation=0)
fig12.text(x=100-28/2, y=2+width/2, s='28\%', va='center', ha='center', fontsize=4, rotation=0)

cmap = ListedColormap(["#B7CADB", "#beaed4", "#fdc086"])
# fig13 = fig.add_subplot(gs[1, 0])
fig13.minorticks_off()
data = pyam.IamDataFrame("(b).xlsx")
data.plot.bar(ax=fig13, title=None, legend=None, cmap=cmap, x='scenario', edgecolor='black', linewidth=0.1)
fig13.set_xlabel('')
fig13.set_ylabel('')
fig13.set_ylim([0, 1200])
x = [0, 1, 2]
y = [1058, 1058, 1058]
fig13.plot(x, y, linestyle='solid', color='black')
fig13.set_title('Max. capacity in MW', fontsize=5)
fig13.text(x=0, y=162+50, s='162', va='center', ha='center', fontsize=4, rotation=0)
fig13.text(x=1, y=148+50, s='148', va='center', ha='center', fontsize=4, rotation=0)
fig13.text(x=2, y=465+50, s='465', va='center', ha='center', fontsize=4, rotation=0)
fig13.set_xticklabels(labels=['CO', 'CO-L', 'ES'], rotation=0)
fig13.text(x=1, y=1058-58, s='Today\'s value\n(1058)', va='top', ha='center', fontsize=4, rotation=0)

# fig11 = fig.add_subplot(gs[0, 0])
# fig11.minorticks_off()
# data = pyam.IamDataFrame("(a).xlsx")
# data.plot.bar(ax=fig11, title=None, legend=None, cmap=cmap, x='scenario', edgecolor='black', linewidth=0.1)
# fig11.set_xlabel('')
# fig11.set_ylabel('')
# # fig11.set_ylim([0, 150])
# fig11.text(x=0, y=50, s='100\%', va='center', ha='center', fontsize=4, rotation=90)
# fig11.text(x=1, y=50, s='101\%', va='center', ha='center', fontsize=4, rotation=90)
# fig11.text(x=2, y=50, s='125\%', va='center', ha='center', fontsize=4, rotation=90)
# fig11.set_yticks(ticks=[0, 50, 100, 150])
# fig11.set_title('Total costs in \%', fontsize=5)
# fig11.set_xticklabels(labels=['CO', 'CO-L', 'ES'], rotation=0)


# fig11.text(x=0, y=50, s='100\%', va='center', ha='center', fontsize=4, rotation=90)
# fig11.text(x=1, y=50, s='101\%', va='center', ha='center', fontsize=4, rotation=90)
# fig11.text(x=2, y=50, s='125\%', va='center', ha='center', fontsize=4, rotation=90)









# fig21 = fig.add_subplot(gs[1, 0])
# fig21.minorticks_off()

# fig22 = fig.add_subplot(gs[1, 1:3])
fig22.minorticks_off()
fig22.set_title('Demand supplied / not supplied in GWh', fontsize=5)
fig22.set_xticks([0, 1, 2])
fig22.set_xticklabels(labels=['CO', 'CO-L', 'ES'])
fig22.set_xlim([-0.5, 2.5])

labels = ['CO', 'CO-L', 'ES']
high = [5.041, 5.041, 5.041+12.110]
mid = [12.792, 11.748, 12.792+1.691]
x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars
rects1 = fig22.bar(x - width/2, high, width, label='High/Sup.', color="#ECB390")
rects2 = fig22.bar(x + width/2, mid, width, label='Mid/Sup.', color='#C3E5AE')

high = [-12.11, -12.11, -0]
mid = [-1.691, -2.735, -0]

rects1 = fig22.bar(x - width/2, high, width, label='High/Not Sup.', color="#9B0000")
rects2 = fig22.bar(x + width/2, mid, width, label='Mid/Not Sup.', color='#6ECB63')
x_new = [-1, 0, 1, 2, 3, 4]
y_new = 6*[0]
fig22.plot(x_new, y_new, linestyle="solid", color="black")
fig22.set_ylim([-35, 25])

fig22.text(x=-width/2, y=-12.11-2.5, s='-12.11', va='center', ha='center', fontsize=4, rotation=0)
fig22.text(x=-width/2+1, y=-12.11-2.5, s='-12.11', va='center', ha='center', fontsize=4, rotation=0)
# fig22.text(x=-width/2+2, y=-2, s='0', va='center', ha='center', fontsize=4, rotation=0)

fig22.text(x=-width/2, y=5.041+2, s='5.04', va='center', ha='center', fontsize=4, rotation=0)
fig22.text(x=-width/2+1, y=5.041+2, s='5.04', va='center', ha='center', fontsize=4, rotation=0)
fig22.text(x=-width/2+2, y=5.041+12.110+2, s='17.14', va='center', ha='center', fontsize=4, rotation=0)

fig22.text(x=+width/2, y=-1.691-2.5, s='-1.69', va='center', ha='center', fontsize=4, rotation=0)
fig22.text(x=+width/2+1, y=-2.735-2.5, s='-2.74', va='center', ha='center', fontsize=4, rotation=0)
# fig22.text(x=+width/2+2, y=-2, s='0', va='center', ha='center', fontsize=4, rotation=0)

fig22.text(x=+width/2, y=12.792+2, s='12.79', va='center', ha='center', fontsize=4, rotation=0)
fig22.text(x=+width/2+1, y=11.748+2, s='11.75', va='center', ha='center', fontsize=4, rotation=0)
fig22.text(x=+width/2+2, y=12.792+1.691+2, s='14.48', va='center', ha='center', fontsize=4, rotation=0)


# fig13.set_title('Refurbished in \%', fontsize=5)
# fig13.set_xticks(ticks=[0,1,2])
# fig13.set_xticklabels(labels=['CO', 'CO-L', 'ES'], rotation=0)
# fig13.set_ylim([0, 115])
# # fig13.legend()
# fig13.bar_label(rects1, padding=0, fontsize=4)
# fig13.bar_label(rects2, padding=0, fontsize=4)

fig22.legend(fontsize=4, frameon=True)


# fig23 = fig.add_subplot(gs[1, 2])
# fig23.minorticks_off()

plt.tight_layout()
fig.savefig("comparison.eps", format="eps")
fig.savefig("comparison.png", dpi=1000)





