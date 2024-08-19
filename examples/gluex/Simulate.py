# Python script to handle Macparticles simulation
# Import and define constants
import os 
import sys
import time

py = "./python/"
macparticles = "root -q ../../macros/Load.C" 

def Simulate(particles,simparticles):
    # Simulate for each particle
    for i in range(len(particles)):
        os.system(f"""{macparticles} 'RunSimulation.C( "{particles[i]}", "{simparticles[i]}", {str(i)} )'""")
        i += 1

if __name__ == '__main__':
    # Execute program
    start_time = time.time()
    
    Simulate(sys.argv[1].split(','), sys.argv[2].split(','))
         
    remaining = (time.time() - start_time)         
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    print(f"Simlulation complete - total simulation runtime of {int(hours)}:{int(mins)}:{round(secs,2)}. Converting data into RAD format.")
    
    # Compile all data into RAD format
    start_time = time.time()

    os.system(f"python3 ./python/master.py {sys.argv[2]} {sys.argv[1]} {sys.argv[3]}")
    
    remaining = (time.time() - start_time)         
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    print(f"Conversion complete - total RAD conversion runtime of {int(hours)}:{int(mins)}:{round(secs,2)}.")
    
    