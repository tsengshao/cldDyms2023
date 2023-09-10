import sys
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
from matplotlib import cm
sys.path.insert(0, "../")
import config
from util.vvmLoader import VVMLoader


if __name__ == "__main__":
    iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])

    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx)
    for tIdx in timeArange:
        print(f"========== {tIdx:06d} ==========")
        fig, ax = plt.subplots(2, 2, figsize=(15, 7))
        for i, caseName in enumerate(caseNameList):
            vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
            thData = vvmLoader.loadThermoDynamic(0)
            xc, yc, zc = np.array(thData["xc"]), np.array(thData["yc"]), np.array(thData["zc"])
            sfData = vvmLoader.loadSurface(tIdx)
            olr = np.array(sfData["olr"][0])
            prec = np.array(sfData["sprec"][0]) * 3600 # mm^3 / m^2 / hr

            cw = plt.get_cmap("coolwarm", 20)
            OLR = ax[i//2, i%2].pcolormesh(xc / 1e3, yc/1e3, olr, cmap="binary", shading="nearest", vmin=100, vmax=280)
            ax[i//2, i%2].pcolormesh(xc / 1e3, yc / 1e3, np.ma.masked_array(prec, prec < 1)>=1, alpha=0.75, cmap='Blues',vmin=0, vmax=2, antialiased=True)
            ax[i//2, i%2].set_title(f"{caseName}", fontsize=15)
            if i // 2 == 1: ax[i//2, i%2].set_xlabel("XC [km]", fontsize=10)
            if i % 2 == 0: ax[i//2, i%2].set_ylabel("YC [km]", fontsize=10)
            
        fig.subplots_adjust(left=0.05, right=1.05)
        fig.colorbar(OLR, extend="both", ax=ax.ravel().tolist())
        fig.suptitle(rf"OLR [W / $m^2$] | Time: {tIdx * config.minPerTimeIdx // 60:04d} hr", fontsize=20)
        plt.savefig(f"./olr-{tIdx:06d}.jpg", dpi=200)
        plt.clf()







