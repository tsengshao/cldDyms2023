import sys, os
import numpy as np
import netCDF4 as nc
import xarray as xr
sys.path.insert(0, "../")
import config
import parameter
from util.vvmLoader import VVMLoader
from util.dataWriter import DataWriter
import util.calculator as ucalc
import matplotlib as mpl
import matplotlib.pyplot as plt

from mpi4py import MPI
comm = MPI.COMM_WORLD
nproc = comm.Get_size()
myid = comm.Get_rank()

if __name__ == "__main__":
    #iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])
    #iniTimeIdx, endTimeIdx = 721, 1201
    iniTimeIdx, endTimeIdx = 721, 722
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    hourTimeArange = timeArange*parameter.minPerTimeIdx/(60*24)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    ilev10km = np.argmin(np.abs(zc-10000))
    pibar=vvmLoader.loadPIBAR()[:-1]
    
    
    caseIdx = myid
    caseName = caseNameList[myid]

    mpl.rcParams.update({'font.size': 15,
                         'axes.linewidth': 2})

    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    for tIdx in timeArange:
        print(f"========== {tIdx}, {caseName:22s} =========")
        ncf = nc.Dataset(f"{config.disPath}{caseName}/dis-{tIdx:06d}.nc")
        dis = ncf.variables['dis'][0]
        ncf.close()

        ncf = nc.Dataset(f"{config.buoyancyPath}{caseName}/buoyancy-{tIdx:06d}.nc")
        buoyancy = ncf.variables['buoyancy'][0]
        #buoyancy = np.trapz(buoyancy, x=zc[:ilev10km], axis=0)
        ncf.close()

        sfData = vvmLoader.loadSurface(tIdx)
        sprec   = np.array(sfData["sprec"][0]) * 3600

        dyData = vvmLoader.loadDynamic(tIdx)
        w   = np.array(dyData["w"][0])

        thData = vvmLoader.loadThermoDynamic(tIdx)
        qc   = np.array(thData["qc"][0])
        qi   = np.array(thData["qi"][0])
        qv   = np.array(thData["qv"][0])
        th   = np.array(thData["th"][0])

        te   = ucalc.getTemperature(th, piBar=pibar[:,np.newaxis,np.newaxis])
        mse  = ucalc.getMSE(te, zc[:,np.newaxis,np.newaxis], qv)/1004

        #kernel = ucalc.getGaussianWeight(np.min([xc.size, yc.size]), std=0.5, normalize=True)
        #convDataB = ucalc.getGaussianConvolve(buoyancy, kernel, method="fft")
        #convDataW = ucalc.getGaussianConvolve(w, kernel, method="fft")

        ipt=-1

        fig, ax = plt.subplots()
        norm=mpl.colors.BoundaryNorm(boundaries=[0, 1, 2, 4, 5, 10, 15, 20, 40],ncolors=265,extend='both')
        plt.pcolormesh(xc/1000, yc/1000, sprec, norm=norm)
        plt.colorbar()
        plt.contour(xc/1000, yc/1000, dis, levels=[0, 5, 10, 15], colors=['k'])
        yidx, xidx = np.where(dis<0.5)
        plt.scatter(xc[xidx]/1000, yc[yidx]/1000, s=10, fc='k')
        plt.title(f'Preci. [mm/hr] / t={tIdx}', loc='left', fontweight='bold')
        plt.tight_layout()


        stdList = [0.5,1,1.5,2,3]
        # Buoyancy
        fig, ax = plt.subplots(2, 3, figsize=(12,8), sharex=True, sharey=True)
        #cax = fig.add_axes([0.95,1,0.1,0.8])
        ax = ax.flatten()
        plt.sca(ax[0])
        xslice=slice(xidx[ipt]-20, xidx[ipt]+20, 1)
        yslice=yidx[ipt]
        xyplane = lambda x: x[:, yslice, xslice]
        xx=xc[xslice]/1000-xc[xidx[ipt]]/1000
        zz=zc/1000

        norm=mpl.colors.BoundaryNorm(boundaries=np.arange(-0.05,0.051,0.01),ncolors=265,extend='both')
        C = plt.pcolormesh(xx, zz, buoyancy[:, yslice, xslice], norm=norm, cmap=plt.cm.coolwarm)
        #plt.colorbar(cax=cax)
        plt.contour(xx, zz, xyplane(qc)+xyplane(qi), levels=[1e-5], linewidths=[3], colors=['k'])
        plt.contour(xx, zz, w[:,yslice,xslice], levels=[0.5, 5, 8], linewidths=[1], colors=['g'])
        plt.ylim(0, 18)
        #plt.xlabel('xc [km]')
        plt.ylabel('zc [km]')
        plt.title(r'Buoyancy[$ms^{-2}$]', loc='left', fontweight='bold')

        for idx, std in enumerate(stdList):
          idx += 1
          plt.sca(ax[idx])
          kernel = ucalc.getGaussianWeight(np.min([xc.size, yc.size]), std=std, normalize=True)
          convDataB = ucalc.getGaussianConvolve(buoyancy, kernel, method="fft")
          #fig, ax = plt.subplots(figsize=(12,8))
          norm=mpl.colors.BoundaryNorm(boundaries=np.arange(-0.05,0.051,0.01),ncolors=265,extend='both')
          plt.pcolormesh(xx, zz, convDataB[:, yslice, xslice], norm=norm, cmap=plt.cm.coolwarm)
          #if(idx%3==2): plt.colorbar()
          plt.contour(xx, zz, xyplane(qc)+xyplane(qi), levels=[1e-5], linewidths=[3], colors=['k'])
          plt.contour(xx, zz, xyplane(w), levels=[0.5, 5, 8], linewidths=[1], colors=['g'])
          plt.ylim(0, 18)
          if(idx//3==1): plt.xlabel('xc [km]')
          if(idx%3==0):  plt.ylabel('zc [km]')
          plt.title(r'$\sigma$' + f' = {std:.1f} ({std*12:.1f}km)', loc='left', fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(right=0.9)
        plt.colorbar(C, cax=fig.add_axes([0.91,0.1,0.02,0.8]))

        # W
        fig, ax = plt.subplots(2, 3, figsize=(12,8), sharex=True, sharey=True)
        ax = ax.flatten()
        plt.sca(ax[0])
        xslice=slice(xidx[ipt]-20, xidx[ipt]+20, 1)
        yslice=yidx[ipt]
        xyplane = lambda x: x[:, yslice, xslice]
        xx=xc[xslice]/1000-xc[xidx[ipt]]/1000
        zz=zc/1000

        norm=mpl.colors.BoundaryNorm(boundaries=[-3,-2,-1,-0.1,0.1,1,2,3],ncolors=265,extend='both')
        C = plt.pcolormesh(xx, zz, w[:, yslice, xslice], norm=norm, cmap=plt.cm.coolwarm)
        #plt.colorbar(cax=cax)
        plt.contour(xx, zz, xyplane(qc)+xyplane(qi), levels=[1e-5], linewidths=[3], colors=['k'])
        plt.contour(xx, zz, w[:,yslice,xslice], levels=[0.5, 5, 8], linewidths=[1], colors=['g'])
        plt.ylim(0, 18)
        #plt.xlabel('xc [km]')
        plt.ylabel('zc [km]')
        plt.title(r'w[$ms^{-1}$]', loc='left', fontweight='bold')

        for idx, std in enumerate(stdList):
          idx += 1
          plt.sca(ax[idx])
          kernel = ucalc.getGaussianWeight(np.min([xc.size, yc.size]), std=std, normalize=True)
          convData = ucalc.getGaussianConvolve(w, kernel, method="fft")
          #fig, ax = plt.subplots(figsize=(12,8))
          norm=mpl.colors.BoundaryNorm(boundaries=[-3,-2,-1,-0.1,0.1,1,2,3],ncolors=265,extend='both')
          plt.pcolormesh(xx, zz, xyplane(convData), norm=norm, cmap=plt.cm.coolwarm)
          #if(idx%3==2): plt.colorbar()
          plt.contour(xx, zz, xyplane(qc)+xyplane(qi), levels=[1e-5], linewidths=[3], colors=['k'])
          plt.contour(xx, zz, xyplane(w), levels=[0.5, 5, 8], linewidths=[1], colors=['g'])
          plt.ylim(0, 18)
          if(idx//3==1): plt.xlabel('xc [km]')
          if(idx%3==0):  plt.ylabel('zc [km]')
          plt.title(r'$\sigma$' + f' = {std:.1f} ({std*12:.1f}km)', loc='left', fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(right=0.9)
        plt.colorbar(C, cax=fig.add_axes([0.91,0.1,0.02,0.8]))

        # MSE
        fig, ax = plt.subplots(2, 3, figsize=(12,8), sharex=True, sharey=True)
        ax = ax.flatten()
        plt.sca(ax[0])
        xslice=slice(xidx[ipt]-20, xidx[ipt]+20, 1)
        yslice=yidx[ipt]
        xyplane = lambda x: x[:, yslice, xslice]
        xx=xc[xslice]/1000-xc[xidx[ipt]]/1000
        zz=zc/1000

        #clevs = np.arange(335,355,2)
        clevs = np.arange(340,350.001,0.05)
        norm=mpl.colors.BoundaryNorm(boundaries=clevs,ncolors=256,extend='both')
        C = plt.pcolormesh(xx, zz, xyplane(mse), norm=norm, cmap=plt.cm.Reds)
        plt.contour(xx, zz, xyplane(qc)+xyplane(qi), levels=[1e-5], linewidths=[3], colors=['k'])
        plt.contour(xx, zz, xyplane(w), levels=[0.5, 5, 8], linewidths=[1], colors=['g'])
        plt.ylim(0, 18)
        plt.ylabel('zc [km]')
        plt.title(r'MSE[$K$]', loc='left', fontweight='bold')

        for idx, std in enumerate(stdList):
          idx += 1
          plt.sca(ax[idx])
          kernel = ucalc.getGaussianWeight(np.min([xc.size, yc.size]), std=std, normalize=True)
          convData = ucalc.getGaussianConvolve(mse, kernel, method="fft")
          plt.pcolormesh(xx, zz, xyplane(convData), norm=norm, cmap=plt.cm.Reds)
          plt.contour(xx, zz, xyplane(qc)+xyplane(qi), levels=[1e-5], linewidths=[3], colors=['k'])
          plt.contour(xx, zz, xyplane(w), levels=[0.5, 5, 8], linewidths=[1], colors=['g'])
          plt.ylim(0, 18)
          if(idx//3==1): plt.xlabel('xc [km]')
          if(idx%3==0):  plt.ylabel('zc [km]')
          plt.title(r'$\sigma$' + f' = {std:.1f} ({std*12:.1f}km) -- {kernel.sum():.1f}', loc='left', fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(right=0.9)
        plt.colorbar(C, cax=fig.add_axes([0.91,0.1,0.02,0.8]))

        sys.exit()


