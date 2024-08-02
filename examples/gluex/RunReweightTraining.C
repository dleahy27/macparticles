//macparticles 'RunReweightTraining.C( "pi+" )'
void RunReweightTraining(string particle, string radparticle = "False")
  {
    string filename = "training.root";
    string simdir = "fast_sim";
    auto dload  = TrainingInfo(particle,filename).TrainingData();


  
    //Give toplevel configuration directory
    ConfigureSimulation config;
    config.Load(simdir.data());
    //give pdg name for particle we are training
    config.UsePid(particle);

    if (radparticle != "False"){
      dload->UnloadColumnsRes(radparticle, false);
  }

    //Use a BDT to fine tune the DNN response (recommended but not required)
    BDTAcceptanceModel rewBdt(config,ProcessType::ReWeight);
    rewBdt.SetFastAcceptanceWeights(dload.get());

    ///////////////////////////////
    ///////////////////////////////
    ///Here can configure the BDT
    rewBdt.SetNEstimators(100);
    rewBdt.SetLearnRate(0.1);
    rewBdt.SetMinImpurityDecrease(1);
    rewBdt.Train(dload.get());
  

    //And some plotting
    AcceptancePlotter(*dload.get(),config).PlotTruthVars();
    AcceptancePlotter(*dload.get(),config).PlotSliceVars(0,1);
    AcceptancePlotter(*dload.get(),config).PlotSliceVars(1,1);
    AcceptancePlotter(*dload.get(),config).PlotSliceVars(2,1);

  }
