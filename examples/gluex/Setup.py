# Python script to set up all the data files needed for GlueX fast sim
# Importing modules and defining file location variables
# /w/work2/home/dariusd/etaphi/data/fastsim/work/test-xrootd/gluex/mcwrap/REQUESTEDMC_OUTPUT/phi_eta_gg_2019_11_M17_030524_dariusd_3769/hddm/
import os 
import sys
import time
import glob 

# Will need to change gluexrun for personal location
gluexrun = "/home/dillon/Desktop/intern24/gluexrun"
py = "./python/"
output_dir = "./data"

def Setup(recon_in, sim_in, particles, Pdg_names, decay_names):
    
    # Check if data file exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Make Config_Hddm.C file for the particles wanted
    
    # Read in HDDM files for each particle
    for particle in particles:
        print(f"Converting {particle} files.")
        output_name = os.path.join(output_dir,particle)

        # Convert
        os.system(f"""{gluexrun} python2 {py}Hddm_rToRoot.py {recon_in} {output_name} {particle}""")
        print(f"All {particle} files converted, now merging them into one file")

        # Merge
        os.system(f"""hadd -f "{output_name}_training.root" "{output_name}_"*"_tmp.root" > /dev/null 2>&1""")
        print(f"All {particle} files merged, now removing interim files.")

        # Remove
        os.system(f"""rm "{output_name}_"*"_tmp.root" """)
        print("All reconstructed files converted.")
    
    print("Converting simulation files.")
    
    in_reaction_names = glob.glob(sim_in+"*.hddm")
    out_reaction_name = os.path.join(output_dir,"gluex_reaction")
    for i in range(len(in_reaction_names)):
        # Convert
        os.system(f"""{gluexrun} python2 {py}Hddm_sToRoot.py {in_reaction_names[i]} {out_reaction_name}_{i}_tmp {Pdg_names} {decay_names}""")
        
    print(f"All reaction files converted, now merging them into one file")

    # Merge
    os.system(f"""hadd -f "{out_reaction_name}.root" "{out_reaction_name}_"*"_tmp.root" > /dev/null 2>&1""")
    print(f"All reaction files merged, now removing interim files.")

    # Remove
    os.system(f"""rm "{out_reaction_name}_"*"_tmp.root" """)
    print("All reaction files converted.")

        
if __name__ == '__main__':
    # Execute program
    start_time = time.time()
    Setup(sys.argv[1], sys.argv[2], sys.argv[3].split(','), sys.argv[4], sys.argv[5])
    
    # Print out script run time
    remaining = (time.time() - start_time)         
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    print(f"Total runtime - {int(hours)}:{int(mins)}:{round(secs,2)}")