#!/bin/bash

#for dir in olrprec;do
for exp in rce_walker_15k_05m_p3  rce_walker_15k_1m_p3  rce_walker_1k_1m_p3  rce_walker_1k_2m_p3;do
  ffmpeg -r 12 -f image2 -i ${exp}/%d.png -vcodec libx264 -pix_fmt yuv420p hw2.${exp}.mp4
done
#done
