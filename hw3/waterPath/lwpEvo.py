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
    cwvArange = np.arange(0, 0.26, 0.01)
    rbCmap, norm = from_levels_and_colors(cwvArange, [rbCmap(i/len(cwvArange)) for i in range(len(cwvArange))], extend="max")
    
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(15, 7))
    for caseIdx, caseName in enumerate(caseNameList):
        print(caseName)
        vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
        distCWV = np.zeros(shape=(len(timeArange), len(xc)))
        for tIdx in timeArange:
            cwv = np.array(nc.Dataset(f"{config.waterPath}{caseName}/waterPath-{tIdx:06d}.nc")["qcPath"][0])
            yMeanCWV = np.mean(cwv, axis=0)
            distCWV[tIdx, :] = yMeanCWV
            
        cwvPcolor=axs[caseIdx//2, caseIdx%2].pcolormesh(hourTimeArange, xc/1e3, distCWV.transpose(), 
                                                        shading='nearest', cmap=rbCmap, norm=norm)
        axs[caseIdx//2, caseIdx%2].grid(True, alpha=0.5)
        axs[caseIdx//2, caseIdx%2].set_yticks([x for x in range(0, 1025, 256)])
        if caseIdx%2 == 0: axs[caseIdx//2, caseIdx%2].set_ylabel("XC [km]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_xlim(0, 50)
        axs[caseIdx//2, caseIdx%2].set_xticks(np.arange(0, 51, 5))
        if caseIdx//2 == 1: axs[caseIdx//2, caseIdx%2].set_xlabel("Time [day]", fontsize=15)
        axs[caseIdx//2, caseIdx%2].set_title(f"{caseName}", fontsize=15)
        axs[caseIdx//2, caseIdx%2].tick_params(labelsize=15)

    plt.subplots_adjust(left=0.1, right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.1, 0.025, 0.78])
    fig.colorbar(cwvPcolor, cax=cbar_ax, extend="max", ticks=cwvArange[::2])
    fig.suptitle(r"LWP [kg/$m^2$]", fontsize=20)
    plt.savefig(f"LWP-XC.jpg", dpi=250)
    plt.close()
