import sys
import numpy as np
import netCDF4 as nc
from matplotlib import cm
sys.path.insert(0, "../")
import config
import parameter
from util.vvmLoader import VVMLoader
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
        meanCWVs = np.zeros(shape=timeArange.shape)
        stdCWVs = np.zeros(shape=timeArange.shape)
        maxCWVs = np.zeros(shape=timeArange.shape)
        for tIdx in timeArange:
            if tIdx % 100 == 0: print(tIdx)
            cwv = np.array(nc.Dataset(f"{config.waterPath}{caseName}/waterPath-{tIdx:06d}.nc")["qiPath"][0])
            cwv = np.ma.masked_array(cwv, cwv<=0)
            meanCWVs[tIdx] = np.mean(cwv)
            stdCWVs[tIdx] = np.std(cwv)
            maxCWVs[tIdx] = np.max(cwv)

        axs[caseIdx//2, caseIdx%2].plot(hourTimeArange, meanCWVs, c='black')
        axs[caseIdx//2, caseIdx%2].plot(hourTimeArange, maxCWVs, c='red')
        axs[caseIdx//2, caseIdx%2].fill_between(hourTimeArange, meanCWVs-stdCWVs, meanCWVs+stdCWVs, alpha=0.5, color="#0095d9")
        axs[caseIdx//2, caseIdx%2].fill_between(hourTimeArange, meanCWVs-2*stdCWVs, meanCWVs+2*stdCWVs, alpha=0.25, color="#0095d9")
        axs[caseIdx//2, caseIdx%2].grid(True)
        axs[caseIdx//2, caseIdx%2].set_ylim(-5, 10)
        axs[caseIdx//2, caseIdx%2].set_yticks([0, 50, 20])
        if caseIdx%2 == 0: axs[caseIdx//2, caseIdx%2].set_ylabel(r"[kg / $m^2$]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_xlim(0, 50)
        axs[caseIdx//2, caseIdx%2].set_xticks(np.arange(0, 51, 5))
        if caseIdx//2 == 1: axs[caseIdx//2, caseIdx%2].set_xlabel("Time [day]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_title(f"{caseName}", fontsize=15)
        axs[caseIdx//2, caseIdx%2].tick_params(labelsize=15)


    fig.suptitle("Ice Water Path [kg / $m^2$]", fontsize=20)
    plt.savefig(f"iwpEvolution.jpg", dpi=250)
    plt.close()
