#!/bin/bash
#for caseName in "rce_walker_15k_05m_p3" "rce_walker_15k_1m_p3" "rce_walker_1k_2m_p3" "rce_walker_1k_1m_p3"
fileName=plotComposite.py
python $fileName "rce_walker_15k_05m_p3" &
python $fileName "rce_walker_15k_1m_p3"  &
python $fileName "rce_walker_1k_2m_p3"   &
python $fileName "rce_walker_1k_1m_p3" 
