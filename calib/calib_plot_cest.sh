#!/bin/bash

# Script for analysis and plot of CEST data - especially N-CEST

LIST_DIR="$PWD/Sparky/Lists"
NOISE_FILE="$PWD/Sparky/Lists_noise/noise.dat"

OUTPUT_NUM=$(basename $PWD | sed 's/^\([0-9]*\).*/\1/')  # extract experiment number, strip all non-numbers
OUTPUT_PLOT_INTENSITIES="${OUTPUT_NUM}_plot_intensities.ps"

OLD_PWD="$PWD"
cd $LIST_DIR
GNUFILE_INTENSITIES="create_plot_intensities.gnuplot"

##### Start Gnuplot files header ##########
cat > $GNUFILE_INTENSITIES <<EOF
set terminal postscript enhanced color
set output "$OUTPUT_PLOT_INTENSITIES"
set xtics autofreq
set grid
set style line 1 lt 1 lw 2 lc "black"
set xlabel "Time [s]"
set ylabel "Peak Height"
set arrow 1 from graph 0, first 0 to graph 1, first 0 lc "red" lw 0.3 nohead

EOF
#### END Gnuplot file headers ##########

peaklists=$(ls *ppm.list | sort -g)

# get list of all residues
first_spectrum=$(echo $peaklists | awk '{print $1}')
res_list="$(awk 'NR>2{print $1}' $first_spectrum)"
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

    filename_intensity="$res.intensity"
    #echo $filename_intensity

    # extract corresponding lines from all *.list files
    # grep adds the filename before each found line - this contains shift
    grep "$res" $peaklists |  # takes care of K3 vs. K31
        sed 's/:/ /' |         # adds space between filename and rest - column numbers in AWK are shifted by 1
        sed 's/_\S*//' |       # remove rest of filename, leave shift
        awk '{print $1, $7, $8}' > $filename_intensity
    
    shift=$(grep "$res" $first_spectrum |
            awk '{printf("%.3f", $2)}')

    
    cat <<EOF >> $GNUFILE_INTENSITIES
set title "$res on freq $shift ppm"
set arrow 9 from ${shift}, graph 0.8 to ${shift}, graph 0 ls 1
plot "$filename_intensity" u 1:2:3 w yerrorbars pt 7 lc "blue" t "From file: $filename_intensity" noenhanced, \\
     "" u 1:2 w lines lc "black" lw 0.5 notitle
unset arrow 9

EOF
done

echo  # for correct handling after all \r overwritings

gnuplot $GNUFILE_INTENSITIES
cd $OLD_PWD
ln -f $LIST_DIR/$OUTPUT_PLOT_INTENSITIES

