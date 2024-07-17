# MacParticles - GlueX
### Machine Learned Particle Kinematics Using GlueX Simulation Data
This directory makes use of the already existing framework of macparticles and applies it to the 2 Pion Photoproduction reaction, 
$$ \gamma + p \rightarrow p^{'} + \pi^+ + \pi^-.$$
The model is trained on GlueX data, differentiating it from the toy model (see [<ins>macparticles/examples/toy](../toy/) for more details), and highlighting the applicability of macparticles to real data. However, to first train on this data it had to be converted into a compatible format for both the training and simulation stages. For this there are two python APIs, Hddm_rToRoot.py and Hddm_sToRoot.py. These APIs read in GlueX hddm files and then convert them to the needed ROOT Tree format for training/simulation - more detail on how both of these APIs function is found below. 

### Training, Simulating and Plotting
Once the data has been converted the rest is largely the same as for the toy example, only having some of the ROOT macro's code changed to suit this example specifically. Thus, following on from the [<ins>toy example](../toy/) they now need to be configured. Assuming you have already followed the [<ins>set up](macparticles/README.md), this is done by running the command
```
macparticles Configure.C
```
After this the data can be trained. This is done through entering the command
```
macparticles 'RunAcceptanceTraining.C( "pi+","./data/pip_training.root","fast_sim" )'
```
If the fast sim looks a bit off the weights can be further improved by a rewighting stage which is run with
```
macparticles 'RunReweightTraining.C( "pi+","./data/pip_training.root","fast_sim" )'
```
Then finally, the resolutions can be trained by entering
```
'RunResolutionTraining.C( "pi+","./data/pip_training.root","fast_sim" )'
```
**Note**, each particle has to be trained individually. So the above command has to be entered for each particle, changing both the name and training file to the correct particle.

With every particle trained the simulation can then be executed with
```
macparticles 'RunSimulation.C( "pip","pi+","fast_sim/","results10" )'
macparticles 'RunSimulation.C( "pim","pi-","fast_sim/","results10" )'
macparticles 'RunSimulation.C( "p","proton","fast_sim/","results10" )'
```
and the resulting plots obtained by 
```
root Reconstruct_Reaction_Mac.C
```
## Data Conversion
Maybe mention something on gluexrun here -> i.e. some stuff on how we dont have the modules so ran it via cloud computing to a place that does? 
### Setup.sh (the recommended way to run this) 
This example comes with a bash script to help set up data conversion. It is run using
```
./setup.sh -t<path/to/training/data> -r<path/to/reaction/data> <particle1> <particle2> ... 
```
With the paths to both the training and reaction HDDM files being passed as flag command line arguments, and the particles being simulated passed as further arguments. This bash script will handle the execution of all scripts with the correct parameters passed, as well as other quality of life features: checking and creating output directorys, file tidying, etc.

However, if you would prefer there is the option to run the scripts individually, including both conversion APIs and other test scripts.
### Hddm_rToRoot.py
Hddm_rToRoot.py is an API to convert simulated reconstruction GlueX HDDM files into the ROOT Tree structure required for **training**. The script will loop through all the files for a particle, converting each one into a respective temporary ROOT file. If run individually, the merging and removal of such temp files will have to be done manually. The script itself can be run with
```
gluexrun python2 ./python/Hddm_rToRoot.py <path/to/input/data> <output_name> <particle>
```
The newly created temp files are stored in the data subdirectory, and have specific file endings to allow for easy merging and removal. These can be performed by running
```
output_name = "./data/<particle>"
hadd -f "${output_name}_training.root" "${output_name}_"*"_tmp.root" > /dev/null 2>&1
rm "${output_name}_"*"_tmp.root"
```
These commands have to be run for each particle that is getting trained.
### Hddm_sToRoot.py
This is very similar to the above script, however, this makes use of the hddm_s python module to read in simulated reaction data. The format is slightly different to reconstructed data, thus needing a different script. This can be run through
```
gluexrun python2 ./python/Hddm_sToRoot.py <path/to/input/data>
```
This only produces a singular ROOT file as an output and requires no additional commands.
## Requirements and Testing
This program was written and tested on Python 2.x.x, and requires the following modules.
- Hddm_s ()
- Hddm_r ()
- ROOT ()
- PyROOT ()
- Bash ()

## Future Plans // Issues
- Move Compare.py into Hddm_sToRoot.py as it handles the comparitive data
- Fix some of the saved figure locations (training, resolution, reweight and simulation)
- Reconstruct_Reaction figures to be saved on disk
- Progress bars need max entries in root tree to function, can either pass as an argument or find a way to read it