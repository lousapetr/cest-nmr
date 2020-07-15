#!/usr/bin/env gnuplot

Fset = 45
fit_filename = 'calib_fits.dat'

set terminal postscript enhanced color size 7,7
directory = system('basename $(pwd)')
set output sprintf("%s_calib_fit_linear.ps", directory)
set title sprintf("Calibration for Cb - %s", directory)

#set xtics 5
set mxtics 5
set mytics 5
set tics nomirror
#set grid
set key left top
set xlabel "Set values [Hz]"
set ylabel "Measured values [Hz]"

set style line 1 lt 1 lw 2 lc "black"

f(x) = a*x + b
fit f(x) fit_filename using 1:2:3 yerrors via a,b
fin=f(Fset)

set label sprintf("y = %.3fx %+-.3f", a, b) at graph 0.2, graph 0.8

set xrange [0:350]
set yrange [0:350]
set arrow from Fset, graph 0 to Fset, fin nohead
set arrow from Fset, fin to 0, fin
plot f(x) lc "red" title sprintf(" Exp at %.0f = %.3f", Fset, fin), \
    fit_filename u 1:2:3 pt 1 lc 'black' w yerr t "exp"


