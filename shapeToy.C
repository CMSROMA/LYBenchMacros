{
  int nEvents=1000;
  float lightYield=1000.;
  float lightYieldResolution=0.1;
  float tMean=50;
  float tRes=4;
  float triggerThreshold=40;
  float decayTime=45;

  //average current profile from PMT
  TProfile full("full","full",1200,0,600);
  TProfile fullTriggered("fullTriggered","fullTriggered",1200,0,600);

  //scintillation decay function
  TF1 *f=new TF1("f","TMath::Exp(-x/[0])",0,600);
  f->SetParameter(0,decayTime);

  TFile *fOut=new TFile("shapeToy.root","RECREATE");
  fOut->mkdir("events");
  fOut->cd("events");

  for (int i=0;i<nEvents;++i)
    {
      int nph=gRandom->Gaus(lightYield,lightYieldResolution*lightYield);

      //photo current for this event from the PMT (convoluting exp decay with gaussian PMT response)x
      TH1F current("event","event",1200,0,600);
      for (int ipho=0;ipho<nph;++ipho)
	{
	  float t=f->GetRandom();
	  TF1 g("g","TMath::Gaus(x,[0],[1])",0,600);
	  g.SetParameter(0,tMean+t);
	  g.SetParameter(1,tRes);
	  for (int ib=1;ib<current.GetNbinsX();++ib)
	    {
	      float i=g.Eval(current.GetBinCenter(ib));
	      current.Fill(current.GetBinCenter(ib),i);
	    }
	}

      for (int ib=1;ib<current.GetNbinsX();++ib)
	current.SetBinError(ib,0);

      //find trigger time
      TH1F* currentTriggered=(TH1F*)current.Clone("eventTriggered");
      int triggerSample=-1;
      for (int ib=1;ib<current.GetNbinsX();++ib)
	if (current.GetBinContent(ib)>triggerThreshold)
	  {
	    triggerSample=ib-1;
	    break;
	  }

      //skio events without a valid trigger
      if (triggerSample==-1)
	continue;

      //optimised to have ~maximum of triggered function not too far off
      triggerSample=triggerSample-60;
      
      //shift current according to trigger time
      for (int ib=1;ib<current.GetNbinsX();++ib)
	{
	  if (ib+triggerSample<=current.GetNbinsX())
	    {
	      currentTriggered->SetBinContent(ib,currentTriggered->GetBinContent(ib+triggerSample));
	      currentTriggered->SetBinError(ib,0);
	    }
	  else
	    {
	      currentTriggered->SetBinContent(ib,0);
	      currentTriggered->SetBinError(ib,0);
	    }
	}
      
      //now fill the average function
      for (int ib=1;ib<=current.GetNbinsX();++ib)
	{
	  full.Fill(current.GetBinCenter(ib),current.GetBinContent(ib));
	  fullTriggered.Fill(currentTriggered->GetBinCenter(ib),currentTriggered->GetBinContent(ib));
	}

      //Save first 100 events
      if (i<100)
	{
	  current.Write(Form("event_%d",i));
	  currentTriggered->Write(Form("eventTriggered_%d",i));
	}
      delete currentTriggered;
    }

  fOut->cd("/");
  full.Write();
  fullTriggered.Write();

  fOut->Close();
}
