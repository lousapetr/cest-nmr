for f in ../18[678]_proc  # propagate all parameters
do
    f=${f}/fit.log
    echo -n "$f "
    grep '^freq.*+/-' $f |
        tail -1 |
        awk '{print $3, $5}' 
done > calib_fits.dat

echo "Open calib_fits.dat and change filenames to the set frequencies in Hz!"
