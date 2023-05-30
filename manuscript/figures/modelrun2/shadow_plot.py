import matplotlib.pyplot as plt
import pandas
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.colors as c
import matplotlib

plt.style.use('science')

shadows = pandas.read_excel('shadow.xlsx', header=None)

fig, ax = plt.subplots()

x = range(0, 26, 1)

bludenz = shadows.loc[0, :]
dornbirn = shadows.loc[1, :]

mark = [5, 10, 21]
mark2 = [5, 10]

ax.plot(x, bludenz, color='#5ab4ac', markevery=mark, marker="o", markersize=4)
ax.plot(x, dornbirn, color='#d8b365', markevery=mark2, marker="o", markersize=4)

ax.set_xticks(ticks=[0, 5, 10, 15, 20, 25])
ax.set_xticklabels(labels=['2025', '2030', '2035', '2040', '2045', '2050'])

ax.set_title(r'Nodal shadow price ($\lambda^{CO}$) in EUR/MWh')
_patches = []
_line = Line2D(
    [0],
    [0],
    label='Near-feed node (Dornbirn)',
    color='#d8b365',
    linewidth=2,
    linestyle="solid",
)
_patches.extend([_line])
_line = Line2D(
    [0],
    [0],
    label='Off-feed node (Bludenz)',
    color='#5ab4ac',
    linewidth=2,
    linestyle="solid",
)
_patches.extend([_line])

leg = ax.legend(
    handles=_patches,
    loc="upper right",
    fontsize=7,
    framealpha=1,
    handlelength=0.25,
    handletextpad=0.5,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="#161616",
    frameon=True,
    ncol=1,
)

zero = shadows.loc[2, :]

ax.plot(x, zero, color='lightgray', zorder=-100, linestyle='dotted')

leg.get_frame().set_linewidth(0.25)

fig.savefig('shadow_example.png', dpi=1000)
fig.savefig('shadow_example.eps', format='eps')

