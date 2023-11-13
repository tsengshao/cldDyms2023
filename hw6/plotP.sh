#!/bin/bash
#for caseName in "rce_walker_15k_05m_p3" "rce_walker_15k_1m_p3" "rce_walker_1k_2m_p3" "rce_walker_1k_1m_p3"
fileName=plotProfile.py

python $fileName "rce_walker_15k_05m_p3" 75 &
python $fileName "rce_walker_15k_1m_p3" 75 &
python $fileName "rce_walker_1k_2m_p3" 75  &
python $fileName "rce_walker_1k_1m_p3" 75

python $fileName "rce_walker_15k_05m_p3" 50 &
python $fileName "rce_walker_15k_1m_p3" 50 &
python $fileName "rce_walker_1k_2m_p3" 50 &
python $fileName "rce_walker_1k_1m_p3" 50

python $fileName "rce_walker_15k_05m_p3" 25 &
python $fileName "rce_walker_15k_1m_p3" 25 &
python $fileName "rce_walker_1k_2m_p3" 25  &
python $fileName "rce_walker_1k_1m_p3" 25

