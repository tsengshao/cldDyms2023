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
    
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(15, 7))
    for caseIdx, caseName in enumerate(caseNameList):
        print(caseName)
        vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
        rho = np.tile(vvmLoader.loadRHO()[:-1][:, np.newaxis, np.newaxis], reps=(1, len(yc), len(xc)))
        zz = vvmLoader.loadZZ()
        deltaZZ = np.tile((zz[1:] - zz[:-1])[:, np.newaxis, np.newaxis], reps=(1, len(yc), len(xc)))
        dataWriter = DataWriter(outputPath=f"{config.waterPath}{caseName}/")
        for tIdx in timeArange:
            print(f"========== {tIdx} =========")
            qvPath = np.sum(np.array(vvmLoader.loadThermoDynamic(tIdx)["qv"][0]) * rho * deltaZZ, axis=0)
            qcPath = np.sum(np.array(vvmLoader.loadThermoDynamic(tIdx)["qc"][0]) * rho * deltaZZ, axis=0)
            qiPath = np.sum(np.array(vvmLoader.loadThermoDynamic(tIdx)["qi"][0]) * rho * deltaZZ, axis=0)
            
            dataWriter.toNC(f"waterPath-{tIdx:06d}.nc", 
                            dict(
                                qvPath = (["time", "yc", "xc"], qvPath[np.newaxis, :, :]),
                                qcPath = (["time", "yc", "xc"], qcPath[np.newaxis, :, :]),
                                qiPath = (["time", "yc", "xc"], qiPath[np.newaxis, :, :])),
                            coords = {'time': np.ones(shape=(1,)), 'yc': yc, 'xc': xc})
