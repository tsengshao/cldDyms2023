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

from mpi4py import MPI
comm = MPI.COMM_WORLD
nproc = comm.Get_size()
myid = comm.Get_rank()

if __name__ == "__main__":
    #iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])
    #iniTimeIdx, endTimeIdx = 1, 1201
    iniTimeIdx, endTimeIdx = 961, 1201
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
    
    caseIdx = myid
    caseName = caseNameList[myid]
    scaleList = [20,10,20,10] #km
    scale    = scaleList[myid]

    wlist=np.zeros((zc.size,1))
    blist=np.zeros((zc.size,1))
    mlist=np.zeros((zc.size,1))
    elist=np.zeros((zc.size,1))

    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
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

        mf = np.where(w>0, rhoz*w, 0)

        threshold = 1
        wMap = np.sum(np.where(w[:ilev10km,:]>threshold,1,0), axis=0)
        coreThick = (w[:ilev10km,:]>threshold)*np.diff(zz).reshape(zz.size-1,1,1)[:ilev10km,:]
        coreThick = np.sum(coreThick, axis=0)

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

        ptxloc = np.zeros(dismap.shape)
        ptyloc = np.zeros(dismap.shape)
        for ilab in range(nLabel):
            ptxloc[minPts==ilab] = xloc[ilab]
            ptyloc[minPts==ilab] = yloc[ilab]


        corenum = wMap[yloc, xloc]
        corethi = coreThick[yloc, xloc]

        thickmap = coreThick[ptyloc.astype(int), ptxloc.astype(int)]

        typeidx = np.where(thickmap<3000,0,1).astype(int)
        print('start to sampling')
        itype = 1
        condi = (scale>=dismap)*(typeidx==itype)
        idxy, idxx = np.where(condi)
        wlist = np.hstack((wlist, w[:, idxy, idxx] ))
        blist = np.hstack((blist, buoyancy[:, idxy, idxx] ))
        mlist = np.hstack((mlist, mf[:, idxy, idxx] ))
        elist = np.hstack((elist, the[:, idxy, idxx] ))

    wlist = wlist[:,1:]
    blist = blist[:,1:]
    mlist = mlist[:,1:]
    elist = elist[:,1:]

    pr = np.array([10, 90])
    wpr = np.percentile(wlist, pr, axis=1)
    wm  = np.mean(wlist, axis=1)
    bpr = np.percentile(blist, pr, axis=1)
    bm  = np.mean(blist, axis=1)
    mpr = np.percentile(mlist, pr, axis=1)
    mm  = np.mean(mlist, axis=1)
    epr = np.percentile(elist, pr, axis=1)
    em  = np.mean(elist, axis=1)

    np.savez(f'prof.{caseName[11:]}', pr=pr, zc=zc, \
                              w=wpr, wmean=wm, \
                              buo=bpr, buomean=bm, \
                              mf=mpr, mfmean=mm, \
                              the=epr, themean=em)
