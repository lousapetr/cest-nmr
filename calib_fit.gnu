#!/usr/bin/env gnuplot

filename = 'Sparky/Lists/1XC-H.intensity'
directory = system('basename $(pwd)')
set output sprintf("%s_calib_fit.ps", directory)

set terminal postscript enhanced color #size 7,7
# set grid
set xlabel "Time [s]"
set ylabel "Intensity"
set style line 1 lt 1 lw 2 lc "black"
set samples 1000
set xtics nomirror
set ytics nomirror

amplitude = 1.8e6
freq = 200
phase = 1.7
decay = 45
constant = 1000

f(x) = amplitude * sin(2.0*pi*freq*x - phase*pi/2) * exp(-decay*x) + constant

fit f(x) filename using 1:2:3 yerrors via amplitude, freq, phase, decay, constant 
set multiplot layout 2,1
plot filename u 1:2:3  w errorbars lc "black" t sprintf("Data - %s", filename) ,\
    f(x) lc "red" title sprintf("f = %.3f Hz", freq)
set ylabel "Residual intensity"
plot filename u 1:($2-f($1)):3 w errorbars lc 'black' t 'residuals',\
     '' u 1:($2-f($1)) w lines lc 'black' notitle,\
    0 lc 'red' notitle
