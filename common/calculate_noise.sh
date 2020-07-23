#!/bin/bash

NOISE_PATH="Sparky/Lists_noise"
NOISE_FILE="${NOISE_PATH}/noise.dat"

echo "The result will be saved to ${NOISE_FILE}"

rm -f "$NOISE_FILE"

for f in "${NOISE_PATH}"/*list
do
    echo "$(basename $f) $(octave << EOF
        data = load("$f")(:,3);
        printf ("%20f\n", std(data));
EOF
    )" >> "${NOISE_FILE}" &
done
wait  # wait until all background processes finish
