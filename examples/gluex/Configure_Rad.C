{


  auto info = TrainingInfo{"pi+"};

  info.treeName = "rad_tree";
  info.reconFile = "/home/dillon/Desktop/intern24/rad/examples/MCMatched.root";
  
  //what fraction of events in each file do you want to use?
  info.recFrac = 1;

  //truth name, generated name, reconstructed name, title, range
  info.variables ={{"truP","truP","recP","#pi+ momentum",0,10},
		   {"truTheta","truTheta","recTheta","#pi+ #theta",0,TMath::Pi()},
		   {"truPhi","truPhi","recPhi","#pi+ #phi",-TMath::Pi(),TMath::Pi()}};

  //variable to flag if particle was reconstructed in this event
  info.acceptVar = "accepted";

  //in case need further fltering of reconstructed events (e.g. truth matching,..)
  info.recFilter = "";


  info.WriteTo("training.root");
  /*********************************************************************************************************/
  info = TrainingInfo{"pi-"};

  info.treeName = "rad_tree";
  info.reconFile = "/home/dillon/Desktop/intern24/rad/examples/MCMatched.root";
  
  //what fraction of events in each file do you want to use?
  info.recFrac = 1;

  //truth name, generated name, reconstructed name, title, range
  info.variables = 	{{"truP","truP","recP","#pi- momentum",0,10},
			 {"truTheta","truTheta","recTheta","#pi- #theta",0,TMath::Pi()},
			 {"truPhi","truPhi","recPhi","#pi- #phi",-TMath::Pi(),TMath::Pi()}};

  //variable to flag if particle was reconstructed in this event
  info.acceptVar = "accepted";

  //in case need further fltering of reconstructed events (e.g. truth matching,..)
  info.recFilter = "";

 

  info.WriteTo("training.root");

 /*********************************************************************************************************/
  info = TrainingInfo{"proton"};

  info.treeName = "rad_tree";
  info.reconFile = "/home/dillon/Desktop/intern24/rad/examples/MCMatched.root";
  
  //what fraction of events in each file do you want to use?
  info.recFrac = 1;

  //truth name, generated name, reconstructed name, title, range
  info.variables = 	{{"truP","truP","recP","#proton momentum",0,10},
			 {"truTheta","truTheta","recTheta","#proton #theta",0,TMath::Pi()},
			 {"truPhi","truPhi","recPhi","#proton #phi",-TMath::Pi(),TMath::Pi()}};

  //variable to flag if particle was reconstructed in this event
  info.acceptVar = "accepted";

  //in case need further fltering of reconstructed events (e.g. truth matching,..)
  info.recFilter = "";


  info.WriteTo("training.root");


}