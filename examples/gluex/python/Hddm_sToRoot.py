# %% Note uses Python2 as HDDM dependancy
import hddm_s
import os
import sys
import glob
import ROOT
from array import array
import math
from time import time
# %%

# Define a c++ struct
ROOT.gInterpreter.Declare("""
struct event {
    std::vector<Double_t> P = [0,0,0] 
    std::vector<Double_t> Theta = [0,0,0] 
    std::vector<Double_t> Phi = [0,0,0] 
};
""")

# Progress bar to command line
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
           


def StringToPdg(particle):
    # Convert particle names to their PDG value
    # Only working with pi+- proton and gamma at the moment
    if particle == "Gamma":
        return 22
    elif particle == "Pi+":
        return 211
    elif particle == "Pi-":
        return -211
    elif particle == "Proton":
        return 2212
    else:
        return 

def CartesianToSpherical(momentum_xyz):
    # Takes in momentum class from Hddm library
    # Converts cartesian momentum to momentum norm and spherical coordinates
    p = math.sqrt((momentum_xyz.px)**2 + (momentum_xyz.py)**2 + (momentum_xyz.pz)**2)
    phi = math.atan2(momentum_xyz.py,momentum_xyz.px)
    theta = math.acos(momentum_xyz.pz/p)

    return p,theta,phi

def HddmToRoot(input_name, output_name):
    # Initialise output file and TTree
    myFile = ROOT.TFile.Open(output_name+".root", "RECREATE")
    tree = ROOT.TTree("tree", "Generated_Reaction_Data")

    # Initialise TTree branches
    # As accepted is a boolean, need to initialise using C++
    # Right now setting all to true
    # Will be read in by rec code
#     accepted_code = """
# Bool_t accepted_p=kTRUE;
# tree->Branch(Form("accepted_p"),&accepted_p);
# Bool_t accepted_pip=kTRUE;
# tree->Branch(Form("accepted_pip"),&accepted_pip);
# Bool_t accepted_pim=kTRUE;
# tree->Branch(Form("accepted_pim"),&accepted_pim);
# """
#     # Run above C++ code
#     ROOT.gInterpreter.ProcessLine(accepted_code)

    # beam = ...
    truth = ROOT.event()

    tree.Branch("truth",truth)
    #tree.Branch("beam", , )

    # Start ProgressBar counters
    i = 1
    initial_wall_time = time()
    
    # Load file and skip first event (always nothing)
    try:
        f = iter(hddm_s.istream(input_name))
        ProgressBar(int(i), initial_wall_time, 10**6)
        i += 1
    except:
        # Only print as we still want the program to run
        print "The file, ", input_name, " cannot be read."

    # Loop over all the events
    for rec in f:
        ProgressBar(int(i), initial_wall_time, 10**6)
        for reaction in rec.getReactions():
            # If beam data is wanted fill out below
            # for beam in reaction.getBeams():
            for product in reaction.getVertices()[0].getProducts():
                pdg  = product.pdgtype
                # Check pdg of each event (only want proton and pi+-)
                # Find a way to generalise this
                # Probably read in particles to keep it consistent, can then loop over i.e
                # for particle in particles, if pdg = pdg then i+= 1 and set array
                if pdg == 2212:
                    for momentum in product.getMomenta():
                        truth.P[0], truth.Theta[0], truth.Phi[0] = CartesianToSpherical(momentum)
                elif pdg == 211:
                    for momentum in product.getMomenta():
                        truth.P[1], truth.Theta[1], truth.Phi[1] = CartesianToSpherical(momentum)
                elif pdg == -211:
                    for momentum in product.getMomenta():
                        truth.P[2], truth.Theta[2], truth.Phi[2] = CartesianToSpherical(momentum)
                else:
                    continue

        i += 1

        # Fill tree and write it to file
        tree.Fill()
    myFile.Write() 

if __name__ == '__main__':
    # Read in arguments from bash script command line
    input_data = sys.argv[1] 
    output_name = sys.argv[2]
    # maybe particles to generalise?

    # Call Hddm Function 
    HddmToRoot(input_data, output_name)

# %%
# Sort progress bar => find way to extract total events from hddm
# Something about putting in branch data, can ask tuesday
# Find a way to generalise better. Idea on line 113
# %%



