'reinit'
'open tv.ctl'
'set background 1'
'c'

e=1
'set e 'e''
'q dim'
line=sublin(result, 6)
ename=subwrd(line,6)
say ename
'open /data/mog/rce/rce_walker_'ename'/gs_ctl_files/thermodynamic.ctl'
'open /data/mog/rce/rce_walker_'ename'/gs_ctl_files/dynamic.ctl'

yi=97
'set y 'yi
'set lev 0 2000'
'set x  1 512'
ti=1090
'set t 'ti

'set xlopts 1 5 0.12'
'set ylopts 1 5 0.12'

'set parea 1 10 3 5.125'
'set ylabs 0|0.5|1|1.5|2'
'set xlabs 0|256|512|768|1024'

'color -1 1 0.2 -kind blue->white->orange -gxout grfill'
'd tv.1'
'xcbar 10.2 10.4 3 5.125 -fs 2'

'set gxout stream'
'set strmden 5 0.5 0.05 1'
'set cthick 12'
'set ccolor 15'
'd skip(u.3(e=1),1,1);w.3(e=1)*50'

'set gxout contour'
'set clevs 1e-5'
'set cthick 10'
'set ccolor 1'
'set clab off'
'd qc.2(e=1)'


'set strsiz 0.15'
'set string 1 bl 5'
day = math_format('%.2f',(ti-1)/24)
'draw string 1 5.2 'ename' / t='day'days ('ti-1') / y='yi*2'km'
'draw ylab Z [km]'

'set parea 1 10 0.5 2.625'
'set ylabs 0|0.5|1|1.5|2'
'set xlabs 0|256|512|768|1024'

'a = const(maskout(1, abs(tc)-abs(qvc)), 0, -u)'
'a = a*const(maskout(1, abs(tc)-abs(qlc)), 0, -u)'
'maxtc = maskout(tc, a-0.5)'

'a = const(maskout(1, abs(qvc)-abs(tc)), 0, -u)'
'a = a*const(maskout(1, abs(qvc)-abs(qlc)), 0, -u)'
'maxqvc = maskout(qvc, a-0.5)'

'a = const(maskout(1, abs(qlc)-abs(tc)), 0, -u)'
'a = a*const(maskout(1, abs(qlc)-abs(qvc)), 0, -u)'
'maxqlc = maskout(qlc, a-0.5)'

'color 0 1 0.1 -kind white->red -gxout grfill'
'd abs(maxtc)'
'color 0 1 0.1 -kind white->blue -gxout grfill'
'd abs(maxqlc)'
'color 0 1 0.1 -kind white->green -gxout grfill'
'd abs(maxqvc)'
'xcbar 10.2 10.4 0.5 2.625 -fs 2'

'set gxout contour'
'set clevs 1e-5'
'set cthick 10'
'set ccolor 1'
'set clab off'
'd qc.2(e=1)'

'set gxout shaded'
'set clevs 0'
'set rgb 80 200 200 200 120'
'set ccols -1 80'
'd tv.1'
'set gxout contour'
'set clevs 0'
'set ccols 15'
'd tv.1'

'draw ylab Z [km]'
'printim fig_'ename'_y'yi'_t'ti'.png x1600 y800'


