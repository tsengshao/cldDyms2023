import numpy as np
import matplotlib.pyplot as plt
import sys, os

"""
con.15k_05m_p3.npz
con.15k_1m_p3.npz
con.1k_1m_p3.npz
con.1k_2m_p3.npz
"""

def draw(draw, drawm, xlab):
  plt.fill_betweenx(zc, x1=draw[0], x2=draw[1], color='0.6')
  plt.plot(draw[0],zc, c='k', lw=1)
  plt.plot(draw[1],zc, c='k', lw=1)
  plt.plot(drawm[:], zc, c='k', lw=1)
  plt.title(xlab,loc='left',fontweight='bold')
  


ename='15k_05m_p3'
data = np.load(f'prof.{ename}.npz')
pr=data['pr']
zc=data['zc']/1000

fig, ax = plt.subplots(2,2,sharey=True, figsize=(10,10))
plt.sca(ax[0,0])
draw(data['buo']*100, data['buomean']*100,r'Buoyancy$[10^{-2}ms^{-2}]$')
plt.ylabel('zc [km]')
plt.xlim(-4,4)

plt.sca(ax[1,0])
draw(data['w'], data['wmean'],r'W$[ms^{-1}]$')
plt.xlim(-0.4,0.6)

plt.sca(ax[0,1])
draw(data['mf']*1e3, data['mfmean']*1e3,r'Mass Flux$[gm^{-2}s^{-1}]$')
plt.xlim(0,500)

plt.sca(ax[1,1])
draw(data['the'], data['themean'],r'theta_e$[K]$')
plt.xlim(330,370)
plt.ylim(0,15)
plt.suptitle(ename+' / thickness>3km',fontweight='bold')
plt.savefig(f'prof.{ename}prof.type1.png',dpi=200)
plt.close('all')
