# Imports and const definitions
import numpy as np
import ROOT
from ROOT import TDatabasePDG as pdg
import os
import sys

nullPtr = -1E6
u_nullPtr = 1E6
ROOT.gInterpreter.Declare("auto valFilter = [](double val){return val!=-1E6;};")
ROOT.gInterpreter.Declare("auto u_valFilter = [](double val){return val!=1E6;};")
ROOT.gInterpreter.Declare("auto accFilter = [](double val){return val!=0;};")

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

def SphericalToXYZ(p, theta, phi):
    px = p*np.sin(theta)*np.cos(phi)
    py = p*np.sin(theta)*np.sin(phi)
    pz = p*np.cos(theta)
    
    return px, py, pz

def GetMass(_particle):
    return pdg.Instance().GetParticle(_particle).Mass()

def GetPid(_particle):
    return pdg.Instance().GetParticle(_particle).PdgCode() 

if __name__ == '__main__':
    # Get the reaction particles from command line
    simparticles = sys.argv[1].split(',')
    particles = sys.argv[2].split(',')
    
    # Open file and get number of events
    File = ROOT.TFile.Open("./data/gluex_reaction.root", "READ")
    Tree = File.tree
    nEvents = Tree.GetEntries()
    
    # Initialise dict and counter
    dict = {}

    # Using RAD indicing [gamma, p, pip, pim] == [0,1,2,3]
    i = 0
    for particle in simparticles:
        # Recreate dataframes every iteration
        dfTruth = ROOT.RDataFrame(Tree)
        
        # Constant particle data
        recM = np.array([GetMass(particles[i])]*nEvents, dtype=np.float64)
        truM = np.array([GetMass(particles[i])]*nEvents, dtype=np.float64)
        dict["recM_"+particle] = recM
        dict["truM_"+particle] = truM
        
        recPID = np.array([GetPid(particles[i])]*nEvents, dtype=np.int32)
        truPID = np.array([GetPid(particles[i])]*nEvents, dtype=np.int32)
        dict["recPID_"+particle] = recPID
        dict["truPID_"+particle] = truPID
        
        recSync = np.array([i]*nEvents, dtype=np.uint32)
        truSync = np.array([i]*nEvents, dtype=np.uint32)
        dict["recSync_"+particle] = recSync
        dict["truSync_"+particle] = truSync
        
        # Seperate case for beam
        if particle == "gamma":
            dfTruth = dfTruth.Define("truthP", f"beam.P")
            dfTruth = dfTruth.Define("truthTheta", f"beam.Theta")
            dfTruth = dfTruth.Define("truthPhi", f"beam.Phi")     
        else:
            dfTruth = dfTruth.Define("truthP", f"truth.P[{i-1}]")
            dfTruth = dfTruth.Define("truthTheta", f"truth.Theta[{i-1}]")
            dfTruth = dfTruth.Define("truthPhi", f"truth.Phi[{i-1}]")
        
        # Read in the momentum arrays
        truP = dfTruth.AsNumpy(columns=["truthP"])["truthP"].astype(np.float64)
        truTheta = dfTruth.AsNumpy(columns=["truthTheta"])["truthTheta"].astype(np.float64)
        truPhi = dfTruth.AsNumpy(columns=["truthPhi"])["truthPhi"].astype(np.float64)
        dict["truP_"+particle] = truP
        dict["truTheta_"+particle] = truTheta
        dict["truPhi_"+particle] = truPhi

        truX, truY, truZ = SphericalToXYZ(truP, truTheta, truPhi)
        dict["truX_"+particle] = truX
        dict["truY_"+particle] = truY
        dict["truZ_"+particle] = truZ
        
        if particle == "gamma":
            recP = truP
            recTheta = truTheta
            recPhi = truPhi
            recAcc = np.array([1]*nEvents, dtype=np.uint32)
        else:
            dfRecon = ROOT.RDataFrame('recon',"results10/"+particle+"/predictions.root")
            dfAcc = ROOT.RDataFrame('acceptance',"results10/"+particle+"/simulation_acceptances.root")
            
            recP = dfRecon.AsNumpy([particle+"P"])[particle+"P"].astype(np.float64)
            recTheta = dfRecon.AsNumpy([particle+"Theta"])[particle+"Theta"].astype(np.float64)
            recPhi = dfRecon.AsNumpy([particle+"Phi"])[particle+"Phi"].astype(np.float64)
            recAcc = dfAcc.AsNumpy(["accept_"+particle])["accept_"+particle].astype(np.uint32)
            
        dict["recP_"+particle] = recP
        dict["recTheta_"+particle] = recTheta
        dict["recPhi_"+particle] = recPhi
        
        recX, recY, recZ = SphericalToXYZ(recP,recTheta,recPhi)
        dict["recX_"+particle] = recX
        dict["recY_"+particle] = recY
        dict["recZ_"+particle] = recZ
        dict["recAcc_"+particle] = recAcc
        
        # Insert nullPtrs for no acceptance
        recX[recAcc == 0] = nullPtr
        recY[recAcc == 0] = nullPtr
        recZ[recAcc == 0] = nullPtr
        recP[recAcc == 0] = nullPtr
        recTheta[recAcc == 0] = nullPtr
        recPhi[recAcc == 0] = nullPtr
        recM[recAcc == 0] = nullPtr
        recPID[recAcc == 0] = nullPtr
        recSync[recAcc == 0] = u_nullPtr
        
        i += 1
    
    # Create the data frame
    df = ROOT.RDF.MakeNumpyDataFrame(dict)
    
    # Define variable strings
    truX_string = "ROOT::RVecD{"
    truY_string = "ROOT::RVecD{"
    truZ_string = "ROOT::RVecD{"
    truP_string = "ROOT::RVecD{"
    truTheta_string = "ROOT::RVecD{"
    truPhi_string = "ROOT::RVecD{"
    
    recX_string = "ROOT::RVecD{"
    recY_string = "ROOT::RVecD{"
    recZ_string = "ROOT::RVecD{"
    recP_string = "ROOT::RVecD{"
    recTheta_string = "ROOT::RVecD{"
    recPhi_string = "ROOT::RVecD{"
    recAcc_string = "ROOT::RVecU{"
    
    truM_string = "ROOT::RVecD{"
    truPID_string = "ROOT::RVecI{"
    truSync_string = "ROOT::RVecU{"
    
    recM_string = "ROOT::RVecD{"
    recPID_string = "ROOT::RVecI{"
    recSync_string = "ROOT::RVecU{"
    
    
    # Write in for each particle
    j = 0
    for particle in simparticles:
        # Need an end bracket
        if j == len(simparticles)-1:
            truX_string += "truX_{0}}}".format(particle)
            truY_string += "truY_{0}}}".format(particle)
            truZ_string += "truZ_{0}}}".format(particle)
            truP_string += "truP_{0}}}".format(particle)
            truTheta_string += "truTheta_{0}}}".format(particle)
            truPhi_string += "truPhi_{0}}}".format(particle)
            
            recX_string += "recX_{0}}}".format(particle)
            recY_string += "recY_{0}}}".format(particle)
            recZ_string += "recZ_{0}}}".format(particle)
            recP_string += "recP_{0}}}".format(particle)
            recTheta_string += "recTheta_{0}}}".format(particle)
            recPhi_string += "recPhi_{0}}}".format(particle)
            recAcc_string += "recAcc_{0}}}".format(particle)
        
            recM_string += "recM_{0}}}".format(particle)
            recPID_string += "recPID_{0}}}".format(particle)
            recSync_string += "recSync_{0}}}".format(particle)
            
            truM_string += "truM_{0}}}".format(particle)
            truPID_string += "truPID_{0}}}".format(particle)
            truSync_string += "truSync_{0}}}".format(particle)
            
        else:
            truX_string += "truX_{0},".format(particle)
            truY_string += "truY_{0},".format(particle)
            truZ_string += "truZ_{0},".format(particle)
            truP_string += "truP_{0},".format(particle)
            truTheta_string += "truTheta_{0},".format(particle)
            truPhi_string += "truPhi_{0},".format(particle)
            
            recX_string += "recX_{0},".format(particle)
            recY_string += "recY_{0},".format(particle)
            recZ_string += "recZ_{0},".format(particle)
            recP_string += "recP_{0},".format(particle)
            recTheta_string += "recTheta_{0},".format(particle)
            recPhi_string += "recPhi_{0},".format(particle)
            recAcc_string += "recAcc_{0},".format(particle)

            recM_string += "recM_{0},".format(particle)
            recPID_string += "recPID_{0},".format(particle)
            recSync_string += "recSync_{0},".format(particle) 
            
            truM_string += "truM_{0},".format(particle)
            truPID_string += "truPID_{0},".format(particle)
            truSync_string += "truSync_{0},".format(particle)    
                     
        j += 1

    # Compile all particle columns into temp columns
    df = df.Define("recX_temp",recX_string).Define("recY_temp",recY_string).Define("recZ_temp",recZ_string)
    df = df.Define("recP_temp",recP_string).Define("recTheta_temp",recTheta_string).Define("recPhi_temp",recPhi_string)
    df = df.Define("recAcc_temp",recAcc_string)
    df = df.Define("recM_temp",recM_string).Define("recPID_temp",recPID_string).Define("recSync_temp",recSync_string)
    
    
    # Remove null pointers for the wanted columns
    df = df.Define("truX",truX_string).Define("truY",truY_string).Define("truZ",truZ_string)
    df = df.Define("truP",truP_string).Define("truTheta",truTheta_string).Define("truPhi",truPhi_string)
    df = df.Define("recX","ROOT::VecOps::Filter(recX_temp,valFilter)").Define("recY","ROOT::VecOps::Filter(recY_temp,valFilter)").Define("recZ","ROOT::VecOps::Filter(recZ_temp,valFilter)")
    df = df.Define("recP","ROOT::VecOps::Filter(recP_temp,valFilter)").Define("recTheta","ROOT::VecOps::Filter(recTheta_temp,valFilter)").Define("recPhi","ROOT::VecOps::Filter(recPhi_temp,valFilter)")
    df = df.Define("recAcc","ROOT::VecOps::Filter(recAcc_temp,accFilter)")
    df = df.Define("recM","ROOT::VecOps::Filter(recM_temp,valFilter)").Define("recPID","ROOT::VecOps::Filter(recPID_temp,valFilter)").Define("recSync","ROOT::VecOps::Filter(recSync_temp,u_valFilter)")
    df = df.Define("truM",truM_string).Define("truPID",truPID_string).Define("truSync",truSync_string)
    
    # Perform any filter/cuts
    
    # Save the wanted columns to file
    df.Snapshot('tree', './data/master.root', ['truX','truY', 'truZ', 'recX', 'recY', 'recZ', 'truP','truTheta', 'truPhi', 'recP', 'recTheta', 'recPhi', 'recAcc', 'truM', 'truPID', 'truSync', 'recM', 'recPID', 'recSync'])