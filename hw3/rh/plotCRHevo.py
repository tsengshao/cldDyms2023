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
        meanSSTs = np.zeros(shape=timeArange.shape)
        stdSSTs = np.zeros(shape=timeArange.shape)
        for tIdx in timeArange:
            sst = np.array(vvmLoader.loadSurface(tIdx)["tg"][0])
            meanSSTs[tIdx] = np.mean(sst)
            stdSSTs[tIdx] = np.std(sst)
            
        axs[caseIdx//2, caseIdx%2].plot(hourTimeArange, meanSSTs, color='black')
        axs[caseIdx//2, caseIdx%2].fill_between(hourTimeArange, meanSSTs-stdSSTs, meanSSTs+stdSSTs, alpha=0.5, color="#0095d9")
        axs[caseIdx//2, caseIdx%2].fill_between(hourTimeArange, meanSSTs-2*stdSSTs, meanSSTs+2*stdSSTs, alpha=0.25, color="#0095d9")
        axs[caseIdx//2, caseIdx%2].grid(True)
        axs[caseIdx//2, caseIdx%2].set_ylim(297, 309)
        axs[caseIdx//2, caseIdx%2].set_yticks([298, 300, 302, 304, 306, 308])
        if caseIdx%2 == 0: axs[caseIdx//2, caseIdx%2].set_ylabel("SST [K]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_xlim(0, 50)
        axs[caseIdx//2, caseIdx%2].set_xticks(np.arange(0, 51, 5))
        if caseIdx//2 == 1: axs[caseIdx//2, caseIdx%2].set_xlabel("Time [day]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_title(f"{caseName}", fontsize=15)
        axs[caseIdx//2, caseIdx%2].tick_params(labelsize=15)


        #
    fig.suptitle("SST", fontsize=20)
    plt.savefig(f"SSTevolution.jpg", dpi=250)
    plt.close()
