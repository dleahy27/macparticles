# Python script to handle Macparticles training and simulation
# Import and define constants
import os 
import sys
import time

py = "./python/"
macparticles = "root -q ../../macros/Load.C" 

def Simulate(particles,simparticles,resparticles=True):
    
    # Run Configure file --- Must be edited manually first!!!!
    os.system(macparticles+" 'Configure.C'")
    
    # Train for each particle
    for i in range(len(particles)):
        if i == 0:
            continue
        if resparticles:
            os.system(f"""{macparticles} 'RunAcceptanceTraining.C( "{particles[i]}" )'""")
            os.system(f"""{macparticles} 'RunReweightTraining.C( "{particles[i]}" )'""")
            os.system(f"""{macparticles} 'RunResolutionTraining.C( "{particles[i]}" )'""")
        else:
            os.system(f"""{macparticles} 'RunAcceptanceTraining.C( "{particles[i]}", "{resparticles[i]}" )'""")
            os.system(f"""{macparticles} 'RunReweightTraining.C( "{particles[i]}", "{resparticles[i]}" )'""")
            os.system(f"""{macparticles} 'RunResolutionTraining.C( "{particles[i]}", "{resparticles[i]}" )'""")
            
        i += 1
    
    # Simulate for each particle
    for i in range(len(particles)):
        if i == 0:
            continue
        os.system(f"""{macparticles} 'RunSimulation.C( "{particles[i]}", "{simparticles[i]}", {str(i)} )'""")
        i += 1
        
    # Compile all data into RAD format
    os.system(f"python3 ./python/master.py {sys.argv[3]} {sys.argv[1]}")

if __name__ == '__main__':
    # Execute program
    start_time = time.time()
    
    if len(sys.argv) > 2:
        Simulate(sys.argv[1].split(','), sys.argv[2].split(','), sys.argv[3].split(','))
    else:
        Simulate(sys.argv[1].split(','), sys.argv[2].split(','))
         
    # Print out script run time
    remaining = (time() - start_time)         
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    time_str = str(f"""Total runtime - int(hours))+":"+str(int(mins))+":"+str(round(secs,2)""")
    print(time_str)
    
    