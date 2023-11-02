import sys, os
import numpy as np
import netCDF4 as nc
import scipy as sci
from matplotlib import cm
import xarray as xr
sys.path.insert(0, "../")
import config
import parameter
from util.vvmLoader import VVMLoader
from util.dataWriter import DataWriter
from util.calculator import getTemperature
import matplotlib.pyplot as plt
import xarray as xr

from mpi4py import MPI
comm = MPI.COMM_WORLD
nproc = comm.Get_size()
myid = comm.Get_rank()

if __name__ == "__main__":
    #iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])
    #iniTimeIdx, endTimeIdx = 1, 1201
    iniTimeIdx, endTimeIdx = 961, 1201
    iniTimeIdx, endTimeIdx = 600, 1201
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    hourTimeArange = timeArange*parameter.minPerTimeIdx/(60*24)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    zz = vvmLoader.loadZZ()[:-1]
    rhoz = vvmLoader.loadRHOZ()[:, np.newaxis, np.newaxis]

    ilev5km=np.argmin(np.abs(zc-5000))
    ilev10km=np.argmin(np.abs(zc-10000))
    depthThreshold=3000
    prange = np.arange(0, 301, 5) #2km, 0km->300km
    buopz = np.zeros((2, zc.size, prange.size-1))
    qvpz = np.zeros((2,  zc.size, prange.size-1))
    thpz = np.zeros((2,  zc.size, prange.size-1))
    qcpz = np.zeros((2,  zc.size, prange.size-1))
    qipz = np.zeros((2,  zc.size, prange.size-1))
    qrpz = np.zeros((2,  zc.size, prange.size-1))
    wpz = np.zeros((2,  zc.size, prange.size-1))
    pwpz = np.zeros((2,  zc.size, prange.size-1))
    vwpz = np.zeros((2,  zc.size, prange.size-1))
    samplenum = np.zeros((2, prange.size-1))
    
    caseIdx = myid
    caseName = caseNameList[myid]

    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    dataWriter = DataWriter(outputPath=f"{config.disPath}{caseName}/")
    allCoreDepth = np.array([])
    for tIdx in timeArange:
        print(f"========== {tIdx}, {caseName:22s} =========")
        thData = vvmLoader.loadThermoDynamic(tIdx)
        th = np.array(thData["th"][0])
        qv = np.array(thData["qv"][0])
        qc = np.array(thData["qc"][0])
        qr = np.array(thData["qr"][0])
        qi = np.array(thData["qi"][0])
        the = th + 2.5e6 * qv / 1004
        thBar = np.mean(th, axis=(1, 2), keepdims=True)
        buoyancy = 9.81 * ((th - thBar) / thBar + 0.608 * qv - (qc + qi + qr))
        buoyancy = buoyancy - np.mean(buoyancy, axis=(1,2), keepdims=True)

        dyData = vvmLoader.loadDynamic(tIdx)
        w = np.array(dyData["w"][0])
        u = np.array(dyData["u"][0])
        v = np.array(dyData["v"][0])

        threshold = 10
        wMap = np.sum(np.where(w[:ilev10km,:]>threshold,1,0), axis=0)
        coreThick = (w[:ilev10km,:]>threshold)*np.diff(zz).reshape(zz.size-1,1,1)[:ilev10km,:]
        coreThick = np.sum(coreThick, axis=0)

        wMap = np.where(w[ilev5km,:]>=threshold,1,0)

        labelArray, nLabel = sci.ndimage.label(\
                             np.where(wMap>0,1,0))
        for y in range(labelArray.shape[0]):
            if labelArray[y, 0] > 0 and labelArray[y, -1] > 0:
                labelArray[labelArray == labelArray[y, -1]] = labelArray[y, 0]
        for x in range(labelArray.shape[1]):
            if labelArray[0, x] > 0 and labelArray[-1, x] > 0:
                labelArray[labelArray == labelArray[-1, x]] = labelArray[0, x]
        labelList = np.sort(np.unique(labelArray))[1:]
        nLabel = labelList.size
        if(nLabel==0): continue

        xloc = np.zeros(nLabel, dtype=int)
        yloc = np.zeros(nLabel, dtype=int)
        xarr, yarr = np.meshgrid(np.arange(xc.size,dtype=int),\
                                 np.arange(yc.size,dtype=int))
        for ilab in range(nLabel):
            ind = np.where(labelArray==labelList[ilab])
            ii  = np.argmax(wMap[ind])
            yloc[ilab] = int(ind[0][ii])
            xloc[ilab] = int(ind[1][ii])

        dis = ((xarr[np.newaxis, ...] - xloc[:, np.newaxis, np.newaxis])**2\
             + (yarr[np.newaxis, ...] - yloc[:, np.newaxis, np.newaxis])**2)**0.5
        minDis = np.min(dis, axis=0)
        minPts = np.argmin(dis, axis=0)   #z

        dismap = dis[minPts, yarr, xarr]*2  #km

        #ptxloc = (xloc[:, np.newaxis, np.newaxis]*np.ones(dis.shape))[minPts, yarr, xarr]
        #ptyloc = (yloc[:, np.newaxis, np.newaxis]*np.ones(dis.shape))[minPts, yarr, xarr]
        ptxloc = np.zeros(dismap.shape)
        ptyloc = np.zeros(dismap.shape)
        for ilab in range(nLabel):
            ptxloc[minPts==ilab] = xloc[ilab]
            ptyloc[minPts==ilab] = yloc[ilab]

        dataWriter.toNC(f"dis-{tIdx:06d}.nc", \
                        dict(
                            dis       = (["time", "yc", "xc"], dismap[np.newaxis, :, :]),
                            xloc      = (["time", "yc", "xc"], ptxloc[np.newaxis, :, :]),
                            yloc      = (["time", "yc", "xc"], ptyloc[np.newaxis, :, :])),
                        coords = {'time': np.ones(shape=(1,)), 'yc': yc, 'xc': xc})

        continue

        ang3d = np.arctan2(yarr-ptyloc, xarr-ptxloc).reshape(1, yc.size, xc.size)
        pwind  = v*np.cos(np.pi/2-ang3d) + u*np.cos(ang3d)
        vwind  = v*np.sin(np.pi/2-ang3d) - u*np.sin(ang3d)

        corenum = wMap[yloc, xloc]
        corethi = coreThick[yloc, xloc]

        thickmap = coreThick[ptyloc.astype(int), ptxloc.astype(int)]

        typeidx = np.where(thickmap<3000,0,1).astype(int)
        print('start to sampling')
        for ip in np.arange(prange.size-1):
           for itype in range(2):
             condi = (prange[ip]<=dismap)*(prange[ip+1]>dismap)*(typeidx==itype)
             idxy, idxx = np.where(condi)
             samplenum[itype, ip] += idxy.size
             buopz[itype, :, ip]  += np.sum( buoyancy[:, idxy, idxx], axis=1 )
             thpz[itype, :, ip]   += np.sum( th[:, idxy, idxx], axis=1 )
             qvpz[itype, :, ip]   += np.sum( qv[:, idxy, idxx], axis=1 )
             qcpz[itype, :, ip]   += np.sum( qc[:, idxy, idxx], axis=1 )
             qipz[itype, :, ip]   += np.sum( qi[:, idxy, idxx], axis=1 )
             qrpz[itype, :, ip]   += np.sum( qr[:, idxy, idxx], axis=1 )
             pwpz[itype, :, ip]   += np.sum( pwind[:, idxy, idxx], axis=1 )
             vwpz[itype, :, ip]   += np.sum( vwind[:, idxy, idxx], axis=1 )
             wpz[itype, :, ip]    += np.sum( w[:, idxy, idxx], axis=1 )
    sys.exit('only write dis-nc')

    buopz  /= samplenum[:, np.newaxis, :]
    thpz   /= samplenum[:, np.newaxis, :]
    qvpz   /= samplenum[:, np.newaxis, :]
    qcpz   /= samplenum[:, np.newaxis, :]
    qipz   /= samplenum[:, np.newaxis, :]
    qrpz   /= samplenum[:, np.newaxis, :]
    pwpz   /= samplenum[:, np.newaxis, :]
    vwpz   /= samplenum[:, np.newaxis, :]
    wpz    /= samplenum[:, np.newaxis, :]

    np.savez(f'con_{caseName}.npz', prange=prange, zc=zc, typeth=3000, \
                                    buopz=buopz, th=thpz, qv=qvpz, \
                                    qc=qcpz, qi=qipz, qr=qrpz, \
                                    pwind=pwpz, vwind=vwpz, w=wpz)
