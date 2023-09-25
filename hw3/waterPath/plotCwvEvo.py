import sys
import numpy as np
import netCDF4 as nc
from matplotlib import cm
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
        meanCWVs = np.zeros(shape=timeArange.shape)
        stdCWVs = np.zeros(shape=timeArange.shape)
        maxCWVs = np.zeros(shape=timeArange.shape)
        dataWriter = DataWriter(outputPath=f"{cwvPa}{caseName}/")
        for tIdx in timeArange:
            cwv = np.sum(np.array(vvmLoader.loadThermoDynamic(tIdx)["qv"][0]) * rho * deltaZZ, axis=0)
            meanCWVs[tIdx] = np.mean(cwv)
            stdCWVs[tIdx] = np.std(cwv)

        axs[caseIdx//2, caseIdx%2].plot(hourTimeArange, meanCWVs, c='black')    
        axs[caseIdx//2, caseIdx%2].fill_between(hourTimeArange, meanCWVs-stdCWVs, meanCWVs+stdCWVs, alpha=0.5, color="#0095d9")
        axs[caseIdx//2, caseIdx%2].fill_between(hourTimeArange, meanCWVs-2*stdCWVs, meanCWVs+2*stdCWVs, alpha=0.25, color="#0095d9")
        axs[caseIdx//2, caseIdx%2].grid(True)
        axs[caseIdx//2, caseIdx%2].set_ylim(-20, 110)
        axs[caseIdx//2, caseIdx%2].set_yticks([0, 50, 100])
        if caseIdx%2 == 0: axs[caseIdx//2, caseIdx%2].set_ylabel(r"[kg / $m^2$]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_xlim(0, 50)
        axs[caseIdx//2, caseIdx%2].set_xticks(np.arange(0, 51, 5))
        if caseIdx//2 == 1: axs[caseIdx//2, caseIdx%2].set_xlabel("Time [day]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_title(f"{caseName}", fontsize=15)
        axs[caseIdx//2, caseIdx%2].tick_params(labelsize=15)


    fig.suptitle("Precipitable Water [kg / $m^2$]", fontsize=20)
    plt.savefig(f"cwvEvolution.jpg", dpi=250)
    plt.close()
