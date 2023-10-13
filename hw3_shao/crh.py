import numpy as np
from netCDF4 import Dataset
import sys
sys.path.insert(0, "../")
import config
import matplotlib.pyplot as plt

if __name__ == "__main__":
  caseNameList = config.caseNameList
  iniTimeIdx, endTimeIdx = 0, 1201
  arr_mean = np.zeros((4, 1201))
  arr_var  = np.zeros((4, 1201))
  for icase in range(len(caseNameList)):
    caseName = caseNameList[icase]
    for it in np.arange(iniTimeIdx, endTimeIdx):
      if(it%100==0): print(icase, caseName, it)
      path = config.waterPath+caseName+'/colRH-%06d.nc'%it
      nc = Dataset(path, 'r')
      crh = nc.variables['columnRH'][0,:,:]
      arr_mean[icase, it] = crh.mean()
      arr_var[icase, it] = crh.var()
 
  np.savez('crh', var=arr_var, mean=arr_mean, caseNameList=caseNameList)  
        
      
