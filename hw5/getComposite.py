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

def filterAndShiftData(data3D, condition, argCenter):
    data3D = data3D[:, condition, :]
    for i in range(data3D.shape[1]):
        data3D[:, i, :] = np.roll(data3D[:, i, :], int(data3D.shape[2]//2 - argCenter[i]), axis=1)
    return data3D

def getCmapAndNorm(cmapName, levels, extend):
    cmap = plt.get_cmap(cmapName)
    if extend == "both":
        cmap, norm = from_levels_and_colors(levels, [cmap(i/len(levels)) for i in range(len(levels)+1)], extend=extend)
    elif extend == "max":
        cmap, norm = from_levels_and_colors(levels, [cmap(i/len(levels)) for i in range(len(levels))], extend=extend)
    return cmap, norm

if __name__ == "__main__":
    caseName = str(sys.argv[1])
    iniTimeIdx, endTimeIdx = 600, 1201#int(sys.argv[1]), int(sys.argv[2])
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    zz = vvmLoader.loadZZ()[:-1]
    wMin, wMax = 10, 1000
    xStart = 200


    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    #dataWriter = DataWriter(outputPath=f"{config.tvPath}{caseName}/")
    recordArgMaxW = np.load(f"compositeDat/recordArgMaxW-{caseName}.npy")
    recordMaxW = np.load(f"compositeDat/recordMaxW-{caseName}.npy")
    sampleCount = 0
    compositeSumW = np.zeros(shape=(len(zc), len(xc)))
    compositeSumU = np.zeros(shape=(len(zc), len(xc)))
    compositeSumBuoy = np.zeros(shape=(len(zc), len(xc)))
    compositeSumCloud = np.zeros(shape=(len(zc), len(xc)))
    compositeSumQv = np.zeros(shape=(len(zc), len(xc)))
    compositeSumThe = np.zeros(shape=(len(zc), len(xc)))
    for i, tIdx in enumerate(timeArange):
        #if tIdx <= 1190: continue
        print(f"========== {tIdx} =========")
        # thermodyanmic vars
        tdData = vvmLoader.loadThermoDynamic(tIdx)
        qc = np.array(tdData["qc"][0, :, :, :])
        qi = np.array(tdData["qi"][0, :, :, :])
        cloud = np.logical_or(qc>0, qi>1e-4)
        th = np.array(tdData["th"][0, :, :, :])
        qv = np.array(tdData["qv"][0, :, :, :])
        the = th + 2.5e6 * qv / 1004
        # dynamic vars
        dyData = vvmLoader.loadDynamic(tIdx)
        w = np.array(dyData["w"][0])
        u = np.array(dyData["u"][0])
        # buoyancy
        buoyancy = np.array(nc.Dataset(f"{config.buoyancyPath}{caseName}/buoyancy-{tIdx:06d}.nc")["buoyancy"][0])

        argMaxW, maxW = recordArgMaxW[timeArange==tIdx, :][0], recordMaxW[timeArange==tIdx, :][0]
        condition = np.logical_and(np.logical_and(maxW>=wMin, maxW<=wMax), argMaxW!=-1)
        sampleCount += np.sum(condition)
        argMaxW = argMaxW[condition]
        # do filter and shifting
        the = filterAndShiftData(the, condition, argMaxW)
        qv = filterAndShiftData(qv, condition, argMaxW)
        w = filterAndShiftData(w, condition, argMaxW)
        u = filterAndShiftData(u, condition, argMaxW)
        buoyancy = filterAndShiftData(buoyancy, condition, argMaxW)
        cloud = filterAndShiftData(cloud, condition, argMaxW)
        compositeSumThe += np.sum(the, axis=1)
        compositeSumQv += np.sum(qv, axis=1)
        compositeSumW += np.sum(w, axis=1)
        compositeSumU += np.sum(u, axis=1)
        compositeSumBuoy += np.sum(buoyancy, axis=1)
        compositeSumCloud += np.sum(cloud, axis=1)
    print(f"# of Valid Samples: {sampleCount}")
    compositeSumThe   /= sampleCount
    compositeSumQv    /= sampleCount
    compositeSumW     /= sampleCount
    compositeSumU     /= sampleCount
    compositeSumBuoy  /= sampleCount
    compositeSumCloud /= sampleCount
    np.save(f"./compositeDat/compositeSumThe-{caseName}.npy",   compositeSumThe)
    np.save(f"./compositeDat/compositeSumQv-{caseName}.npy",    compositeSumQv)
    np.save(f"./compositeDat/compositeSumW-{caseName}.npy",     compositeSumW)
    np.save(f"./compositeDat/compositeSumU-{caseName}.npy",     compositeSumU)
    np.save(f"./compositeDat/compositeSumBuoy-{caseName}.npy", compositeSumBuoy)
    np.save(f"./compositeDat/compositeSumCloud-{caseName}.npy", compositeSumCloud)
"""
    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(24, 12))
    # w plot
    cmap, norm = getCmapAndNorm("coolwarm", np.linspace(-5, 5, 21), "both")
    plt.sca(axs[0, 0])
    plt.pcolormesh(xc/1e3, zz/1e3, compositeSumW, cmap=cmap, norm=norm)
    plt.colorbar()
    plt.title("Composite W [m/s]", fontsize=15, loc="left")
    # u plot
    cmap, norm = getCmapAndNorm("PiYG", np.linspace(-3, 3, 21), "both")
    plt.sca(axs[0, 1])
    plt.pcolormesh(xc/1e3, zz/1e3, compositeSumU, cmap=cmap, norm=norm)
    plt.colorbar()
    plt.title("Composite U [m/s]", fontsize=15, loc="left")
    # buoyancy plot
    cmap, norm = getCmapAndNorm("coolwarm", np.linspace(-0.05, 0.05, 21), "both")
    plt.sca(axs[1, 0])
    plt.pcolormesh(xc/1e3, zz/1e3, compositeSumBuoy, cmap=cmap, norm=norm)
    plt.colorbar()
    plt.title(r"Composite Buoyancy [$m/s^2$]", fontsize=15, loc="left")
    # theta_e plot
    cmap, norm = getCmapAndNorm("coolwarm", np.arange(330, 361, 2.5), "both")
    plt.sca(axs[1, 1])
    plt.pcolormesh(xc/1e3, zc/1e3, compositeSumThe, cmap=cmap, norm=norm)
    plt.colorbar()
    plt.contour(xc/1e3, zc/1e3, compositeSumQv, colors='cyan', levels=np.arange(5, 36, 5)/1e3)
    plt.title(r"Composite $\Theta_e$ [K] & Qv [kg/kg]", fontsize=15, loc="left")
    #
    for i in range(4):
        plt.sca(axs[i//2, i%2])
        plt.title(f"# of Valid Samples: {sampleCount}", fontsize=15, loc="right")
        plt.ylim(0, 15)
        plt.xlim(xStart, xc.max()/1e3-xStart)
        plt.grid(True)
        plt.contour(xc/1e3, zc/1e3, compositeSumCloud, colors='black', levels=[0.5, 0.75, 1.0], linewidths=1)
        plt.xlabel("XC [km]", fontsize=15)
        plt.ylabel("ZC [km]", fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
    plt.subplots_adjust(left=0.05, right=1.025, top=0.95, bottom=0.05, wspace=0.01)
    plt.savefig(f"composite-{caseName}.jpg", dpi=300)
"""