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
from util.calculator import getTemperature
import matplotlib.pyplot as plt

if __name__ == "__main__":
    iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])
    caseNameList = config.caseNameList
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
        pBar3D = np.tile(vvmLoader.loadPBAR()[:-1][:, np.newaxis, np.newaxis], reps=(1, len(yc), len(xc)))
        dataWriter = DataWriter(outputPath=f"{config.tvPath}{caseName}/")
        for tIdx in timeArange:
            print(f"========== {tIdx} =========")
            thData = vvmLoader.loadThermoDynamic(tIdx)
            th = np.array(thData["th"][0])
            qv = np.array(thData["qv"][0])
            qc = np.array(thData["qc"][0])
            qr = np.array(thData["qr"][0])
            qi = np.array(thData["qi"][0])
            ql = qc + qr + qi
            temp = getTemperature(th, pBar=pBar3D)
            qvComp = temp * 0.608 * qv
            qlComp = temp * ql
            tv = temp + qvComp - qlComp #temp * (1 + 0.608 * qv - ql)

            tv       = tv - np.mean(tv, axis=1, keepdims=True)
            tempComp = temp - np.mean(temp, axis=1, keepdims=True)
            qvComp   = qvComp - np.mean(qvComp, axis=1, keepdims=True)
            qlComp   = qlComp - np.mean(qlComp, axis=1, keepdims=True)
            
            dataWriter.toNC(f"tv-{tIdx:06d}.nc", 
                            dict(
                                tv       = (["time", "zc", "yc", "xc"], tv[np.newaxis, :, :]),
                                tempComp = (["time", "zc", "yc", "xc"], tempComp[np.newaxis, :, :]),
                                qvComp   = (["time", "zc", "yc", "xc"], qvComp[np.newaxis, :, :]), 
                                qlComp   = (["time", "zc", "yc", "xc"], qlComp[np.newaxis, :, :])),
                            coords = {'time': np.ones(shape=(1,)), 'zc': zc, 'yc': yc, 'xc': xc})
