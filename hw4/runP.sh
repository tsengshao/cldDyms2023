#!/bin/bash

filename=calTv.py
python ${filename} 0 200 &
python ${filename} 200 400 &
python ${filename} 400 600 &
python ${filename} 600 800 &
python ${filename} 800 1000 &
python ${filename} 1000 1201

