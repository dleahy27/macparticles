# %% Note uses Python2 as HDDM dependancy
import hddm_r
import os
import sys
import glob
import ROOT
from array import array
import math
from time import time
# %%

# Function to display progress bar to terminal
def ProgressBar(i, initial_wall_time, N ):
    a = int(20*i/N)

    remaining = ((time() - initial_wall_time) / i) * (N - i)
            
    mins, secs = divmod(remaining, 60)
    hours, mins = divmod(mins, 60)
    time_str = str(int(hours))+":"+str(int(mins))+":"+str(round(secs,2))

    if i==0:
        time_str="--:--:--.--"

    prefix="\t" 
    sys.stdout.write(prefix+"["+'#'*a+('.'*(20-a))+"] "+str(round(100*(i-1)/N,2))+"% ETA "+ time_str + ' \r')
    sys.stdout.flush()

    return

def StringToPdg(particle):
    # Convert strings to interger PDG values
    # Only working with pi+- proton and gamma
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

def HddmLoader(data_path, output_name, particle):
    # Loads HDDM reader for each particle file
    print "Loading and converting all ", particle, " files from ", data_path, "."
    # Counters
    i = 1
    initial_wall_time = time()

    # Convert all the HDDM files to Root Trees
    input_names = glob.glob(data_path+"particle_gun_"+particle+"*.hddm")
    for input_name in input_names:
        ProgressBar(int(i), initial_wall_time, len(input_names))
        HddmToRoot(input_name,output_name,str(i))
        i += 1

def HddmToRoot(input_name, output_name, i):
    # Initialise output file and TTree
    myFile = ROOT.TFile.Open(output_name+"_"+i+"_tmp.root", "RECREATE")
    tree = ROOT.TTree("simtree", "training_data")

    # Initialise TTree branches 
    tru_pdg = array('i', [0])
    tru_E = array('d', [0])
    tru_p = array('d', [0])
    tru_theta = array('d', [0])
    tru_phi = array('d', [0])
    rec_E_bcal= array('d', [0])
    rec_E_fcal = array('d', [0])
    rec_track_pdg = array('i', [0])
    rec_track_chi2 = array('d', [0])
    rec_track_p = array('d', [0])
    rec_track_theta = array('d', [0])
    rec_track_phi = array('d', [0])
    rec_cluster_fcal = array('d', [0])
    rec_cluster_bcal = array('d', [0])
    acceptance = array('I', [0])
    l1_bits = array('I', [0])

    tree.Branch("truPdg",tru_pdg,"truPdg/I")
    tree.Branch("truE",tru_E,"truE/D")
    tree.Branch("truP",tru_p,"truP/D")
    tree.Branch("truTheta",tru_theta,"truTheta/D")
    tree.Branch("truPhi",tru_phi,"truPhi/D")
    tree.Branch("recPdg",rec_track_pdg,"recPdg/I")
    tree.Branch("recChi2",rec_track_chi2,"recChi2/D")
    tree.Branch("recP", rec_track_p, "recP/D")
    tree.Branch("recTheta", rec_track_theta, "recTheta/D")
    tree.Branch("recPhi", rec_track_phi, "recPhi/D")
    # maybe better names for these, not sure exactly what they are
    tree.Branch("L1TriggerBits",l1_bits, "L1TriggerBits/I")
    tree.Branch("E_bcal",rec_E_bcal,"E_bcal/D")
    tree.Branch("E_fcal",rec_E_fcal,"E_fcal/D")
    tree.Branch("Cluster_fcal",rec_cluster_fcal,"Cluster_fcal/D")
    tree.Branch("Cluster_bcal",rec_cluster_bcal,"Cluster_bcal/D")
    tree.Branch("accepted",acceptance,"accepted/I")

    # Load file and skip first event (always nothing)
    try:
        f = iter(hddm_r.istream(input_name))
        next(f)
    except:
        print "The file, ", input_name, " cannot be read."
        return
    # Loop over all the events
    for rec in f:
        for reaction in rec.getReactions():
            for product in reaction.getVertices()[0].getProducts():
                tru_pdg[0] = product.pdgtype
                for momentum in product.getMomenta():
                    tru_E[0] = momentum.E 
                    tru_p[0], tru_theta[0], tru_phi[0] = CartesianToSpherical(momentum)
         
        for trig in rec.getTriggers():
            l1_bits[0] = trig.l1_trig_bits
            for esum in trig.getTriggerEnergySumses():
                rec_E_bcal[0] = esum.BCALEnergySum
                rec_E_fcal[0] = esum.FCALEnergySum
    
        # Particle is accepted/detected if its energy is detected or track is reconstructed
        for track in rec.getChargedTracks():
            if  StringToPdg(track.ptype) == tru_pdg[0]:
                rec_track_pdg[0] = StringToPdg(track.ptype)
                acceptance[0] = 1
                for fit in track.getTrackFits():
                    rec_track_chi2[0] = fit.chisq
                    rec_track_p[0], rec_track_theta[0], rec_track_phi[0] = CartesianToSpherical(fit)
            else:
                continue

        
        for fcal in rec.getFcalShowers():
            rec_cluster_fcal[0] = fcal.E
        
        for bcal in rec.getBcalShowers():
            rec_cluster_bcal[0] = bcal.E
        
        # Fill tree then write
        tree.Fill()
    myFile.Write()

    return 

if __name__ == '__main__':
    # Read in arguments from bash script command line
    input_data = sys.argv[1] 
    output_name = sys.argv[2] 
    particle = sys.argv[3]

    # Call Hddm Function 
    HddmLoader(input_data, output_name, particle)


