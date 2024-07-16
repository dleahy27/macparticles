import os
import sys
import ROOT
ROOT.gROOT.SetBatch(False)

def DataFrameTest(output_name):
    # Load the dataframe and add resolution columns
	df = ROOT.RDataFrame('simtree', output_name).Define("resP", "abs(truP-recP)").Define("resTheta", "abs(truTheta-recTheta)").Define("resPhi","abs(truPhi-recPhi)")
    # Here can define any cuts, additions or tests (plotting histos)
	#h1 = df.Histo1D("truTheta")
	#h1.Draw()
	#g1 = df.Graph("truTheta", "Acceptance")
	#g1.Draw()
	#df.Display("truP",10).Print()
	df.Snapshot("simtree", output_name)

	return

if __name__=='__main__':
        # Load command line arguments
        output_name = sys.argv[1] 

        # Load merged file as RDF and do stuff to it
        DataFrameTest(output_name)
		
