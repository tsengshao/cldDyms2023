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
from matplotlib.colors import from_levels_and_colors

if __name__ == "__main__":
    caseNameList = config.caseNameList
    iniTimeIdx, endTimeIdx = 0, 1201
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    hourTimeArange = timeArange*parameter.minPerTimeIdx/(60*24)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    rbCmap = plt.get_cmap("turbo")
    sstArange = np.arange(295, 310.1, 0.1)
    #levels = np.array([0, 10, 50, 100, 500, 1000, 2500, 5000, 10000, 15000, 20000])
    levels = np.arange(0, 0.1, 0.001)
    rbCmap, norm = from_levels_and_colors(levels, [rbCmap(i/len(levels)) for i in range(len(levels))], extend="max")
    
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(15, 7))
    for caseIdx, caseName in enumerate(caseNameList):
        print(caseName)
        vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
        distSST = np.zeros(shape=(len(timeArange), len(sstArange)-1))
        for tIdx in timeArange:
            sst = np.array(vvmLoader.loadSurface(tIdx)["tg"][0])
            distSST[tIdx, :], _ = np.histogram(sst, sstArange)
        distSST /= np.size(distSST)
            
        sstPcolor=axs[caseIdx//2, caseIdx%2].pcolormesh(hourTimeArange, sstArange[:-1], distSST.transpose(), 
                                                        shading='nearest', cmap=rbCmap, norm=norm)
        axs[caseIdx//2, caseIdx%2].grid(True, alpha=0.5)
        axs[caseIdx//2, caseIdx%2].set_ylim(297, 309)
        axs[caseIdx//2, caseIdx%2].set_yticks([298, 300, 302, 304, 306, 308])
        if caseIdx%2 == 0: axs[caseIdx//2, caseIdx%2].set_ylabel("SST [K]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_xlim(0, 50)
        axs[caseIdx//2, caseIdx%2].set_xticks(np.arange(0, 51, 5))
        if caseIdx//2 == 1: axs[caseIdx//2, caseIdx%2].set_xlabel("Time [day]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_title(f"{caseName}", fontsize=15)
        axs[caseIdx//2, caseIdx%2].tick_params(labelsize=15)

    plt.subplots_adjust(left=0.1, right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.1, 0.025, 0.78])
    fig.colorbar(sstPcolor, cax=cbar_ax, extend="max")
    fig.suptitle("SST", fontsize=20)
    plt.savefig(f"SSTevolution-Pcolor.jpg", dpi=250)
    plt.close()
