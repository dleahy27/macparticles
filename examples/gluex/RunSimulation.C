void RunSimulation(string particle, string simparticle, unsigned int i){

  auto info  = TrainingInfo(particle,"training.root");
  string outdir = "results10";
  string simdir = "fast_sim/";

  ConfigureSimulation config;
  config.Load(simdir);
  //output directory for simulated data
  config.SetParticleName(simparticle);
  config.Simulate(outdir);
  config.UsePid(particle);

  //configure the data loader for requested particle
  DataLoader  dl("tree", "./data/gluex_reaction.root");

  //if variables in new tree are different from original simulated data
  // auto varPrefix = std::string("XXX")+particle;
  // accepted name, generated name, reconstructed name
  auto pname = simparticle.data();

  dl.SetTruthVars({Form("truth_%sP",pname),Form("truth_%sTheta",pname), Form("truth_%sPhi",pname)});
  dl.SetGenVars({Form("truth_%sP",pname),Form("truth_%sTheta",pname), Form("truth_%sPhi",pname)});
  dl.SetReconVars({Form("%sP",pname),Form("%sTheta",pname), Form("%sPhi",pname)});

  dl.UnloadColumnsSim(simparticle, i);
  

  
  /////if variables are just the same as the original simulation
  //// dl.SimVars(info.variables);

  dl.SetFractionToProcess(1);

  //and run fast simulation
  SimWithKerasAccDTRes(config,dl,simparticle, i);

  // Can ignore for now
  //ResolutionPlotter(dl,config).PlotSimulation();

   
}




/*{
  ConfigureSimulation config;
  config.Load("fast_simulation/");
  //output directory for simulated data
  config.Simulate("results/");

  //Soret the pid
  auto pid = GetPID();
  if(config.ContainsPDG(pid.Data()))
    config.UsePdg(pid.Data());
  else{
    config.UsePdg("all");
    config.PretendPdg(pid.Data());
  }
  
  //configure the data loader for requested particle
  DataLoader  dl1("tree", "toy_reaction.root");
  if(pid=="pi-"){
    dl1.SetTruthVars({"truth.pimP","truth.pimTheta","truth.pimPhi"});
    //these branches willl be created
    dl1.SetReconVars({"pimP","pimTheta","pimPhi"});

  }
  else if(pid=="pi+"){
    dl1.SetTruthVars({"truth.pipP","truth.pipTheta","truth.pipPhi"}); 
    //these branches willl be created
    dl1.SetReconVars({"pipP","pipTheta","pipPhi"});

  }
  else if(pid=="proton"){
    dl1.SetTruthVars({"truth.pP","truth.pTheta","truth.pPhi"});  
    //these branches willl be created
    dl1.SetReconVars({"pP","pTheta","pPhi"});
  }
  else{
    Fatal("RunSimulation","This particle %s is not recgonised ",pid.Data());
  }
  
  //and run fast simulation
  SimWithKerasAccDTRes(config,dl1);

 
   
}
*/
