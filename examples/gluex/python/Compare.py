import ROOT
import numpy as np
from array import array
from time import time
import sys
# Python Script to read in the simulated data
# Should probably move it into Hddm_sToRoot
# Was hoping to move it to a root macro to speed it up

def ProgressBar(i, initial_wall_time, N ):
    # Progress bar to command line
    a = int(20*i/N)

    remaining = ((time() - initial_wall_time) / (i+1)) * (N - i)
            
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    time_str = str(int(hours))+":"+str(int(mins))+":"+str(round(secs,2))

    if i==0:
        sys.stdout.write("\n")
        time_str="--:--:--.--"

    prefix="\t" 
    sys.stdout.write(prefix+"["+'#'*a+('.'*(20-a))+"] "+str(round(100*(i)/N,2))+"% ETA "+ time_str + ' \r')
    sys.stdout.flush()

    return

# Define a struct
ROOT.gInterpreter.Declare("""
struct event {
    Double_t pP=0;
    Double_t pTheta=0;
    Double_t pPhi=0;
    Double_t pipP=0;
    Double_t pipTheta=0;
    Double_t pipPhi=0;
    Double_t pimP=0;
    Double_t pimTheta=0;
    Double_t pimPhi=0;
};
""") 

if __name__ == '__main__':
    # Open input/output files and relevant trees
    inFile = ROOT.TFile.Open("/w/work4/jlab/halld/sim/2017-01/gen_amp/ver46/amo_merged/tree_pippim__B4_gen_amp/merged/tree_pippim__B4_gen_amp_031036.root", "READ")
    inTree = inFile.pippim__B4_Tree
    
    outFile = ROOT.TFile.Open("gluex_reaction.root", "update")
    outTree = outFile.tree
    
    # Create recon struct, will be a branch in our output
    recon = ROOT.event()
    reconBranch = outTree.Branch("recon", recon)
    
    # Progress bar initialisations
    i = 0
    init_time = time()
    
    # Loop over each value in the input Tree
    for entry in inTree:
        ProgressBar(int(i), init_time, 1902527)
        # Store each particles data in the recon struct
        recon.pipP = entry.Thrown__P4[1].Rho()
        recon.pipTheta = entry.Thrown__P4[1].Theta()
        recon.pipPhi = entry.Thrown__P4[1].Phi()
        
        recon.pimP = entry.Thrown__P4[2].Rho()
        recon.pimTheta = entry.Thrown__P4[2].Theta()
        recon.pimPhi = entry.Thrown__P4[2].Phi()
        
        recon.pP = entry.Thrown__P4[0].Rho()
        recon.pTheta = entry.Thrown__P4[0].Theta()
        recon.pPhi = entry.Thrown__P4[0].Phi()

        reconBranch.Fill()
        i += 1

    # Update the root Tree
    outFile.Write("", ROOT.TObject.kOverwrite) 
  