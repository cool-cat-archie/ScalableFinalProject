#!/bin/bash

TRACES=("spec06/473.astar-s0" "spec06/429.mcf-s0" "spec06/450.soplex-s0" "spec06/471.omnetpp-s0" "spec17/623.xalancbmk-s0")

rm -rf results
mkdir results
mkdir results/gen_output

for t in ${TRACES[@]}; do
    SAVE_AS=$(echo $t | cut -d'/' -f 2)
    ./ml_prefetch_sim.py generate ML-DPC/LoadTraces/${t}.txt.xz ${SAVE_AS}.pref --model save_path > results/gen_output/${SAVE_AS}_gen.txt
done

for t in ${TRACES[@]}; do
    SAVE_AS=$(echo $t | cut -d'/' -f 2)
    EXT=$(echo $t | cut -d'/' -f 1)
    if [ "$EXT" == "spec06" ]; then
        ./ml_prefetch_sim.py run ML-DPC/ChampSimTraces/${t}.trace.gz --prefetch ${SAVE_AS}.pref --num-instructions 500 --no-base
    else
        ./ml_prefetch_sim.py run ML-DPC/ChampSimTraces/${t}.trace.xz --prefetch ${SAVE_AS}.pref --num-instructions 500 --no-base
    fi
done
