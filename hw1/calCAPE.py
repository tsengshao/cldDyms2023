import sys
import numpy as np
sys.path.insert(0, "../")
import config
from util.vvmLoader import VVMLoader
from util.calculator import *
from util.dataWriter import DataWriter


if __name__ == "__main__":
    iniTimeIdx, endTimeIdx = int(sys.argv[1]), int(sys.argv[2])

    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx)
    for tIdx in timeArange:
        print(f"========== {tIdx:06d} ==========")
        #fig, ax = plt.subplots(2, 2, figsize=(15, 7))
        for i, caseName in enumerate(caseNameList):
            outputPath = f"{config.capecinPath}"
            dataWriter = DataWriter(outputPath = outputPath+f'{caseName}/')
            #print(dataWriter.outputPath)
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
            dataWriter.toNC(f"cape-{tIdx:06d}.nc", CAPE[np.newaxis, :, :], 
                            coords = {'time': np.ones(shape=(1,)),  'yc': yc, 'xc': xc}, 
                            dims = ['time', 'yc', 'xc'], 
                            varName = 'cape')
            dataWriter.toNC(f"cin-{tIdx:06d}.nc", CIN[np.newaxis, :, :], 
                            coords = {'time': np.ones(shape=(1,)),  'yc': yc, 'xc': xc}, 
                            dims = ['time', 'yc', 'xc'], 
                            varName = 'cin')

            #print(CAPE[ny//2,nx//10], CIN[ny//2,nx//10])
            #sys.exit()

