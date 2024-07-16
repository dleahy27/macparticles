// Function that takes in the simulated trees and fast sim trees
// Replaces truth data with simulated
// Currently trying to replace the py with this, will be a lot faster


//Define a struct
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

void Compare(){
  
  std::unique_ptr<TFile> inputFile( TFile::Open("/w/work4/jlab/halld/sim/2017-01/gen_amp/ver46/amo_merged/tree_pippim__B4_gen_amp/merged/tree_pippim__B4_gen_amp_031036.root", "update") );
  auto inputTree = inputFile->Get("pippim__B4_Tree");

  std::unique_ptr<TFile> outputFile( TFile::Open("./gluex_reaction.root", "update"));
  auto outputTree = outputFile->Get("tree");

  event recon;
  auto reconBranch = outputTree->Branch("recon", &recon);

  for (auto entry : inputTree){

    recon.pipP = entry.Thrown__P4[1]->Rho();
    recon.pipTheta = entry.Thrown__P4[1]->Theta();
    recon.pipPhi = entry.Thrown__P4[1]->Phi();
    
    recon.pimP = entry.Thrown__P4[2]->Rho();
    recon.pimTheta = entry.Thrown__P4[2]->Theta();
    recon.pimPhi = entry.Thrown__P4[2]->Phi();
    
    recon.pP = entry.Thrown__P4[0]->Rho();
    recon.pTheta = entry.Thrown__P4[0]->Theta();
    recon.pPhi = entry.Thrown__P4[0]->Phi();

    reconBranch->Fill();
  }
  
  outputFile->Write("", TObject::kOverwrite);

}
