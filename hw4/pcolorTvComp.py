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
    iniTimeIdx, endTimeIdx = 1100, 1201
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    hourTimeArange = timeArange*parameter.minPerTimeIdx/(60*24)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    zz = vvmLoader.loadZZ()[:-1]
    cmap = plt.get_cmap("coolwarm")
    levels = np.linspace(-1, 1, 11)
    cmap, norm = from_levels_and_colors(levels, [cmap(i/len(levels)) for i in range(len(levels)+1)], extend="both")
    windCmap = plt.get_cmap("PiYG")
    levels = np.linspace(-0.01, 0.01, 11)
    windCmap, windNorm = from_levels_and_colors(levels, [windCmap(i/len(levels)) for i in range(len(levels)+1)], extend="both")
    reds, blues, greens = plt.get_cmap("Reds", 8), plt.get_cmap("Blues", 8), plt.get_cmap("Greens", 8)
    ySection = yc.max()//2

    for caseIdx, caseName in enumerate(caseNameList):
        print(caseName)
        vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
        #if caseName != "rce_walker_15k_1m_p3": continue
        for tIdx in timeArange:
            print(f"========== {tIdx} =========")
            fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True, sharey=True, figsize=(15, 8))
            thData = vvmLoader.loadThermoDynamic(tIdx)
            qc = np.array(thData["qc"][0])
            qi = np.array(thData["qi"][0])
            cloudPlot = np.logical_or(qc>0, qi>1e-4)[:, np.argmin(np.min(yc-ySection))]
            
            dyData = vvmLoader.loadDynamic(tIdx)
            u = dyData["u"][0, :, np.argmin(np.min(yc-ySection))]
            w = dyData["w"][0, :, np.argmin(np.min(yc-ySection))]


            tvData = nc.Dataset(f"{config.tvPath}{caseName}/tv-{tIdx:06d}.nc")
            tv = np.array(tvData["tv"][0, :, np.argmin(np.min(yc-ySection))])
            tempComp = np.array(tvData["tempComp"][0, :, np.argmin(np.min(yc-ySection))])
            qvComp   = np.array(tvData["qvComp"][0, :, np.argmin(np.min(yc-ySection))])
            qlComp   = np.array(tvData["qlComp"][0, :, np.argmin(np.min(yc-ySection))])
            tvPcolor=axs[0].pcolormesh(xc/1e3, zc/1e3, tv, shading='nearest', cmap=cmap, norm=norm)
            windPlot=axs[0].quiver(xc[::5]/1e3, zz/1e3, u[:, ::5], w[:, ::5]*5, w[:, ::5], cmap=windCmap, norm=windNorm)#, colors='black', linewidths=1, levels=[0.9])
            axs[0].contour(xc/1e3, zc/1e3, cloudPlot, colors='blue', linewidths=1, levels=[0.9])
            cb_ax = fig.add_axes([0.175, 0.55, 0.7, 0.025])
            fig.colorbar(tvPcolor,orientation='horizontal',cax=cb_ax)
            maxVal = np.maximum.reduce([np.abs(tempComp), np.abs(qvComp), np.abs(qlComp)])
            rPlot=axs[1].pcolormesh(xc/1e3, zc/1e3, np.ma.masked_array(np.abs(tempComp), np.abs(tempComp)!=maxVal), shading='nearest', cmap=reds, vmin=0, vmax=2)
            gPlot=axs[1].pcolormesh(xc/1e3, zc/1e3, np.ma.masked_array(np.abs(qvComp), np.abs(qvComp)!=maxVal), shading='nearest', cmap=greens, vmin=0, vmax=2)
            bPlot=axs[1].pcolormesh(xc/1e3, zc/1e3, np.ma.masked_array(np.abs(qlComp), np.abs(qlComp)!=maxVal), shading='nearest', cmap=blues, vmin=0, vmax=2)
            cb_ax = fig.add_axes([0.1, 0.08, 0.25, 0.025])
            cbar=fig.colorbar(rPlot,orientation='horizontal',cax=cb_ax, extend="max")
            cbar.ax.set_title("Temperature [K]")
            cb_ax = fig.add_axes([0.4, 0.08, 0.25, 0.025])
            cbar=fig.colorbar(gPlot,orientation='horizontal',cax=cb_ax, extend="max")
            cbar.ax.set_title("Vapor [K]")
            cb_ax = fig.add_axes([0.7, 0.08, 0.25, 0.025])
            cbar=fig.colorbar(bPlot,orientation='horizontal',cax=cb_ax, extend="max")
            cbar.ax.set_title("Condensation [K]")
            axs[1].contourf(xc/1e3, zc/1e3, np.ma.masked_array(tv, tv>=0), hatches="/////", colors='none')
            axs[1].contour(xc/1e3, zc/1e3, cloudPlot, colors='blue', linewidths=1, levels=[0.9])
            axs[0].set_ylabel("ZC [km]", fontsize=15)
            axs[1].set_ylabel("ZC [km]", fontsize=15)
            axs[1].set_xlabel("XC [km]", fontsize=15)
            axs[0].set_title(f"", fontsize=15)

            for i in range(2):
                axs[i%2].grid(True, alpha=0.5)
                axs[i%2].set_ylim(0, 2)
                axs[i%2].set_xticks(np.linspace(0, 1024, 5))
                axs[i%2].tick_params(labelsize=15)

            plt.subplots_adjust(left=0.1, right=0.95, bottom=0.2, hspace=0.5)
            fig.suptitle(fr"$T_v$ and components [K] | {caseName} | Time: {tIdx:06d} hr", fontsize=20)
            plt.savefig(f"{caseName}/tv-{caseName}-{tIdx:06d}.jpg", dpi=250)
            plt.close()
