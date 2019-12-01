set encoding iso_8859_1
set title ''
set ylabel 'PSD [dBW/m^2/Hz]'
set xlabel '{/Symbol n} [GHz]'
set yrange [-195:]
set xtics 0.1; set mxtics 10
set ytics 10; set mytics 10
set key top right

#set arrow from graph 0,0.5 to graph 1,0.5 nohead dt 2 lw 2 lc rgb "grey40"


plot 'rfi.txt' u 1:2 t '10 %' w l lw 1.5,\
	'' u 1:3 t '90 %' w l lw 1.5,\
	'' u 1:4 t 'Max' w l lw 1.0 lc 4,\
	'' u 1:5 t 'Med' w l lw 3 lc 7,\
	'' u 1:6 t 'Min' w l lw 1.5 lc 3

set terminal postscript color solid enhanced dl 2.5 lw 2.7 "Helvetica" 21
set output 'RFI_month.ps'
replot 
!./fixbb RFI_month.ps
!mv RFI_month.ps RFI_month.eps
