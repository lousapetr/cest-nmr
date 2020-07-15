sfo=$(awk '/SFO2/{print $2}' acqus) #acqus SFO2
zcar=$(awk '/zCAR/{print $6}' fid.com) # from fid.com by `bruker`
echo "SFO2 = $sfo MHz"
echo "zCAR = $zcar ppm"

shift () {
    # take frequency in Hz as parameter, output value in ppm
    printf "%5.2f" $(echo "$zcar + ($1 / $sfo)" | bc -l)
}

cd UCSF
first_freq=$(head -2 ../fq3list | tail -1)
first_shift=$(echo "$(shift $first_freq) - 5" | bc -l)
ln -fs -- 1.ucsf "${first_shift}_ppm.ucsf"

nspec=$(ls *[0-9].ucsf | wc -l)  # select only original UCSFs
for ((i = 2; i <= $nspec; ++i))
do
    freq=$(head -${i} ../fq3list | tail -1)
    ppm=$(shift $freq)
    # echo -ne "$i $freq $ppm   \r"
    printf "%5d %7d %7.2f\r" $i $freq $ppm
    ln -fs -- $i.ucsf ${ppm}_ppm.ucsf
done
echo
cd ..
