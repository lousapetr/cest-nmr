#!/bin/bash

# Number of Monte Carlo cycles - use 3 or 20 for testing, 2000 for real calculations
MONTE_CARLO=3

# Pick which ones you want to use, by default use all
CREATE_CPMG=1
FIT_DATA=1
COLLECT_RESULTS=1
PLOT_RESULTS=1

# Loop over all data lists
# Create structure of directories within CPMG/
if [ "$CREATE_CPMG" = 1 ]; then
echo "Creating CPMG/ data structure..."
rm -rf CPMG
mkdir CPMG
for f in Lists_ha/[^1][^_]*list
do
    #Extract time and recalculate it to the frequency
    f=$(basename $f | sed 's/.list//')
    # cut fields by underscore (character after -d)
    TIME=$(echo $f | cut -f1 -d_)
    NUMCYC=$(echo $f | cut -f3 -d_)
    EXP=$(echo $f | cut -f4 -d_)
    FREQ=$(printf "%.0f" $(echo "1 / (4*$TIME)" | bc -l))
    TIMET2=$(printf "%.2f" $(echo "$TIME * $NUMCYC * 4" | bc -l))
    # echo ${f}.list $TIME $FREQ $NUMCYC $TIMET2 $EXP
    # continue
 
    mkdir -p CPMG/$FREQ/Lists_ha
    mkdir -p CPMG/$FREQ/Lists_noise
    cp Lists_ha/${f}.list     CPMG/$FREQ/Lists_ha/${TIMET2}_${EXP}.list
    cp Lists_noise/${f}.list  CPMG/$FREQ/Lists_noise/${TIMET2}_${EXP}.list
    for base_file in Lists_ha/1_*list
    do
        base_file=$(basename $base_file | sed 's/.list//')
        # echo $base_file
        base_exp=$(echo $base_file | cut -f4 -d_)
        cp Lists_ha/${base_file}.list    CPMG/$FREQ/Lists_ha/0.0_${base_exp}.list
        cp Lists_noise/${base_file}.list CPMG/$FREQ/Lists_noise/0.0_${base_exp}.list
    done
done
echo "CPMG/ structure completed."
fi  # CREATE_CPMG


# Go through the data in CPMG/ and fit them
if [ "$FIT_DATA" = 1 ]; then
echo "Fitting data..."
echo "Monte carlo cycles: $MONTE_CARLO"
sleep 1
sed -i'.bk' "s/.*\(%.*MONTE_CARLO_MODIFY_HERE\)/monte_carlo_simul=${MONTE_CARLO};  \1/" Octave_empty/exp_fit_noise_ha.m
OLD_PWD=$(pwd)
rm -f octave_stderr.out

for d in CPMG/*
do
    rm -rf $d/Lists_ha/Octave
    cp -r Octave_empty $d/Lists_ha/Octave 
    cd $d/Lists_ha/Octave 
    # pwd
    ./prepare_data_ha.sh
    octave-cli exp_fit_noise_ha.m 2>> "${OLD_PWD}/octave_stderr.out" 
    ./make_graph_ha.sh
    cd "$OLD_PWD"
done
echo "Data fitted."
fi  # FIT_DATA


# Collect results from CPMG/ into results_cpmg.dat
if [ "$COLLECT_RESULTS" = 1 ]; then
echo "Collecting results..."
rm -f results_cpmg.dat
for A in CPMG/*
do
    grep -v "#" $A/Lists_ha/Octave/result_ha_atan.dat |
        grep "[0-9]"  |
        awk -v freq=$(basename $A) '{print freq"\t"$1"\t"$3"\t"$5}' >>  results_cpmg.dat
done
echo "Results collected into results_cpmg.dat"
fi  # COLLECT_RESULTS


# Plot the results
if [ "$PLOT_RESULTS" = 1 ]; then
echo "Plotting results..."
cat > plot_cpmg.gnu << EOF
set output "cpmg_plot.ps" 
set terminal postscript enhanced color
set xlabel "{/Symbol n}_{CPMG} / Hz" 
set ylabel "R_{CPMG} / s^{-1}"
unset key
EOF

data_dir=$(ls CPMG/ | head -1)
aanum_list=$(grep -v "#" CPMG/$data_dir/Lists_ha/Octave/result_ha_atan.dat | grep "[0-9]" | awk '{print $1}')
peaklist=$(ls Lists_ha/*list | head -1)
# echo $peaklist
for aanum in $aanum_list
do
    aa_full=$(grep "[A-Z]$aanum[^0-9]" $peaklist | sed 's/.*\([A-Z][0-9]*\).*/\1/')  # find residue name from its number
    # echo $aanum $aa_full
    echo >> plot_cpmg.gnu
    echo "set title \"Residue $aa_full\" noenhanced" >> plot_cpmg.gnu
    echo "plot \"results_cpmg.dat\" using (\$2==$aanum ? \$1 : 1/0):3:4 w errorbars title \"Residue $aa_full\" noenhanced" >> plot_cpmg.gnu
done
gnuplot plot_cpmg.gnu
echo "Plot cpmg_plot.ps was created."
fi  # PLOT_RESULTS
