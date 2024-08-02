# Note uses Python2 as HDDM dependancy
import hddm_s
import os
import sys
import glob
import ROOT
from array import array
import math
from time import time

ROOT.gInterpreter.Declare("""
struct event {
    std::vector<double> P{0,0,0}; 
    std::vector<double> Theta{0,0,0}; 
    std::vector<double> Phi{0,0,0};
};

struct beam {
    double P = 0;
    double Theta = 0;
    double Phi = 0; 
};
""")

def ProgressBar(j, initial_wall_time, N ):
    i = j-1
    a = int(20*i/N)

    remaining = ((time() - initial_wall_time) / (j) * (N - i))
            
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    time_str = str(int(hours))+":"+str(int(mins))+":"+str(round(secs,2))

    if i==0:
        time_str="--:--:--.--"

    prefix="\t" 
    sys.stdout.write(prefix+"["+'#'*a+('.'*(20-a))+"] "+str(round(100*i/N,2))+"% ETA "+ time_str + ' \r')
    sys.stdout.flush()

    return

def CartesianToSpherical(momentum_xyz):
    # Takes in momentum class from Hddm library
    p = math.sqrt((momentum_xyz.px)**2 + (momentum_xyz.py)**2 + (momentum_xyz.pz)**2)
    phi = math.atan2(momentum_xyz.py,momentum_xyz.px)
    theta = math.acos(momentum_xyz.pz/p)

    return p,theta,phi

def GetPid(_particle):
    return pdg.Instance().GetParticle(_particle).PdgCode() 

def HddmToRoot(input_name, output_name, particles):
    # Initialise output file and TTree
    myFile = ROOT.TFile.Open(output_name+".root", "RECREATE")
    tree = ROOT.TTree("tree", "Generated_Reaction_Data")

    beam = ROOT.beam()
    truth = ROOT.event()

    tree.Branch("truth",truth)
    tree.Branch("beam", beam)

    # Start ProgressBar counters
    # For now comment out until I can get total number of events from HDDM
    #i = 1
    #initial_wall_time = time()
    
    # Load file and skip first event (always nothing)
    try:
        f = iter(hddm_s.istream(input_name))
        # ProgressBar(int(i), initial_wall_time, 10**6)
        # i += 1
    except:
        # Only print as we still want the program to run
        print "The file, ", input_name, " cannot be read."

    # Loop over all the events
    for rec in f:
        # ProgressBar(int(i), initial_wall_time, 10**6)
        for reaction in rec.getReactions():
            for Beam in reaction.getBeams():
                for momentum in Beam.getMomenta():
                    beam.P, beam.Theta, beam.Phi = CartesianToSpherical(momentum)
            for product in reaction.getVertices()[0].getProducts():
                pdg  = product.pdgtype
                
                i=0
                for particle in particles:
                    if particle == "gamma":
                        continue # Gammas cant be reconstructed
                    elif GetPid(particle) == pdg:
                        truth.P[i], truth.Theta[i], truth.Phi[i] = CartesianToSpherical(momentum)
                        i += 1
                        continue       
                continue
        i += 1

        # Fill tree and write it to file
        tree.Fill()
    myFile.Write() 

if __name__ == '__main__':
    # Read in arguments from bash script command line
    input_data = sys.argv[1]
    particles = sys.argv[2].split(',') 
    output_name = os.path.join("data", "gluex_reaction")

    # Call Hddm Function 
    HddmToRoot(input_data, output_name, particles)
    



