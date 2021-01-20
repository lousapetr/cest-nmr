sfo=$(awk '/SFO2/{print $2}' acqus) #acqus SFO2
zcar=$(awk '/zCAR/{print $6}' fid.com) # from fid.com by `bruker`
echo "SFO2 = $sfo MHz"
echo "zCAR = $zcar ppm"

shift () {
    # take frequency in Hz as parameter, output value in ppm
    printf "%5.2f" $(echo "$zcar + ($1 / $sfo)" | bc -l)
}

cd UCSF
echo '' > ../freq2shift.txt
# first_freq=$(head -2 ../fq3list | tail -1)
# first_shift=$(echo "$(shift $first_freq) - 5" | bc -l)
# ln -fs -- 1.ucsf "${first_shift}_ppm.ucsf"

for ((i = 1; i <= $(cat ../fq3list | wc -l); ++i))
do
    freq=$(head -${i} ../fq3list | tail -1)
    ppm=$(printf "%.2f%03d" $(shift $freq) $i)  # creates shifts in form of XX.XX001, YY.YY002, necessary for later identification
    # echo -ne "$i $freq $ppm   \r"
    new_name="${ppm}_ppm.ucsf"
    echo "$ppm $freq " >> freq2shift.txt
    printf "%5d.ucsf -> %20s\r" $i $new_name
    ln -fs -- $i.ucsf "$new_name"
done
cd ..
echo "Reference spectrum: $(ls UCSF/*001_ppm*)"
