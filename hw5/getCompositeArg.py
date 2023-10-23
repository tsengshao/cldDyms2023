import sys
import numpy as np
import netCDF4 as nc
import xarray as xr
sys.path.insert(0, "../")
import config
from util.vvmLoader import VVMLoader
from util.dataWriter import DataWriter

if __name__ == "__main__":
    iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    zz = vvmLoader.loadZZ()

    heightOfMaxW = 5000
    for caseIdx, caseName in enumerate(caseNameList):
        print(caseName)
        vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
        dataWriter = DataWriter(outputPath=f"{config.tvPath}{caseName}/")
        recordArgMaxW = np.zeros(shape=(len(timeArange), len(yc)))
        recordMaxW = np.zeros(shape=(len(timeArange), len(yc)))
        for i, tIdx in enumerate(timeArange):
            print(f"========== {tIdx} =========")
            tdData = vvmLoader.loadThermoDynamic(tIdx)
            qc = np.array(tdData["qc"][0, np.argmin(np.abs(zz-heightOfMaxW)), :, :])
            dyData = vvmLoader.loadDynamic(tIdx)
            w = np.array(dyData["w"][0])
            levelW = np.array(w[np.argmin(np.abs(zz-heightOfMaxW)), :, :])
            argMaxW = np.nanargmax(np.ma.masked_array(levelW, qc<=0), axis=1)
            maxW = np.nanmax(np.ma.masked_array(levelW, qc<=0), axis=1)
            argMaxW = np.where(~maxW.mask, argMaxW, -1)
            maxW = np.where(~maxW.mask, maxW, -1)
            recordMaxW[i, :] = maxW
            recordArgMaxW[i, :] = argMaxW
        np.save(f"recordMaxW-{caseName}.npy", recordMaxW)
        np.save(f"recordArgMaxW-{caseName}.npy", recordArgMaxW)
