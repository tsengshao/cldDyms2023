'reinit'
ename.1="15k_05m_p3"
ename.2="15k_1m_p3"
ename.3="1k_1m_p3"
ename.4="1k_2m_p3"
e = 1
while(e<=4)
'open /data/mog/rce/rce_walker_'ename.e'/gs_ctl_files/surface.ctl'
'set display white'
'c'
'set xlopts 1 8 0.2'
'set ylopts 1 8 0.2'
'set parea 1.2 10.5 1.5 5'
'set mpt 1 off'
t=1
while(t<=1201)
'c'
'set t 't
'set x 1 512'
'set y 1 128'
'set xlabs 0|256|512|768|1024'
'set ylabs 0|64|128|192|256'
'set grads off'
'set timelab off'
'color 100 300 25 -kind white->(50,50,50) -gxout grfill -xcbar 5.8 9.5 0.7 0.95 -fw 0.15 -fh 0.2 -line off -fskip 2'
'd olr'
'set string 1 l 10 0'
'set strsiz 0.15'
'draw string 9.6 0.95 OLR'
'draw string 9.6 0.65 [W/m2]'
'color -levs 1 5 10 20 30 40 50 -gxout grfill -kind (255,255,255,0)->deepskyblue->olivedrab->khaki->darkorange -xcbar 0.7 4.7 0.7 0.95 -fw 0.15 -fh 0.2 -line off -fskip 1'
'd sprec*3600'
'set string 1 l 10 0'
'set strsiz 0.15'
'draw string  4.8 0.95 Rain'
'draw string  4.8 0.65 [mm/hr]'
'set gxout contour'
'set clab off'
'set clevs 150'
'set ccolor 1'
'set cthick 7'
'd olr'
'draw ylab YC[km]'
'draw xlab XC[km]'
'draw title rce_walker_'ename.e' / t='t-1''
'! mkdir -p ./fig/olrprec/rce_walker_'ename.e''
'printim ./fig/olrprec/rce_walker_'ename.e'/'t'.png x2048 y1024 white'
t=t+1
endwhile
'close 1'
e=e+1
endwhile
