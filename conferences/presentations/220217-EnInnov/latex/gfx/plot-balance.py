
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey

plt.style.use(["science"])

fig = plt.figure(figsize=(4,4))
ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[])
sankey = Sankey(ax=ax, scale=0.01, offset=0.2, head_angle=180, format='%.0f', unit='%')



sankey.add(flows=[552.57, -461.04, 9.04, -100.57],
       orientations=[0, 0, -1, 1],
       trunklength=1,
       pathlengths=[1,1,1,1])
Results = sankey.finish()

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)

# plt.title("Gas balance from Austria in 2017")
plt.tight_layout()

for text in Results[0].texts:
    text.set(fontsize=0)
    
ax.text(x=-2.8, y=0, s='Import\n($553~TWh$)', rotation=0, ha='center', va='center', fontsize=12)
ax.text(x=3.7, y=-0.5, s='Export\n($461~TWh$)', rotation=0, ha='center', va='center', fontsize=12)
ax.text(x=-2.3, y=-3.75, s='Production \&\nstorage\n($9~TWh$)', rotation=0, ha='center', va='center', fontsize=12)
ax.text(x=2.75, y=3.5, s='Demand\n($101~TWh$)', rotation=0, ha='center', va='center', fontsize=12)
ax.text(x=0.5, y=0, s='Austria\nin 2017', rotation=0, ha='center', va='center', fontsize=14)

Results[0].patch.set_color('#B762C1')
Results[0].text.set_fontweight('bold')



fig.savefig('Balance.png', dpi=1000)
fig.savefig('Balance.eps', format='eps')




# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
#                      title="Flow Diagram of a Widget")
# sankey = Sankey(ax=ax, scale=0.01, offset=0.2, head_angle=180,
#                 format='%.0f', unit='%')
# sankey.add(flows=[25, 0, 60, -10, -20, -5, -15, -10, -40],
#            labels=['', '', '', 'First', 'Second', 'Third', 'Fourth',
#                    'Fifth', 'Hurray!'],
#            orientations=[-1, 1, 0, 1, 1, 1, -1, -1, 0],
#            pathlengths=[0.25, 0.25, 0.25, 0.25, 0.25, 0.6, 0.25, 0.25,
#                         0.25],
#            patchlabel="Widget\nA")  # Arguments to matplotlib.patches.PathPatch
# diagrams = sankey.finish()
# 
# diagrams[0].text.set_fontweight('bold')