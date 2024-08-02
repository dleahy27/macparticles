# Python script to set up all the data files needed for GlueX fast sim
# Importing modules and defining file location variables
import os 
import sys
import time 

# Will need to change gluexrun for personal location
gluexrun = "/home/dillon/Desktop/intern24/gluexrun"
py = "./python/"
output_dir = "./data"

def Setup(recon_in, sim_in, particles, Pdg_names):
    
    # Check if data file exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read in HDDM files for each particle
    for particle in particles:
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
    os.system(f"""{gluexrun} python2 {py}Hddm_sToRoot.py {sim_in} {Pdg_names}""")
    print("All reaction files converted.")

        
if __name__ == '__main__':
    # Execute program
    start_time = time.time()
    Setup(sys.argv[1], sys.argv[2], sys.argv[3].split(','), sys.argv[4])
    
    # Print out script run time
    remaining = (time() - start_time)         
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    time_str = str(f"""Total runtime - int(hours))+":"+str(int(mins))+":"+str(round(secs,2)""")
    print(time_str)