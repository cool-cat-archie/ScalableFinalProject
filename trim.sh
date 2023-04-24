#!/bin/bash

FILE=results/gen_output/${1}
OUT=results/gen_output/${6}
rm $FILE 2> /dev/null
echo "pred gap = ${2} pattern size = ${3} hash count = ${4} barrier count = ${5}" > "${FILE}"
echo '' >> "${FILE}"

for res in ./results/*.txt; do
    echo "$res" >> "$FILE"
    echo $(grep -i 'Finished CPU 0 instructions' ${res}) >> "$FILE"
    echo $(grep -i 'LLC PREFETCH  REQUESTED' ${res}) >> "$FILE"
    echo '' >> "$FILE"
done

zip -r "${OUT}" results/gen_output 