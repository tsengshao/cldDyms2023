#!/bin/bash

mpifort -free -O3 $(nc-config --fflags --flibs) cal_sf.F -o sf.out
mpifort -free -O3 $(nc-config --fflags --flibs) cal_sst.F -o sst.out
