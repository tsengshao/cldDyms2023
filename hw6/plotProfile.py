import sys
import numpy as np
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import from_levels_and_colors
sys.path.insert(0, "../")
import config
from util.vvmLoader import VVMLoader
from util.dataWriter import DataWriter

if __name__ == "__main__":
    caseName, percentage = str(sys.argv[1]), int(sys.argv[2]) / 100
    iniTimeIdx, endTimeIdx = 600, 1201#int(sys.argv[1]), int(sys.argv[2])
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    zz = vvmLoader.loadZZ()[:-1]
    wMin, wMax = 10, 1000
    xStart = 400

    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    #dataWriter = DataWriter(outputPath=f"{config.tvPath}{caseName}/")
    recordArgMaxW = np.load(f"../hw5/compositeDat/recordArgMaxW-{caseName}.npy")
    recordMaxW = np.load(f"../hw5/compositeDat/recordMaxW-{caseName}.npy")
    condition = np.logical_and(np.logical_and(recordMaxW>=wMin, recordMaxW<=wMax), recordArgMaxW!=-1)
    sampleCount = np.sum(condition)
    print(sampleCount)
    compositeSumThe = np.load(f"./compositeProfile/compositeSumThe-{percentage}-{caseName}.npy")
    compositeSumW = np.load(f"./compositeProfile/compositeSumW-{percentage}-{caseName}.npy")
    compositeSumConvectMF = np.load(f"./compositeProfile/compositeSumConvectMF-{percentage}-{caseName}.npy")
    compositeSumBuoy = np.load(f"./compositeProfile/compositeSumBuoy-{percentage}-{caseName}.npy")
    condition = np.logical_and(np.logical_and(recordMaxW>=wMin, recordMaxW<=wMax), recordArgMaxW!=-1)
    print(f"# of Valid Samples: {sampleCount}")

    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(15, 12))
    # w plot
    plt.sca(axs[0, 0])
    plt.vlines(x=0, ymin=0, ymax=15, color='black')
    plt.plot(np.mean(compositeSumW, axis=(0)), zz/1e3)
    plt.fill_betweenx(zz/1e3, np.min(compositeSumW, axis=(0)), np.max(compositeSumW, axis=(0)), alpha=0.25)
    plt.title("W [m/s]", fontsize=15, loc="left")
    # u plot
    plt.sca(axs[0, 1])
    plt.plot(np.mean(compositeSumThe, axis=(0)), zz/1e3)
    plt.fill_betweenx(zz/1e3, np.min(compositeSumThe, axis=(0)), np.max(compositeSumThe, axis=(0)), alpha=0.25)
    plt.title(r"$\theta_e$ [K]", fontsize=15, loc="left")
    # buoyancy plot
    plt.sca(axs[1, 0])
    plt.vlines(x=0, ymin=0, ymax=15, color='black')
    plt.plot(np.mean(compositeSumBuoy, axis=(0)), zc/1e3)
    plt.fill_betweenx(zz/1e3, np.min(compositeSumBuoy, axis=(0)), np.max(compositeSumBuoy, axis=(0)), alpha=0.25)
    plt.title(r"Buoyancy [$m/s^2$]", fontsize=15, loc="left")
    # theta_e plot
    plt.sca(axs[1, 1])
    plt.vlines(x=0, ymin=0, ymax=15, color='black')
    plt.plot(np.mean(compositeSumConvectMF, axis=(0)), zz/1e3)
    plt.fill_betweenx(zz/1e3, np.min(compositeSumConvectMF, axis=(0)), np.max(compositeSumConvectMF, axis=(0)), alpha=0.25)
    plt.title(r"Convective Mass Flux [$g m^{-2} s^{-1}$]", fontsize=15, loc="left")
    #
    for i in range(4):
        plt.sca(axs[i//2, i%2])
        plt.title(f"# of Valid Samples: {sampleCount}", fontsize=15, loc="right")
        plt.ylim(0, 15)
        plt.grid(True)
        #plt.contour(xc/1e3, zc/1e3, compositeSumCloud, colors='black', levels=[0.25, 0.5, 0.75, 1.0], linewidths=1)
        #plt.xlabel("", fontsize=15)
        plt.ylabel("ZC [km]", fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
    plt.suptitle(f"{caseName} | Probability: {percentage*100}%", fontsize=25)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92)
    plt.savefig(f"composite-{percentage}-{caseName}.jpg", dpi=300)
    #plt.show()
