******
*grads -a 2 -bcx drawCin.gs
******
'reinit'
'open cin.ctl'
'set display white'
'c'

e=1
while(e<=4)
'set e 'e''

'q dim'
line=sublin(result, 6)
ename=subwrd(line, 6)
say ename
'open /data/mog/rce/rce_walker_'ename'/gs_ctl_files/surface.ctl'

'set xlopts 1 8 0.2'
'set ylopts 1 8 0.2'
'set parea 1.2 10.5 1.5 5'
'set mpt 1 off'
t=1
while(t<=1201)
'c'
'set x 1 512'
'set y 1 128'
'set xlabs 0|256|512|768|1024'
'set ylabs 0|64|128|192|256'
'set grads off'
'set timelab off'
'set t 't
*'color 0 5000 250 -kind white->deepskyblue->mediumseagreen->khaki->orange->tomato -gxout grfill -xcbar 0.7 10 0.7 0.95 -fw 0.15 -fh 0.2 -line off -fskip 2'
'color -300 0 30 -kind blue->skyblue->turquoise->white -gxout grfill -xcbar 1.4 10.7 0.7 0.95 -fw 0.15 -fh 0.2 -line off -fskip 2'
'set gxout grfill'
'd cin'

'set gxout contour'
'set clevs 1'
'set clab off'
'set ccolor 1'
'set cthick 7'
'd sprec.2(e=1,z=1)*3600'

'define c=maskout(cin, cin+300)'
'set x 1'
'set y 1'
'd amean(c,x=1,x=512,y=1,y=128)'
c300=subwrd(result,4)

* 'define cinmean=amean(cin,x=1,x=512,y=1,y=128)'
* 'd cinmean'
* cmean=subwrd(result,4)
*X Limits = 1.2 to 10.5
*Y Limits = 1.86086 to 4.63914
'set string 1 tr 10 0'
'set strsiz 0.2'
'draw string 10.45 4.55 'c300' J/kg'

'draw ylab YC[km]'
'draw xlab XC[km]'
'draw title rce_walker_'ename' / CIN / t='t-1''
'! mkdir -p ./fig/cin/rce_walker_'ename''
'printim ./fig/cin/rce_walker_'ename'/'t'.png x2048 y1024'


t=t+1
endwhile

'close 2'
*ens
e=e+1
endwhile
