'reinit'
*type='up'
type='down'
*case='15k_1m_p3'
case='15k_05m_p3'

'open /data/C.shaoyu/CD2023/dat/vvmProperties/conCom/rce_walker_'case'/'type'draft_3km.ctl'
'set background 1'
'c'

e=1
while(e<=6)
'c'
'set e 'e''
'q dim'
line=sublin(result, 6)
ename=subwrd(line, 6)

'set z 1 45'
'set x 1'
'define bum=mean(bu, x=1, x=512)'
'define thm=mean(th, x=1, x=512)'
'define qvm=mean(qv, x=1, x=512)'

'set parea 1 9.7 3 8'
'set xlopts 1 10 0.15'
'set ylopts 1 10 0.15'

'set x 1 512'
'set x '256-96' '256+96''
'set x '256-24' '256+24''
'set lev 0 14000'
'set ylabs 0km|2km|4km|6km|8km|10km|12km|14km'
'set xlab off'


'color -0.015 0.015 0.002 -kind blue->white->red -gxout grfill'
'd bu-bum'
'xcbar 9.8 10.1 3 8 -fs 5'

'set gxout shaded'
'set clevs 1e-4'
'set rgb 80 200 200 200 200'
'set ccols -1 80'
'd qi'


'set gxout vector'
len = 0.3
scale = 2
xrit = 9
ybot = 2.5
'set arrscl 'len' 'scale
'set arrlab off'
'set ccolor 1'
*'d u;v'
'd maskout(u,mag(u,w)-0.2);w'
rc = arrow(xrit-0.25,ybot+0.2,len,scale)

'set gxout contour'
'set cthick 10'
'set clab off'
'set ccolor 1'
'set clevs 1e-5'
'd qc'

'draw title 'ename

'set parea 1 9.7 1 3'
'set xlab on'
*'set xlabs 0|256km|512km|768km|1024km'
'set xlabs -192km|-96km|0|96km|192km'
'set xlabs -96km|48km|0|48km|96km'
'set xlabs -48km|24km|0|24km|48km'

'set z 1'
'set cmark 0'
'set cthick 10'
'set ccolor 1'
'set vrange 0 5'
'set ylabs 0|1|2|3|4|'
'd rain'

'set strsiz 0.2'
'set string 1 tl 10'
'set strsiz 0.2'
'draw string 1.2 2.8 Rain [mm hr`a-1`n]'

'set x 1'
'set y 1'
'set z 1'
'd num'
num=subwrd(result, 4)
'set string 1 br 10'
'draw string 9.7 8.1 'num

'printim fig/'case'_'type''e'.png white x1600 y1200'

e=e+1
endwhile

function arrow(x,y,len,scale)
'set line 1 1 10'
'draw line 'x-len/2.' 'y' 'x+len/2.' 'y
'draw line 'x+len/2.-0.05' 'y+0.025' 'x+len/2.' 'y
'draw line 'x+len/2.-0.05' 'y-0.025' 'x+len/2.' 'y
'set string 1 c 10'
'set strsiz 0.15'
'draw string 'x' 'y-0.2' 'scale' m/s'
return


