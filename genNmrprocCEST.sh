PHASE_x0=-171
PHASE_y0=0.0
NSPEC=$(awk '/yN/{print $4}' fid.com)
# NSPEC=1

rm -rf FT2_spectra UCSF
mkdir UCSF
mkdir FT2_spectra

for ((i=1; i<=$NSPEC; ++i))
do
    echo -ne "Working on $i out of $NSPEC\r"
    cat > nmrprocG.com <<EOF
#!/bin/csh

\$NMRTXT/ext.xz.com fid/test%03d.fid test.fid $i
nmrPipe -in test.fid        \\
| nmrPipe  -fn POLY -time \\
| nmrPipe  -fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5      \\
| nmrPipe  -fn ZF -auto                                 \\
| nmrPipe  -fn FT                                       \\
| nmrPipe  -fn PS -p0 $PHASE_x0  -p1 -0.0 -di              \\
| nmrPipe  -fn POLY -auto                               \\
| nmrPipe  -fn TP                                       \\
| nmrPipe  -fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5      \\
| nmrPipe  -fn ZF -auto                                 \\
| nmrPipe  -fn FT -alt                                      \\
| nmrPipe  -fn PS -p0 $PHASE_y0 -p1 0.0 -di              \\
| nmrPipe  -fn TP                                     \\
#| nmrPipe  -fn EXT -x1 6.0ppm -xn 11.0ppm -sw \\
| nmrPipe  -fn TP                                     \\
   -out FT2_spectra/${i}.ft2 -ov 

sethdr FT2_spectra/${i}.ft2 -ndim 2 -zN 1 -zT 1 -zMODE Real
pipe2ucsf FT2_spectra/$i.ft2 UCSF/$i.ucsf

EOF
    chmod u+x nmrprocG.com
    if ! ./nmrprocG.com ; then
        echo "Failure at plane $i"
        exit 1
    fi
done
echo
rm test.fid
