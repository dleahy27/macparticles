# Note uses Python2 as HDDM dependancy
import hddm_s
import os
import sys
import glob
import ROOT
from ROOT import TDatabasePDG as pdg
from ROOT import TLorentzVector
from array import array
import math
from time import time
import random

# Find way to generalise event struct
ROOT.gInterpreter.Declare("""
struct event {
    std::vector<double> P{0,0,0,0,0}; 
    std::vector<double> Theta{0,0,0,0,0}; 
    std::vector<double> Phi{0,0,0,0,0};
    std::vector<int> Pid{0,0,0,0,0};
    std::vector<float> Mass{0,0,0,0,0};
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

def SphericalToCartesian(rho,theta,phi):
    x = rho*math.sin(theta)*math.cos(phi)
    y = rho*math.sin(theta)*math.sin(phi)
    z = rho*math.cos(theta)
    return x,y,z

def Decay(momentum, decay_pdgs):
    # Generalise to more than 2 by using the class Dr. Glazier mentioned on teams at some point
    # parent and child masses
    m_parent = GetMass(decay_pdgs)
    m_child1 = 0
    m_child2 = 0
    # m_parent = GetMass(decay_pdgs[0])
    # m_child1 = GetMass(decay_pdgs[1])
    # m_child2 = GetMass(decay_pdgs[2])
    
    # Original parent particle momentum
    v = TLorentzVector(momentum.px, momentum.py, momentum.pz, momentum.E)
    v_boost = v.BoostVector()
    
    # Breakup CM momentum
    P_breakup = 0.5*math.sqrt((m_parent**2 + m_child1**2 + m_child2**2 - 2*(m_parent*m_child1 + m_parent*m_child2 + m_child1*m_child2)))
    # Randomly sample the angles
    # Could just sample theta between -pi/2 and pi/2?
    child1_costheta = random.uniform(-1,1)
    child1_theta = math.acos(child1_costheta)
    child2_theta = math.pi - child1_theta
    
    child1_phi = random.uniform(-math.pi, math.pi)
    child2_phi = math.pi + child1_phi
    
    # Eta rest frame is what the particles are created in
    # child1 = TLorentzVector(0,0,0,m_child1) + TLorentzVector(SphericalToCartesian(P_breakup,child1_theta,child1_phi),P_breakup)
    # child2 = TLorentzVector(0,0,0,m_child2) + TLorentzVector(SphericalToCartesian(P_breakup,child2_theta,child2_phi),P_breakup)
    child1 = TLorentzVector()
    child2 = TLorentzVector()
    child1_cart = SphericalToCartesian(P_breakup,child1_theta,child1_phi)
    child2_cart = SphericalToCartesian(P_breakup,child2_theta,child2_phi)
    child1.SetXYZM(child1_cart[0], child1_cart[1], child1_cart[2], 0)
    child2.SetXYZM(child2_cart[0], child2_cart[1], child2_cart[2], 0)
    
    # Boost to lab frame
    child1.Boost(-v_boost)
    child2.Boost(-v_boost)
    
    child1_p = child1.P()
    child2_p = child2.P()
    child1_theta = child1.Theta()
    child2_theta = child2.Theta()
    child1_phi = child1.Phi()
    child2_phi = child2.Phi()
    
    return child1_p, child1_theta, child1_phi, child2_p, child2_theta, child2_phi,

def GetPid(_particle):
    return pdg.Instance().GetParticle(_particle).PdgCode() 

def GetParticle(_pid):
    return pdg.Instance().GetParticle(_pid).GetName()

def GetMass(_pid):
    return pdg.Instance().GetParticle(_pid).Mass()

def HddmToRoot(input_name, output_name, particles, decay_particles=[""]):
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
            j=0
            for product in reaction.getVertices()[0].getProducts():
                for particle in particles:
                    if GetParticle(product.pdgtype).lower() == particle:
                        truth.Pid[j] = product.pdgtype
                        truth.Mass[j] = GetMass(product.pdgtype)
                        for momentum in product.getMomenta():
                            truth.P[j], truth.Theta[j], truth.Phi[j] = CartesianToSpherical(momentum)
                            j += 1
                                
                if GetParticle(product.pdgtype).lower() == decay_particles[0]:
                    # Make it more general, right now set to 22
                    n = len(truth.Pid)
                    truth.Pid[n-1] = 22
                    truth.Pid[n-2] = 22
            
                    truth.Mass[n-1] = GetMass(truth.Pid[j])
                    truth.Mass[n-2] = GetMass(truth.Pid[j+1])
        
                    for momentum in product.getMomenta():
                        truth.P[n-1], truth.Theta[n-1], truth.Phi[n-1], truth.P[n-2], truth.Theta[n-2], truth.Phi[n-2] = Decay(momentum,product.pdgtype) # Decay(momentum,decay_particles)
                        
        # Fill tree and write it to file
        tree.Fill()
    myFile.Write() 

if __name__ == '__main__':
    # Read in arguments from bash script command line
    input_data = sys.argv[1]
    output_name = sys.argv[2]
    particles = sys.argv[3].split(',')
    # Check if there are any decay particles
    if len(sys.argv)==5:
        decay_particles = sys.argv[4].split(',')
        HddmToRoot(input_data, output_name, particles, decay_particles)
    else:
        # Call Hddm Function 
        HddmToRoot(input_data, output_name, particles)
    



