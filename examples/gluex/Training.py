# Python script to handle Macparticles simulation
# Import and define constants
import os 
import sys
import time

py = "./python/"
macparticles = "root -q ../../macros/Load.C" 

def Train(particles,resparticles=[""], id=False):
    #Run Configure file
    if id:
        os.system(macparticles+" 'Configure_Rad.C'")
    else:
        os.system(macparticles+" 'Configure_etaphi.C'")
        
           
        
    
    # Train for each particle
    for i in range(len(particles)):
        if id:
            os.system(f"""{macparticles} 'RunAcceptanceTraining.C( "{particles[i]}", "{resparticles[i]}" )'""")
            os.system(f"""{macparticles} 'RunReweightTraining.C( "{particles[i]}", "{resparticles[i]}" )'""")
            os.system(f"""{macparticles} 'RunResolutionTraining.C( "{particles[i]}", "{resparticles[i]}" )'""")
        else:
            os.system(f"""{macparticles} 'RunAcceptanceTraining.C( "{particles[i]}" )'""")
            os.system(f"""{macparticles} 'RunReweightTraining.C( "{particles[i]}" )'""")
            os.system(f"""{macparticles} 'RunResolutionTraining.C( "{particles[i]}" )'""")
            
            
        i += 1

if __name__ == '__main__':
    # Execute program
    start_time = time.time()
    
    if len(sys.argv) > 2:
        Train(sys.argv[1].split(','), sys.argv[2].split(','), True)
    else:
        Train(sys.argv[1].split(','))
         
    # Print out script run time
    remaining = (time.time() - start_time)         
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    print(f"Total runtime - {int(hours)}:{int(mins)}:{round(secs,2)}")