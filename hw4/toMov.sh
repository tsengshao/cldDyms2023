#!/bin/bash
for caseName in "rce_walker_15k_05m_p3" "rce_walker_15k_1m_p3" "rce_walker_1k_1m_p3" "rce_walker_1k_2m_p3"
do
    ffmpeg -framerate 30 -pattern_type glob -i "$caseName/tv-$caseName-*.jpg" -c:v libx264 -pix_fmt yuv420p $caseName.mp4
done
#ffmpeg -framerate 30 -pattern_type glob -i "cin/cin-*.jpg" -c:v libx264 -pix_fmt yuv420p cin.mp4
