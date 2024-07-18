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
    return 0.125

#Function to get PID
def GetPid(particle):
    return 211

if __name__ == '__main__':
    # Get the reaction particles from command line
    particles = sys.argv[1].split(",")
    nEvents = int(sys.argv[2])
    nParticles = int(len(particles))
    
    # Initialise numpy arrays (RDF columns)
    truP = np.empty(shape=(nEvents, nParticles), dtype=np.float64)
    truTheta = np.empty(shape=(nEvents, nParticles), dtype=np.float64)
    truPhi = np.empty(shape=(nEvents, nParticles), dtype=np.float64)
    truAcc = np.empty(shape=(nEvents, nParticles), dtype=np.uint)
    
    recP = np.empty(shape=(nEvents, nParticles), dtype=np.float64)
    recTheta = np.empty(shape=(nEvents, nParticles), dtype=np.float64)
    recPhi = np.empty(shape=(nEvents, nParticles), dtype=np.float64)
    recAcc = np.empty(shape=(nEvents, nParticles), dtype=np.uint)
    
    M = np.empty(shape=(nEvents, nParticles), dtype=np.float32)
    PID = np.empty(shape=(nEvents, nParticles), dtype=np.int32)
    sync = np.empty(shape=(nEvents, nParticles), dtype=np.uint)
    
    i = 0
    for particle in particles:
        # Constant particle data
        # For now just constants can think about this later
        M[:,i] = [GetMass(particle)]*nEvents
        PID[:,i] = [GetPid(particle)]*nEvents
        sync[:,i] = [i]*nEvents

        
        # Truth and Reconstruction file
        # Currently ignoring recon struct
        dfTruth = ROOT.RDataFrame('tree',"./data/gluex_reaction.root")
        
        # Read in the momentum arrays
        truP[:,i] = dfTruth.AsNumpy(columns=["truth."+particle+"P"])["truth."+particle+"P"]
        truTheta[:,i] = dfTruth.AsNumpy(["truth."+particle+"Theta"])["truth."+particle+"Theta"]
        truPhi[:,i] = dfTruth.AsNumpy(["truth."+particle+"Phi"])["truth."+particle+"Phi"]
        truAcc[:,i] = dfTruth.AsNumpy(["accepted_"+particle])["accepted_"+particle].astype(np.uint)
        
        # fast sim reconstructed data + acceptances
        dfRecon = ROOT.RDataFrame('recon',"results10/"+particle+"/predictions.root")
        
        recP[:,i] = dfRecon.AsNumpy([particle+"P"])[particle+"P"]
        recTheta[:,i] = dfRecon.AsNumpy([particle+"Theta"])[particle+"Theta"]
        recPhi[:,i] = dfRecon.AsNumpy([particle+"Phi"])[particle+"Phi"]
        
        # Fast sim acceptences in another file
        dfAcc = ROOT.RDataFrame('acceptance',"results10/"+particle+"/simulation_acceptances.root")
        
        recAcc[:,i] = dfAcc.AsNumpy(["accept_"+particle])["accept_"+particle].astype(np.uint)

        i += 1

    # testing
    truP = np.array([1, 2])
    sync = np.array([0, 1])
    
    dict = {'truP' : np.array([1,2]), #'truTheta' : np.array(truTheta[:,:]), 'truPhi' : np.array(truPhi[:,:]), 'truAcc' : np.array(truAcc[:,:]),
            #'recP' : np.array(recP[:,:]), 'recTheta' : np.array(recTheta[:,:]), 'recPhi' : np.array(recPhi[:,:]), 'recAcc' : np.array(recAcc[:,:]),
            #S'M' : np.array(M[:,:]), 'PID' :  np.array(PID[:,:]), 
            'Sync' : np.array([1,2])
            }
    
    print(truP)
    print(sync)
    
    # Create the data frame
    df = ROOT.RDF.MakeNumpyDataFrame(dict)
    df.Display().Print()
    df.Snapshot('tree', 'master.root')
    
    file = ROOT.TFile.Open("master.root", "READ")
    tree = file.tree
    print(tree.GetEntries())
    # Read in as dataframe