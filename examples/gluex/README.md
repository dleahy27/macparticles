# MacParticles - GlueX
## Machine Learned Particle Kinematics Using GlueX Simulation Data
This directory makes use of the already existing framework of macparticles and allows training/simulation of reactions. Here, as an example, is the 2 Pion Photoproduction reaction, 
$$ \gamma + p \rightarrow p^{'} + \pi^+ + \pi^-.$$

The model is trained on GlueX data, differentiating it from the toy model (see [<ins>macparticles/examples/toy](../toy/) for more details), and highlighting the applicability of macparticles to real data. However, to first train on this data it has to be converted into a compatible format for both the training and simulation stages. For this there are two python APIs, Hddm_rToRoot.py and Hddm_sToRoot.py. These APIs read in GlueX hddm files and then convert them to the needed ROOT Tree format for training/simulation - more detail on how both of these APIs function is found below.

The output of the fast simulation itself, in the same format as the future ePIC data. This allows the output to be used within the RAD software developed by Dr. Glazier (author of Macparticles), thus it is expected that the data generated here will be used in conjunction with RAD to develop plots and kinematic information.

## Scripts
The reccommended way to run this program is through the use of 2 seperate scripts **Setup.py** and **Simulate.py**. Each of these handle seperate parts of the fastsim, running all the necessary programs as well as cleaning and merging files. Setup.py handles all the data conversion from HDDM files to ROOT, with Simulate.py handling all the training and simulation aspects. **Important!** To run this program the location of gluexrun must be specified in the Setup.py file, and further if using RAD data for resolutions and/or acceptance training make sure to specify it in Configuration.C first.

To run the scripts just enter the following commands:
```
python3 Setup.py path/to/training/input.hddm path/to/simulation/input.hddm proton,pip,pim proton,pi+,pi-
python3 Simulate.py gamma,proton,pi+,pi- Proton,PiPlus,PiMinus gamma,p,pip,pim
```
If you have all the data set up and just want to try different weightings and/or models just run Simulate.py itself.
```
python3 Simulate.py gamma,proton,pi+,pi- Proton,PiPlus,PiMinus gamma,p,pip,pim
```
Currently there is an option to run Simulate.py with rad data, and further the kinematic fitted data. However, as this option has only been tested for resolution, it has to be activated manually. This can be done by putting in an extra option to all the training macros, as an example:
```
macparticles 'RunResolutionTraining.C( "pi+", "PiPlus", rad=true )'
```
As it has only been tested for resolutions

## Training, Simulating and Plotting
Once the data has been converted the rest is largely the same as for the toy example, only having some of the ROOT macro's code changed to suit this example specifically. Thus, following on from the [<ins>toy example](../toy/) they now need to be configured. Assuming you have already followed the [<ins>set up](macparticles/README.md), this is done by running the command
```
macparticles Configure.C
```
After this the data can be trained. This is done through entering the command
```
macparticles 'RunAcceptanceTraining.C( "pi+")'
```
If the fast sim looks a bit off the weights can be further improved by a rewighting stage which is run with
```
macparticles 'RunReweightTraining.C( "pi+" )'
```
Then finally, the resolutions can be trained by entering
```
'RunResolutionTraining.C( "pi+", "PiPlus" )'
```
**Note**, each particle has to be trained individually. So the above command has to be entered for each particle, changing both the name and training file to the correct particle.

With every particle trained the simulation can then be executed with
```
macparticles 'RunSimulation.C( "proton","p",0 )'
macparticles 'RunSimulation.C( "pi+","pip",1 )'
macparticles 'RunSimulation.C( "pi-","pim",2 )'
```
Following this all the data can be compiled into the RAD format by running master.py,
```
python3 ./python/master.py gamma,p,pip,pim gamma,proton,pi+,pi-
``` 
Following this, for plotting and kinematic information, RAD can be used with this outputted data to make plots.
## Data Conversion
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
gluexrun python2 ./python/Hddm_sToRoot.py <path/to/input/data> proton,pi+,pi-
```
This only produces a singular ROOT file as an output and requires no additional commands.
## Requirements and Testing
This program was written, tested, and requires the following modules:
- CERN ROOT (6.24)
- Python (3.8.10)
- Keras (2.8.0)
- Scikit-learn (1.0.2)
- Tensorflow (2.8.0)

Furthermore, this program requires access to the gluex container to run the HDDM converters and/or Setup.py.
## Future Plans // Issues
- How to read in total number of events in a HDDM file. Needed for progress bar in Hddm_sToRoot.py
- Generalise core to accept RAD data too