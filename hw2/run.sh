#!/bin/bash

clist=$(grep -irw ../config.py -e "caseNameList"|cut -d= -f2)
clist=${clist//,/}
clist=${clist//[/}
clist=${clist//]/}
clist=${clist//\"/}

for exp in ${clist};do
mkdir -p /data/C.shaoyu/CD2023/dat/vvmYmean/qvtg/${exp}
echo ${exp}
#time mpiexec -np 12 ./sf.out ${exp}
time mpiexec -np 1 ./sst.out ${exp}
done
