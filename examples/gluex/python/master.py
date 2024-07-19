# Need better name
# ... .py - Takes in all simulated particle data and combines into TTree to be read as a dataframe
# all the needed truth and reconstructed data as well as a sync file to point to truth
import numpy as np
import ROOT
import os
import sys

# Leave these just as constants for now
# Function to get mass
def GetMass(particle):
    if particle == "gamma":
        return 0
    elif particle == "pip":
        return 0.1396
    elif particle == "pim":
        return 0.1396
    elif particle == "p":
        return 0.938
    else:
        return 

#Function to get PID
def GetPid(particle):
    if particle == "gamma":
        return 22
    elif particle == "pip":
        return 211
    elif particle == "pim":
        return -211
    elif particle == "p":
        return 2212
    else:
        return 

if __name__ == '__main__':
    # Get the reaction particles from command line
    particles = sys.argv[1].split(",")
    nEvents = int(sys.argv[2])
    
    # Initialise dict and counter
    dict = {}
    i = 0
    for particle in particles:
        # Constant particle data
        # For now just constants can think about this later
        M = np.array([GetMass(particle)]*nEvents, dtype=np.float64)
        dict["M_"+particle] = M
        
        PID = np.array([GetPid(particle)]*nEvents, dtype=np.int32)
        dict["PID_"+particle] = PID
        
        sync = np.array([i]*nEvents, dtype=np.uint32)
        dict["Sync_"+particle] = sync
        
        # Truth and Reconstruction file
        # Currently ignoring recon struct
        dfTruth = ROOT.RDataFrame('tree',"./data/gluex_reaction.root")
        
        # Read in the momentum arrays
        truP = dfTruth.AsNumpy(columns=["truth."+particle+"P"])["truth."+particle+"P"].astype(np.float64)
        dict["truP_"+particle] = truP
        truTheta = dfTruth.AsNumpy(["truth."+particle+"Theta"])["truth."+particle+"Theta"].astype(np.float64)
        dict["truTheta_"+particle] = truTheta
        truPhi = dfTruth.AsNumpy(["truth."+particle+"Phi"])["truth."+particle+"Phi"].astype(np.float64)
        dict["truPhi_"+particle] = truPhi
        truAcc = dfTruth.AsNumpy(["accepted_"+particle])["accepted_"+particle].astype(np.uint32)
        dict["truAcc_"+particle] = truAcc
        
        # fast sim reconstructed data + acceptances
        dfRecon = ROOT.RDataFrame('recon',"results10/"+particle+"/predictions.root")
        
        recP = dfRecon.AsNumpy([particle+"P"])[particle+"P"].astype(np.float64)
        dict["recP_"+particle] = recP
        recTheta = dfRecon.AsNumpy([particle+"Theta"])[particle+"Theta"].astype(np.float64)
        dict["recTheta_"+particle] = recTheta
        recPhi = dfRecon.AsNumpy([particle+"Phi"])[particle+"Phi"].astype(np.float64)
        dict["recPhi_"+particle] = recPhi
        
        # Fast sim acceptences in another file
        dfAcc = ROOT.RDataFrame('acceptance',"results10/"+particle+"/simulation_acceptances.root")
        
        recAcc = dfAcc.AsNumpy(["accept_"+particle])["accept_"+particle].astype(np.uint32)
        dict["recAcc_"+particle] = recAcc

        i += 1
    
    # Create the data frame
    df = ROOT.RDF.MakeNumpyDataFrame(dict)
    
    # Define variable strings
    truP_string = "ROOT::RVecD{"
    truTheta_string = "ROOT::RVecD{"
    truPhi_string = "ROOT::RVecD{"
    truAcc_string = "ROOT::RVecU{"
    
    recP_string = "ROOT::RVecD{"
    recTheta_string = "ROOT::RVecD{"
    recPhi_string = "ROOT::RVecD{"
    recAcc_string = "ROOT::RVecU{"
    
    M_string = "ROOT::RVecD{"
    PID_string = "ROOT::RVecI{"
    sync_string = "ROOT::RVecU{"
    
    
    # Write in for each particle
    j = 1
    for particle in particles:
        if j == len(particles):
            truP_string += "truP_{0}}}".format(particle)
            truTheta_string += "truTheta_{0}}}".format(particle)
            truPhi_string += "truPhi_{0}}}".format(particle)
            truAcc_string += "truAcc_{0}}}".format(particle)
            
            recP_string += "recP_{0}}}".format(particle)
            recTheta_string += "recTheta_{0}}}".format(particle)
            recPhi_string += "recPhi_{0}}}".format(particle)
            recAcc_string += "recAcc_{0}}}".format(particle)
        
            M_string += "M_{0}}}".format(particle)
            PID_string += "PID_{0}}}".format(particle)
            sync_string += "Sync_{0}}}".format(particle)
            
        else:
            truP_string += "truP_{0},".format(particle)
            truTheta_string += "truTheta_{0},".format(particle)
            truPhi_string += "truPhi_{0},".format(particle)
            truAcc_string += "truAcc_{0},".format(particle)
            
            recP_string += "recP_{0},".format(particle)
            recTheta_string += "recTheta_{0},".format(particle)
            recPhi_string += "recPhi_{0},".format(particle)
            recAcc_string += "recAcc_{0},".format(particle)
        
            M_string += "M_{0},".format(particle)
            PID_string += "PID_{0},".format(particle)
            sync_string += "Sync_{0},".format(particle)    
                     
        j += 1
    
    # Compile all particle columns
    df = df.Define("truP",truP_string).Define("truTheta",truTheta_string).Define("truPhi",truPhi_string)
    df =df.Define("recP",recP_string).Define("recTheta",recTheta_string).Define("recPhi",recPhi_string)
    df = df.Define("truAcc",truAcc_string).Define("recAcc",recAcc_string)
    df = df.Define("M",M_string).Define("PID",PID_string).Define("Sync",sync_string)
    
    # Perform any filter/cuts
    
    # Save the wanted columns to file
    df.Display(['truP','truTheta', 'truPhi', 'truAcc', 'recP', 'recTheta', 'recPhi', 'recAcc', 'M', 'PID', 'Sync']).Print()
    df.Snapshot('tree', 'master.root', ['truP','truTheta', 'truPhi', 'truAcc', 'recP', 'recTheta', 'recPhi', 'recAcc', 'M', 'PID', 'Sync'])
    
    # Test
    # file = ROOT.TFile.Open("master.root", "READ")
    # tree = file.tree
    # print(tree.GetEntries())