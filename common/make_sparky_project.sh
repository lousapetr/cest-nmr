#!/bin/bash

NAME1=$(ls Sparky/Save | head -1 | sed 's/\.save//')

NAMEPROJ=project.proj
cat > Sparky/Projects/$NAMEPROJ << EOF
<sparky project file>
<version 3.115>
<savefiles>
../Save/$NAME1.save
EOF

for f in UCSF/*ucsf
do
    if [ "$f" == "$NAME1" ]; then
        continue
    fi
    NAME2=$(echo $f | sed 's/\.ucsf//')
    sed -e "s/$NAME1/$NAME2/" Sparky/Save/$NAME1.save |
        sed -e 's/flags/flags hidden/' \
        > Sparky/Save/$NAME2.save
    echo "../Save/$NAME2.save" >> Sparky/Projects/ $NAMEPROJ
done

echo "WARNING! After running Sparky, only first spectrum is visible."
echo "         Others are hidden. If you want to see them, run 'PV' command"

cat >> Sparky/Projects/$NAMEPROJ << EOF
<end savefiles>
<options>
<end options>
<overlays>
<end overlays>
<attached data>
<end attached data>
<molecule>
name
<attached data>
<end attached data>
<condition>
name
<resonances>
<end resonances>
<end condition>
<end molecule>
EOF
