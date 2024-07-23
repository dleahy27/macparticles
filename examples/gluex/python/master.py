# Imports and const definitions
import numpy as np
import ROOT
import os
import sys
nullPtr = -1E6
u_nullPtr = 1E6
ROOT.gInterpreter.Declare("auto valFilter = [](double val){return val!=-1E6;};")
ROOT.gInterpreter.Declare("auto u_valFilter = [](double val){return val!=1E6;};")
ROOT.gInterpreter.Declare("auto accFilter = [](double val){return val!=0;};")

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
    
    # Open file and get number of events
    tempFile = ROOT.TFile.Open("./data/gluex_reaction.root", "READ")
    tempTree = tempFile.tree
    nEvents = tempTree.GetEvents()
    tempFile.Close()
    
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
        truP = dfTruth.AsNumpy(columns=["truth.P["+i+"]"])["truth.P["+i+"]"].astype(np.float64)
        dict["truP_"+particle] = truP
        truTheta = dfTruth.AsNumpy(columns=["truth.Theta["+i+"]"])["truth.Theta["+i+"]"].astype(np.float64)
        dict["truTheta_"+particle] = truTheta
        truPhi = dfTruth.AsNumpy(columns=["truth.Phi["+i+"]"])["truth.Phi["+i+"]"].astype(np.float64)
        dict["truPhi_"+particle] = truPhi
        
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
        
        # Put in nullPtrs based of acceptances
        recP[recAcc == 0] = nullPtr
        recTheta[recAcc == 0] = nullPtr
        recPhi[recAcc == 0] = nullPtr
        M[recAcc == 0] = nullPtr
        PID[recAcc == 0] = nullPtr
        sync[recAcc == 0] = u_nullPtr
        
        
        dict["recAcc_"+particle] = recAcc

        i += 1
    
    # Create the data frame
    df = ROOT.RDF.MakeNumpyDataFrame(dict)
    
    # Define variable strings
    truP_string = "ROOT::RVecD{"
    truTheta_string = "ROOT::RVecD{"
    truPhi_string = "ROOT::RVecD{"
    
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
            
            recP_string += "recP_{0},".format(particle)
            recTheta_string += "recTheta_{0},".format(particle)
            recPhi_string += "recPhi_{0},".format(particle)
            recAcc_string += "recAcc_{0},".format(particle)
        
            M_string += "M_{0},".format(particle)
            PID_string += "PID_{0},".format(particle)
            sync_string += "Sync_{0},".format(particle)    
                     
        j += 1
    
    # Compile all particle columns into temp columns
    df =df.Define("recP_temp",recP_string).Define("recTheta_temp",recTheta_string).Define("recPhi_temp",recPhi_string)
    df = df.Define("recAcc_temp",recAcc_string)
    df = df.Define("M_temp",M_string).Define("PID_temp",PID_string).Define("Sync_temp",sync_string)
    
    
    # Remove null pointers for the wanted columns
    df = df.Define("truP",truP_string).Define("truTheta",truTheta_string).Define("truPhi",truPhi_string)
    df =df.Define("recP","ROOT::VecOps::Filter(recP_temp,valFilter)").Define("recTheta","ROOT::VecOps::Filter(recTheta_temp,valFilter)").Define("recPhi","ROOT::VecOps::Filter(recPhi_temp,valFilter)")
    df = df.Define("recAcc","ROOT::VecOps::Filter(recAcc_temp,accFilter)")
    df = df.Define("M","ROOT::VecOps::Filter(M_temp,valFilter)").Define("PID","ROOT::VecOps::Filter(PID_temp,valFilter)").Define("Sync","ROOT::VecOps::Filter(Sync_temp,u_valFilter)")
    
    # Perform any filter/cuts
    
    # Save the wanted columns to file
    df.Snapshot('tree', './data/master.root', ['truP','truTheta', 'truPhi', 'recP', 'recTheta', 'recPhi', 'recAcc', 'M', 'PID', 'Sync'])