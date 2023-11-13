import sys, os
import numpy as np
import netCDF4 as nc
from matplotlib import cm
import xarray as xr
sys.path.insert(0, "../")
import config
import parameter
from util.vvmLoader import VVMLoader
from util.dataWriter import DataWriter
from util.calculator import getTemperature

from mpi4py import MPI
comm = MPI.COMM_WORLD
nproc = comm.Get_size()
myid = comm.Get_rank()

if __name__ == "__main__":
    #iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])
    iniTimeIdx, endTimeIdx = 1, 1201
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    hourTimeArange = timeArange*parameter.minPerTimeIdx/(60*24)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    
    caseIdx = myid
    caseName = caseNameList[myid]

    contype='downdraft_3km'
    bins = np.array([-100000, -10, -5, -3, -1, -0.5, 0])
    connum = np.zeros(bins.size-1)
    print(contype)
    print(bins)

    conth = np.zeros((connum.size, zc.size, xc.size))
    conqv = np.copy(conth)
    conqc = np.copy(conth)
    conqi = np.copy(conth)
    conqr = np.copy(conth)
    conbu = np.copy(conth)
    conbup = np.copy(conth)
    conu = np.copy(conth)
    conw = np.copy(conth)
    
    conreg = np.zeros((connum.size, xc.size))
    conprec = np.zeros((connum.size, xc.size))


    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    for tIdx in timeArange:
        print(f"========== {tIdx}, {caseName:22s} =========")
        thData = vvmLoader.loadThermoDynamic(tIdx)
        th = np.array(thData["th"][0])
        qv = np.array(thData["qv"][0])
        qc = np.array(thData["qc"][0])
        qr = np.array(thData["qr"][0])
        qi = np.array(thData["qi"][0])
        thBar = np.mean(th, axis=(1, 2), keepdims=True)
        buoyancy = 9.81 * ((th - thBar) / thBar + 0.608 * qv - (qc + qi + qr))
        buoyancy_prime = buoyancy - np.mean(buoyancy, axis=(1,2), keepdims=True)

        dyData = vvmLoader.loadDynamic(tIdx)
        u = np.array(dyData["u"][0])
        w = np.array(dyData["w"][0])

        sfData = vvmLoader.loadSurface(tIdx)
        sprec = np.array(sfData["sprec"][0])*3600
        reg   = np.any(qc>1e-5, axis=0)

        # find convection center
        izc3km = np.argmin(np.abs(zc-3000))
        con_center = np.argmin(w[izc3km, :, :], axis=1)
        wmax = np.min(w[izc3km, :, :], axis=1)
        ibinlist = np.digitize(wmax, bins)
        for iy in np.arange(yc.size):
            shiftx=xc.size//2 - con_center[iy]  #center 512/2
            ibin = ibinlist[iy]-1
            connum[ibin] += 1
            conth[ibin]  += np.roll(th[:,iy,:],       shiftx, axis=1)
            conqv[ibin]  += np.roll(qv[:,iy,:],       shiftx, axis=1)
            conqc[ibin]  += np.roll(qc[:,iy,:],       shiftx, axis=1)
            conqr[ibin]  += np.roll(qr[:,iy,:],       shiftx, axis=1)
            conqi[ibin]  += np.roll(qi[:,iy,:],       shiftx, axis=1)
            conbu[ibin]  += np.roll(buoyancy[:,iy,:], shiftx, axis=1)
            conbup[ibin] += np.roll(buoyancy_prime[:,iy,:], shiftx, axis=1)
            conu[ibin]   += np.roll(u[:,iy,:],        shiftx, axis=1)
            conw[ibin]   += np.roll(w[:,iy,:],        shiftx, axis=1)
              
            conreg[ibin] += np.roll(reg[iy,:], shiftx)
            conprec[ibin] += np.roll(sprec[iy,:], shiftx)

    dataWriter = DataWriter(outputPath=f"{config.conPath}{caseName}/")
    dataWriter.toNC(f"{contype}.nc", 
                    dict(\
                        conth    = (["ibin", "zc", "xc"], conth / connum.reshape(connum.size,1,1)),
                        conqv    = (["ibin", "zc", "xc"], conqv / connum.reshape(connum.size,1,1)),
                        conqc    = (["ibin", "zc", "xc"], conqc / connum.reshape(connum.size,1,1)),
                        conqr    = (["ibin", "zc", "xc"], conqr / connum.reshape(connum.size,1,1)),
                        conqi    = (["ibin", "zc", "xc"], conqi / connum.reshape(connum.size,1,1)),
                        conbu    = (["ibin", "zc", "xc"], conbu / connum.reshape(connum.size,1,1)),
                        conbup   = (["ibin", "zc", "xc"], conbup/ connum.reshape(connum.size,1,1)),
                        conu     = (["ibin", "zc", "xc"], conu  / connum.reshape(connum.size,1,1)),
                        conw     = (["ibin", "zc", "xc"], conw  / connum.reshape(connum.size,1,1)),
                        conrange = (["ibin", "xc"], conreg  / connum.reshape(connum.size,1)),
                        conrain  = (["ibin", "xc"], conprec / connum.reshape(connum.size,1)),
                        connum   = (["ibin"], connum)),
                    coords = {'ibin': bins[1:], 'zc': zc, 'xc': xc})
    os.system(f"cp {contype}.ctl {config.conPath}{caseName}/")
