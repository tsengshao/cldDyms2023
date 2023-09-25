import sys
import numpy as np
import netCDF4 as nc
from matplotlib import cm
import xarray as xr
sys.path.insert(0, "../")
import config
import parameter
from util.vvmLoader import VVMLoader
from util.dataWriter import DataWriter
from util.calculator import getTemperature, cal_saturated_rv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    caseNameList = config.caseNameList
    iniTimeIdx, endTimeIdx = 0, 1201
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    hourTimeArange = timeArange*parameter.minPerTimeIdx/(60*24)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    rbCmap = plt.get_cmap("rainbow")
    
    for caseIdx, caseName in enumerate(caseNameList):
        print(caseName)
        vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
        rho = np.tile(vvmLoader.loadRHO()[:-1][:, np.newaxis, np.newaxis], reps=(1, len(yc), len(xc)))
        zz = vvmLoader.loadZZ()
        deltaZZ = np.tile((zz[1:] - zz[:-1])[:, np.newaxis, np.newaxis], reps=(1, len(yc), len(xc)))
        piBar = vvmLoader.loadPIBAR()[:-1][:, np.newaxis, np.newaxis]
        pBar = vvmLoader.loadPBAR()[:-1][:, np.newaxis, np.newaxis]
        dataWriter = DataWriter(outputPath=f"{config.waterPath}{caseName}/")
        for tIdx in timeArange:
            print(f"========== {tIdx} =========")
            thData = vvmLoader.loadThermoDynamic(tIdx)
            tempK = getTemperature(thData["th"][0], pBar, piBar)
            qv = np.array(thData["qv"][0])
            qvs, rvs = cal_saturated_rv(P_hPa=pBar/100, T_K=tempK)
            argHeightLim = np.argmin(np.abs(zc/1e3-15)) + 1
            colRH = np.sum((qv*rho*deltaZZ)[:argHeightLim], axis=0) / np.sum((qvs*rho*deltaZZ)[:argHeightLim], axis=0)
            dataWriter.toNC(f"colRH-{tIdx:06d}.nc", 
                            dict(
                                columnRH = (["time", "yc", "xc"], colRH[np.newaxis, :, :])),
                            coords = {'time': np.ones(shape=(1,)), 'yc': yc, 'xc': xc})
