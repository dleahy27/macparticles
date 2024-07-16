#!/usr/bin/bash
# Bash script to set up all the data files needed for GlueX fast sim
main () {
    # Variables for file locations
    # Will need to change gluexrun for personal location
    gluexrun="/home/dillon/Desktop/intern24/gluexrun"
    py="./python/"
    output_dir = "./data"

    # Get specific command line args that are always needed
    # Input file locations for the _s and _r APIs
    while getopts r:s:o: flag
    do
        case "${flag}" in
            r) recon_in=${OPTARG};;
            s) sim_in=${OPTARG};;
        esac
    done

    # Check if directory exists
    if [ ! -d "${output_dir}" ]; then
        mkdir "${output_dir}"
    fi

    # Shift past the flags
    shift 2

    # Any other argument is designated to be a particle name
    for particle in ${@}
    do
        output_name="${output_dir}/${particle}"

        ${gluexrun} python2 ${py}Hddm_rToRoot.py ${recon_in} ${output_name} ${particle}
        echo "All ${particle} files converted, now merging them into one file"

        hadd -f "${output_name}_training.root" "${output_name}_"*"_tmp.root" > /dev/null 2>&1

        echo "All ${particle} files merged, now removing interim files."

        rm "${output_name}_"*"_tmp.root"

        # Only here as I need local python to see plots
        # Handles filters/additions of new data
        # Can comment out if not needed
        #python3 ${py}DataFrame.py ${output_name}_training.root particle

        echo "All reconstructed files converted."

    done

    # Convert simulation data 
    ${gluexrun} python2 ${py}Hddm_sToRoot.py ${sim_in} ./gluex_reaction
}
# Call function with time to see program run time
time main

