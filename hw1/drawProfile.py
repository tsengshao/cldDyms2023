import sys
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
sys.path.insert(0, "../")
import config
from util.vvmLoader import VVMLoader
from util.calculator import *
from util.dataWriter import DataWriter
import util.skewt

if __name__ == "__main__":
    tIdx, caseIdx = int(sys.argv[1]), int(sys.argv[2])

    caseNameList = config.caseNameList
    caseName = caseNameList[caseIdx]
    print(f"========== {tIdx:06d}, {caseName} ==========")

    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    pbar = vvmLoader.loadPBAR()[:-1]
    pbar3d = pbar.reshape(pbar.size, 1, 1)
    pibar = vvmLoader.loadPIBAR()[:-1]
    pibar3d = pibar.reshape(pibar.size, 1, 1)
    thData = vvmLoader.loadThermoDynamic(0)
    xc, yc, zc = np.array(thData["xc"]), np.array(thData["yc"]), np.array(thData["zc"]) 
    nx, ny, nz = xc.size, yc.size, zc.size

    thData = vvmLoader.loadThermoDynamic(tIdx)
    th = np.array(thData['th'][0])
    qv = np.array(thData['qv'][0])
    temp = getTemperature(th, pbar3d, pibar3d)
    idxLCL, parcel = parcel_profile_2d(temp[0,:,:],pbar/100, qv[0,:,:], zc)
    CAPE, CIN = cal_CAPE_CIN(temp, parcel, zc)

    fig, ax = util.skewt.draw_skewt()
    pt=[ny//2, nx//10]
    ptCAPE, ptCIN = CAPE[pt[0], pt[1]], CIN[pt[0], pt[1]]
    plt.plot(  temp[:,pt[0], pt[1]]-273.15, pbar/100, '-', lw=2, label='env')
    plt.plot(parcel[:,pt[0], pt[1]]-273.15, pbar/100, '-', lw=2, label='parcel')
    plt.legend()
    plt.title(f'{caseName}\nCAPE:{ptCAPE:.1f}J/kg, CIN:{ptCIN:.1f}J/kg', loc='left',fontsize=15)
    plt.title(f'({pt[0]:d}, {pt[1]:d})\nt={tIdx}', loc='right', fontsize=12)
    plt.yticks(np.arange(100,1001,100), [f'{i:.0f}' for i in np.arange(100,1001,100)])
    plt.xlim(-40,40)
    plt.ylim(1000,100)
    plt.savefig(f'./fig/profile_{caseName}_{tIdx:d}.png',dpi=200)
    plt.show()

    


