import numpy as np
import matplotlib.pyplot as plt
import sys, os

"""
con.15k_05m_p3.npz
con.15k_1m_p3.npz
con.1k_1m_p3.npz
con.1k_2m_p3.npz
"""

ename='15k_05m_p3'
data = np.load(f'con.{ename}.npz')
prange=data['prange']
xp=(prange[:-1]+prange[1:])/2
zc=data['zc']/1000
thick=data['typeth']/1000
typen=['<','>']

thbar=np.nanmean(data['th'], axis=2, keepdims=True)
buo = 9.81 * ((data['th']-thbar)/thbar + 0.608*data['qv'] - (data['qc']+data['qi']+data['qr']))
buo = buo - np.nanmean(buo, axis=2, keepdims=True)

for i in np.arange(2):
  fig, ax = plt.subplots()
  #plt.contourf(xp, zc, data['th'][i], levels=np.arange(300,400,5),cmap=plt.cm.hot,extend='both')
  plt.pcolormesh(xp, zc, buo[i], vmin=-0.02,vmax=0.02,cmap=plt.cm.RdBu_r)
  plt.colorbar(extend='both')
  plt.contour(xp,zc,data['qv'][i]*1e3, levels=[1,3,5,7,10,15,20],colors=['0.5'],linewidths=[1])
  plt.contour(xp,zc,data['qc'][i]+data['qi'][i], levels=[1e-5,1e-4],colors=['k'],linewidths=[2])
  plt.contour(xp,zc,data['w'][i],levels=np.arange(-0.2,0.5,0.1),colors=['g'],linewidths=[2])
  plt.xlim(0,150)
  plt.ylim(0,15)
  plt.title(f'{ename} / core_thickness{typen[i]}{thick:.0f}km',loc='left',fontweight='bold')
  plt.savefig(f'cross.{ename}.type{i}.png',dpi=200)
  plt.close('all')




