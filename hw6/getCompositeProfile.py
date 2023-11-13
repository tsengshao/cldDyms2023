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

def getProfiles(var, scaleMapCloud):
    profiles = np.zeros(shape=(var.shape[1], var.shape[0]))
    for i in range(var.shape[1]):
        profiles[i, :] = np.sum(var[:, i, :] * scaleMapCloud, axis=(1)) / np.sum(scaleMapCloud, axis=(1))
    return profiles

def getConvMfProfiles(var, scaleMapCloud):
    profiles = np.zeros(shape=(var.shape[1], var.shape[0]))
    for i in range(var.shape[1]):
        profiles[i, :] = np.nansum(var[:, i, :] * scaleMapCloud, axis=(1)) / np.sum(scaleMapCloud, axis=(1))
    return profiles

if __name__ == "__main__":
    caseName, percentage = str(sys.argv[1]), int(sys.argv[2]) / 100
    iniTimeIdx, endTimeIdx = 600, 1201#int(sys.argv[1]), int(sys.argv[2])
    caseNameList = config.caseNameList
    timeArange = np.arange(iniTimeIdx, endTimeIdx, 1)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseNameList[0]}/")
    dyData = vvmLoader.loadDynamic(0)
    xc, yc, zc = np.array(dyData["xc"]), np.array(dyData["yc"]), np.array(dyData["zc"])
    zz = vvmLoader.loadZZ()[:-1]
    rhoz = vvmLoader.loadRHOZ()[:, np.newaxis, np.newaxis]
    wMin, wMax = 10, 1000

    print(caseName)
    vvmLoader = VVMLoader(dataDir=f"{config.vvmPath}{caseName}/")
    recordArgMaxW = np.load(f"../hw5/compositeDat/recordArgMaxW-{caseName}.npy")
    recordMaxW = np.load(f"../hw5/compositeDat/recordMaxW-{caseName}.npy")
    condition = np.logical_and(np.logical_and(recordMaxW>=wMin, recordMaxW<=wMax), recordArgMaxW!=-1)
    sampleCount = np.sum(condition)
    print(sampleCount)
    currentCount = 0
    probOfCloud = np.load(f"../hw5/compositeDat/compositeSumCloud-{caseName}.npy") # sampleCount
    scaleMapCloud = probOfCloud>=percentage

    compositeSumW = np.zeros(shape=(sampleCount, len(zc)))
    compositeSumBuoy = np.zeros(shape=(sampleCount, len(zc)))
    compositeSumConvectMF = np.zeros(shape=(sampleCount, len(zc)))
    compositeSumThe = np.zeros(shape=(sampleCount, len(zc)))

    for i, tIdx in enumerate(timeArange):
        #if tIdx != 1150: continue
        print(f"========== {tIdx} =========")
        # thermodyanmic vars
        tdData = vvmLoader.loadThermoDynamic(tIdx)
        th = np.array(tdData["th"][0, :, :, :])
        qv = np.array(tdData["qv"][0, :, :, :])
        the = th + 2.5e6 * qv / 1004
        # dynamic vars
        dyData = vvmLoader.loadDynamic(tIdx)
        w = np.array(dyData["w"][0])
        # buoyancy
        buoyancy = np.array(nc.Dataset(f"{config.buoyancyPath}{caseName}/buoyancy-{tIdx:06d}.nc")["buoyancy"][0])
        
        argMaxW, maxW = recordArgMaxW[timeArange==tIdx, :][0], recordMaxW[timeArange==tIdx, :][0]
        condition = np.logical_and(np.logical_and(maxW>=wMin, maxW<=wMax), argMaxW!=-1)
        argMaxW = argMaxW[condition]
        # do filter and shifting
        the = filterAndShiftData(the, condition, argMaxW)
        theProfile = getProfiles(the, scaleMapCloud)
        compositeSumThe[currentCount:currentCount+np.sum(condition)] = theProfile
        
        w = filterAndShiftData(w, condition, argMaxW)
        wProfile = getProfiles(w, scaleMapCloud)
        compositeSumW[currentCount:currentCount+np.sum(condition)] = wProfile
        
        convMassFlux = np.ma.masked_array(rhoz * w, w <= 0)
        convMfProfile = getConvMfProfiles(convMassFlux, scaleMapCloud)
        compositeSumConvectMF[currentCount:currentCount+np.sum(condition)] = convMfProfile
        
        buoyancy = filterAndShiftData(buoyancy, condition, argMaxW)
        bProfile = getProfiles(buoyancy, scaleMapCloud)
        compositeSumBuoy[currentCount:currentCount+np.sum(condition)] = bProfile

        currentCount += np.sum(condition)

    np.save(f"./compositeProfile/compositeSumThe-{percentage}-{caseName}.npy",       compositeSumThe)
    np.save(f"./compositeProfile/compositeSumW-{percentage}-{caseName}.npy",         compositeSumW)
    np.save(f"./compositeProfile/compositeSumConvectMF-{percentage}-{caseName}.npy", compositeSumConvectMF)
    np.save(f"./compositeProfile/compositeSumBuoy-{percentage}-{caseName}.npy",      compositeSumBuoy)
