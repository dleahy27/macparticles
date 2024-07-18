#!/usr/bin/bash
# Variables for file locations
py="./python/"
output_dir="./data"
macparticles="../../macros/Load.C"

main() {
    # Check if directory exists
    if [ ! -d "${output_dir}" ]; then
        mkdir "${output_dir}"
    fi

    # Run configuration
    macparticles Configure.C

    # Run training, reweight and resolutions for each particle
    for particle in ${@}
    do
        macparticles 'RunAcceptanceTraining( ${particle},"training.root","fast_sim" ).C'
        macparticles 'RunReweightTraining( ${particle},"training.root","fast_sim" ).C'
        macparticles 'RunResolutionTraining( ${particle},"training.root","fast_sim" ).C'
    done

    # Run simulation for each particle
    for particle in ${@}
    do
        macparticles 'RunSimulation( "${particle}","${particle}","fast_sim/","results10" ).C'
    done

    # Plotting etc. find a way to get number of entries better
    python3 ./python/master.py pip,pim 1000000
}

# Execute and time above
time main


# Current issues:
# Getting number of events, can pass as an argument similar to particles
# particle names - want to generalise but need pip and pi+, proton and p etc. 
# -> how do I generalise this? Could have a bunch of if statements but that defeats the generalisation
# ^ also applies to master.py and Configure.C
# for master.py file/directories and variables change between proton and p
# Need to generalise Configure.C for each particle