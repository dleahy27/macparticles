#!/usr/bin/bash
# Variables for file locations
py="./python/"
macparticles="../../macros/Load.C"

main() {
    # Run configuration
    macparticles Configure.C

    # Run training, reweight and resolutions for each particle
    # Edit Training, no need for some command line arguments
    # Keeps program more consistent
    for particle in ${@}
    do
        macparticles 'RunAcceptanceTraining( ${particle} ).C'
        macparticles 'RunReweightTraining( ${particle} ).C'
        macparticles 'RunResolutionTraining( ${particle} ).C'
    done

    # Run simulation for each particle
    i=0
    for particle in ${@}
    do
        macparticles 'RunSimulation( "${particle}","${particle}",${i} ).C'
        ((i+=1))
    done

    # Plotting etc. find a way to get number of entries better
    python3 ./python/master.py ${@}
}

# Execute and time above
time main


# Current issues:
# particle names - want to generalise but need pip and pi+, proton and p etc. 
# -> how do I generalise this? Could have a bunch of if statements but that defeats the generalisation
# ^ also applies to Configure.C
# Need to generalise Configure.C for each particle
# Could always make Configure.C be manually edited