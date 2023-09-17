'reinit'
'open sfhm.ctl'
'open qvtg.ctl'
'set display white'
'c'

e=1
while(e<=4)
'set e 'e''

'set xlopts 1 8 0.2'
'set ylopts 1 8 0.2'
'set mpt 1 off'
'q dim'
line=sublin(result,6)
ename=subwrd(line,6)

t=1
while(t<=1201)
'c'
'set x 1 512'
'set lev 1000 100'
'set xlabs ||||'
'set grads off'
'set timelab off'
'set t 't

'set parea 1.5 9.5 3 7.5'
'color 310 370 5 -kind deepskyblue->mediumseagreen->khaki->orange->tomato -gxout grfill -xcbar 9.7 10 3 7.5 -fw 0.15 -fh 0.2 -line off -fskip 2'
'd hm.1/1004'

'set gxout contour'
'set cmin 1'
'set cint 5'
'set ccolor 0'
'set cthick 10'
'set clab off'
'd qv.2*1e3'

'set gxout contour'
'set cint 1000'
'set cmax 0'
'set rgb 20 80 80 80'
'set ccolor 20'
'set cthick 10'
'set cstyle 2'
*'set line 1 3 7'
'set clab off'
'd sf.1'

'set cmin 0'
'set cint 1000'
'set ccolor 1'
'set cthick 10'
'set cstyle 1'
'set clab off'
'd sf.1'
'draw ylab Pressure [hPa]'
day = math_format('%.2f',(t-1)/24)
'draw title 'ename' / 'day' days (t='t-1')'


'set z 1'
'set parea 1.5 9.5 1 3'
'set xlabs 0|256|512|768|1024'

'set lwid 13 3.5'

'set cmark 0'
'set cthick 13'
'set ccolor 1'
'set vrange 297 309'
'set ylabs ||299||||303||||307||'
'd tg.2(t=1)'

'set cmark 0'
'set cthick 13'
'set ccolor 4'
'set vrange 297 309'
'set ylabs ||299||||303||||307||'
'd tg.2'

'draw ylab SST [K]'
'draw xlab XC [km]'

'! mkdir -p ./fig/rce_walker_'ename''
'printim ./fig/rce_walker_'ename'/'t-1'.png x1600 y1200'

t = t+1
endwhile

e = e+1
endwhile
