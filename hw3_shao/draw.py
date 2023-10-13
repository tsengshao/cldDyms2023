import numpy as np
import matplotlib.pyplot as plt

def conv(x):
  c = np.convolve(x, np.ones(24)/24, mode='same')
  c[:12] = np.nan
  c[-12:] = np.nan
  return c

x=np.arange(1201)/24

c=['#E84637', '#FBBC15']

plt.rcParams.update({'font.size':15,
                     'savefig.facecolor':(1,1,1,0),
                     'axes.facecolor' :(1,1,1,1),
                     'axes.linewidth':1.5})

fig, ax = plt.subplots(6,2, figsize=(12, 10),sharex=True)

dat = np.load('crh.npz')
crh_mean = dat['mean']
crh_var  = dat['var']
caseNameList = dat['caseNameList']

plt.sca(ax[0][0])
plt.plot(x, conv(crh_mean[0,:]*100),c=c[0],lw=2)
plt.plot(x, conv(crh_mean[3,:]*100),c=c[1],lw=2)
plt.ylabel('[%]')
plt.title('CRH', weight='bold',fontsize=15,loc='left')
plt.sca(ax[0][1])
plt.plot(x, conv(crh_var[0,:]),c=c[0],lw=2)
plt.plot(x, conv(crh_var[3,:]),c=c[1],lw=2)
plt.title('CRH', weight='bold',fontsize=15,loc='left')


dat = np.load('surface.npz')
var = dat['rain_var']
mean = dat['rain_mean']
plt.sca(ax[1][0])
plt.plot(x, conv(mean[0,:]),c=c[0],lw=2)
plt.plot(x, conv(mean[3,:]),c=c[1],lw=2)
plt.ylabel('[mm]')
plt.title('Rain', weight='bold',fontsize=15,loc='left')
plt.sca(ax[1][1])
plt.plot(x, conv(var[0,:]),c=c[0],lw=2)
plt.plot(x, conv(var[3,:]),c=c[1],lw=2)
plt.ylabel(r'[$mm^2$]')
plt.title('Rain', weight='bold',fontsize=15,loc='left')

var  = dat['sst_var']
mean = dat['sst_mean']
plt.sca(ax[2][0])
plt.plot(x, conv(mean[0,:]),c=c[0],lw=2)
plt.plot(x, conv(mean[3,:]),c=c[1],lw=2)
plt.ylabel('[K]')
plt.title('SST', weight='bold',fontsize=15,loc='left')
plt.sca(ax[2][1])
plt.plot(x, conv(var[0,:]),c=c[0],lw=2)
plt.plot(x, conv(var[3,:]),c=c[1],lw=2)
plt.ylabel(r'[$K^2$]')
plt.title('SST', weight='bold',fontsize=15,loc='left')

dat = np.load('waterPath.npz')
iw=0

for iw in range(len(dat['waterlist'])):
  var = dat['var'][:,iw,:]
  mean = dat['mean'][:,iw,:]
  water = dat['waterlist'][iw]
  
  plt.sca(ax[3+iw][0])
  plt.plot(x, conv(mean[0,:]),c=c[0],lw=2)
  plt.plot(x, conv(mean[3,:]),c=c[1],lw=2)
  plt.ylabel('[mm]')
  plt.title('column '+water, weight='bold',fontsize=15,loc='left')
  plt.sca(ax[3+iw][1])
  plt.plot(x, conv(var[0,:]),c=c[0],lw=2)
  plt.plot(x, conv(var[3,:]),c=c[1],lw=2)
  plt.ylabel(r'[$mm^2$]')
  plt.title('column '+water, weight='bold',fontsize=15,loc='left')
  plt.xlim(0,50)
ax[5,0].set_xlabel('[day]')
ax[5,1].set_xlabel('[day]')

plt.subplots_adjust(wspace=0.25, hspace=0.3,bottom=0.08, top=0.97, left=0.07, right=0.98)
plt.savefig('evolution.png', dpi=150)

