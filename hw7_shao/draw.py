import sys, os
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, "../")
import config
import matplotlib as mpl

def getCmapAndNorm(cmapName, levels, extend):
    cmap = plt.get_cmap(cmapName)
    if extend == "both":
        cmap, norm = mpl.colors.from_levels_and_colors(levels, [cmap(i/len(levels)) for i in range(len(levels)+1)], extend=extend)
    elif extend == "max" or extend=='min':
        cmap, norm = mpl.colors.from_levels_and_colors(levels, [cmap(i/(len(levels)-1)) for i in range(len(levels))], extend=extend)
    return cmap, norm

caseList = ['15k_05m', '15k_1m', '1k_1m', '1k_2m']
var='buoyancy'
binx=np.arange(-500,500,20)
biny=np.arange(0,61,5)

fig, axs = plt.subplots(2,2,sharex=True, sharey=True)
axs = axs.flatten()
for i in np.arange(axs.size):
  plt.sca(axs[i])
  casename = caseList[i]

  data = np.load(f'rce_walker_{casename}_p3.npz')
  y = data['pcp']
  x    = data['buoyancy']
  #x    = data['cape']

  clev = np.arange(-4,-0.99999, 0.2)
  cmap, norm = getCmapAndNorm('Oranges', clev, 'both')
  hist = np.histogram2d(x, y, bins=(binx, biny))
  C = plt.pcolormesh(hist[1], hist[2], np.log10(hist[0].T/hist[0].sum()),cmap=cmap, norm=norm)
  plt.colorbar(C, ticks=clev[::5])
  plt.title(f'{casename}',loc='left',fontweight='bold')
plt.suptitle('Buoyancy [J/kg] v.s. Preci [mm/hr] @convection', fontweight='bold')
plt.tight_layout()
plt.savefig('buo_pcp.png', dpi=250)

binx=np.arange(0,5001,200)
biny=np.arange(0,61,5)

fig, axs = plt.subplots(2,2,sharex=True, sharey=True)
axs = axs.flatten()
for i in np.arange(axs.size):
  plt.sca(axs[i])
  casename = caseList[i]

  data = np.load(f'rce_walker_{casename}_p3.npz')
  y = data['pcp']
  #x    = data['buoyancy']
  x    = data['cape']

  clev = np.arange(-4,-0.99999, 0.2)
  cmap, norm = getCmapAndNorm('Oranges', clev, 'both')
  hist = np.histogram2d(x, y, bins=(binx, biny))
  C = plt.pcolormesh(hist[1], hist[2], np.log10(hist[0].T/hist[0].sum()),cmap=cmap, norm=norm)
  plt.colorbar(C, ticks=clev[::5])
  plt.title(f'{casename}',loc='left',fontweight='bold')
plt.suptitle('CAPE [J/kg] v.s. Preci [mm/hr] @convection', fontweight='bold')
plt.tight_layout()
plt.savefig('cape_pcp.png', dpi=250)

