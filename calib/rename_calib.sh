cd UCSF
nspec=$(ls *[0-9].ucsf | wc -l)  # select only original UCSFs

for ((i = 1; i <= $nspec; ++i))
do
        fq=$(head -${i} ../vdlist | tail -1)
        vc=$(printf "%.4f" $fq)
        echo -ne "$i $vc   \r"
        ln -sf $i.ucsf ${vc}_ppm.ucsf
done
echo
cd ..
