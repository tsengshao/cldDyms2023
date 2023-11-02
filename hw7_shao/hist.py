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
    iniTimeIdx, endTimeIdx = 721, 1201
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    hourTimeArange = timeArange*parameter.minPerTimeIdx/(60*24)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    ilev10km = np.argmin(np.abs(zc-10000))
    
    caseIdx = myid
    caseName = caseNameList[myid]

    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    arrpcp = np.array([])
    arrbuo = np.array([])
    arrcap = np.array([])
    for tIdx in timeArange:
        print(f"========== {tIdx}, {caseName:22s} =========")
        ncf = nc.Dataset(f"{config.disPath}{caseName}/dis-{tIdx:06d}.nc")
        dis = ncf.variables['dis'][0]
        ncf.close()

        ncf = nc.Dataset(f"{config.buoyancyPath}{caseName}/buoyancy-{tIdx:06d}.nc")
        buoyancy = ncf.variables['buoyancy'][0][:ilev10km,:,:]
        buoyancy = np.trapz(buoyancy, x=zc[:ilev10km], axis=0)
        ncf.close()

        #/data/C.shaoyu/CD2023/dat/vvmProperties/capecin/rce_walker_15k_05m_p3/cape-000005.nc
        ncf = nc.Dataset(f"{config.capecinPath}{caseName}/cape-{tIdx:06d}.nc")
        cape = ncf.variables['cape'][0]
        ncf.close()

        sfData = vvmLoader.loadSurface(tIdx)
        sprec   = np.array(sfData["sprec"][0]) * 3600
        
        scale=1
        ind = np.where(dis<=scale)
        arrpcp = np.hstack([arrpcp,    sprec[ind]])
        arrbuo = np.hstack([arrbuo, buoyancy[ind]])
        arrcap = np.hstack([arrcap,     cape[ind]])

    np.savez(f'{caseName}.npz', pcp=arrpcp, buoyancy=arrbuo, cape=arrcap)

