#!/bin/bash

# This version handles spectra where the CEST irradiated nucleus
# is located in the previous (i-1) residue
# Then: CEST profile (in *list) references i-th residue, while
#       belonging to the (i-1)-th residue

LIST_DIR="$PWD/Sparky/Lists"
NOISE_FILE="$PWD/Sparky/Lists_noise/noise.dat"

# standard Sparky peak list - convention X-N-H nuclei, named e.g. G1C-I2N-H
PEAK_LIST="$LIST_DIR/hnco_from128_3D.list"  # only for non-N CEST

OUTPUT_NUM=$(basename $PWD | sed 's/^\([0-9]*\).*/\1/')  # extract experiment number, strip all non-numbers
OUTPUT_PLOT_INTENSITIES="${OUTPUT_NUM}_plot_intensities.ps"
OUTPUT_PLOT_RATIOS="${OUTPUT_NUM}_plot_ratios.ps"

OLD_PWD="$PWD"
cd $LIST_DIR
GNUFILE_INTENSITIES="create_plot_intensities.gnuplot"
GNUFILE_RATIOS="create_plot_ratios.gnuplot"

##### Start Gnuplot files header ##########
cat > $GNUFILE_INTENSITIES <<EOF
set terminal postscript enhanced color
set output "$OUTPUT_PLOT_INTENSITIES"
set xtics 5
set grid
set style line 1 lt 1 lw 2 lc "black"
set xlabel "Chemical Shift [ppm]"
set ylabel "Peak Height"
set arrow 1 from graph 0, first 0 to graph 1, first 0 lc "red" lw 0.3 nohead

EOF

cat > $GNUFILE_RATIOS <<EOF
set terminal postscript enhanced color
set output "$OUTPUT_PLOT_RATIOS"
set xtics autofreq
set grid
set style line 1 lt 1 lw 2 lc "black"
set xlabel "ppm"
set ylabel "Ratio"
set yrange [-0.2:1.2]
set arrow 1 from graph 0, first 0 to graph 1, first 0 lc "red" lw 0.3 nohead
set arrow 2 from graph 0, first 1 to graph 1, first 1 lc "red" lw 0.3 nohead

EOF
#### END Gnuplot file headers ##########

peaklists=$(ls *ppm.list | sort -g)

# get list of all residues
first_spectrum=$(echo $peaklists | awk '{print $1}')
res_list="$(awk 'NR>2{print $1}' $first_spectrum |
    sed -e 's/\([A-Z][0-9]\+\).*/\1/')"  # clean from "N-H" Sparky stuff
nres=$(echo $res_list | wc -w)


# add noise to peaklists, if available
if [ -f "$NOISE_FILE" ]; then
    for f in $peaklists; do
        if grep -q "Noise" $f; then  # if column "Noise" already present, remove it
            # echo "Column 'Noise' found in $peak_list - values were replaced"
            sed -i'.bk' -e '1s/[[:space:]]*Noise$//' \
                -e '3,$s/[[:space:]]*[0-9.]*$//' $f
        fi
        noise=$(awk -v filename=$(basename $f) '$1==filename {printf "%20f", $2}' "$NOISE_FILE")
        # write noise to new column
        sed -i'' -e "1s/$/               Noise/" \
            -e "3,\$s/$/ ${noise}/" $f
    done
fi


for res in $res_list
do
    echo -ne "$res out of $nres peaks \r"

    # extract residue number, pad by zeros - e.g. 003
    resnum=$(echo $res |
             sed 's/[A-Z]//')
    resnum=$(printf "%03d" $resnum)
    #echo $resnum
    filename_intensity="${resnum}_$res.intensity"
    filename_ratio="${resnum}_$res.ratio"
    #echo $filename_intensity $filename_ratio

    # extract corresponding lines from all *.list files
    # grep adds the filename before each found line - this contains shift
    grep "$res[^0-9]" $peaklists |  # takes care of K3 vs. K31
        sed 's/:/ /' |         # adds space between filename and rest - column numbers in AWK are shifted by 1
        sed 's/_\S*//' |       # remove rest of filename, leave shift
        awk '{print $1, $7, $8}' > $filename_intensity
    

    # get correct name
    atom=$(grep "${res}N" "$PEAK_LIST" | sed "s/^\s*\([a-Z0-9]\+\)-${res}N.*$/\1/")

    # get chemical shift from spectrum
    if [ -f "$PEAK_LIST" ]
    then
        # '\b' in grep means word boundary
        shift=$(grep "\b${res}N\b" "$PEAK_LIST" |
                awk '{printf("%.3f", $2)}')
    else
        shift=$(grep "\b$res\b" $first_spectrum |
                awk '{printf("%.3f", $2)}')
    fi
    # if shift not found, use zero
    if [ -z $shift ]; then shift=0; fi
    
    cat <<EOF >> $GNUFILE_INTENSITIES
set title "$atom on freq $shift ppm"
set arrow 9 from ${shift}, graph 0.8 to ${shift}, graph 0 ls 1
plot "$filename_intensity" u 1:2:3 w yerrorbars pt 7 lc "blue" t "From file: $filename_intensity" noenhanced, \\
     "" u 1:2 w lines lc "black" lw 0.5 notitle
unset arrow 9

EOF
########
    
    # create ratios files and plot them
    original_intensity=$(awk 'NR==1 {print $2}' $filename_intensity)
    original_noise=$(awk 'NR==1 {print $3}' $filename_intensity)
    # the relative error of the quotient (after division) equals to the sum of relative errors
    awk -v intensity=$original_intensity -v noise=$original_noise \
        'NR>1 {print $1, $2/intensity, $2/intensity * (noise/intensity + $3/$2)}' \
        $filename_intensity > $filename_ratio
    cat <<EOF >> $GNUFILE_RATIOS
set title "$atom on freq $shift ppm"
set arrow 9 from ${shift}, graph 0.8 to ${shift}, graph 0 ls 1
plot "$filename_ratio" u 1:2:3 w yerrorbars pt 7 lc "blue" t "From file: $filename_ratio" noenhanced, \\
     "" u 1:2 w lines lc "black" lw 0.5 t "Original intensity: $(printf '%.3g' $original_intensity)"
unset arrow 9

EOF
########
done

echo

gnuplot $GNUFILE_INTENSITIES
gnuplot $GNUFILE_RATIOS
cd $OLD_PWD
ln -f $LIST_DIR/$OUTPUT_PLOT_INTENSITIES
ln -f $LIST_DIR/$OUTPUT_PLOT_RATIOS

