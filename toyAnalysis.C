{
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  TFile *_file0 = TFile::Open("shapeToy.root");

  _file0->cd("events");
  float max=-999;
  TH1F* frame=0;
  for(int iev=0;iev<20;++iev)
    {
      TH1F* event=(TH1F*)_file0->Get(Form("events/eventTriggered_%d",iev));
      if (iev==0)
	{
	  event->Draw();
	  frame=event;
	}
      else
      	event->Draw("SAME");
      if (event->GetBinContent(event->GetMaximumBin())>max)
	max=event->GetBinContent(event->GetMaximumBin());
    }
  frame->SetMaximum(max*1.2);
  frame->GetXaxis()->SetRangeUser(0,300);
  TH1F* averageTriggered=(TH1F*)_file0->Get("fullTriggered");
  averageTriggered->SetLineColor(kRed);
  averageTriggered->SetMarkerColor(kRed);
  averageTriggered->SetMarkerSize(0.9);
  averageTriggered->SetMarkerStyle(20);
  averageTriggered->SetLineWidth(4);
  averageTriggered->Draw("PSAME");

  //now fit the shape
  TF1* f2=new TF1("f2","[0]*((1-[4])*(TMath::Exp((-2*[1]*(x-[3])+[2]*[2])/2/[1]/[1])*(1-TMath::Erf((-[1]*(x-[3])+[2]*[2])/(TMath::Sqrt(2)*[1]*[2])))) + [4]* TMath::Exp((-2*[1]*(x-[3])+[5]*[5])/2/[1]/[1])*(1-TMath::Erf((-[1]*(x-[3])+[5]*[5])/(TMath::Sqrt(2)*[1]*[5]))))",0,500);
  f2->SetParameter(3,50);
  f2->SetParLimits(3,10,100);
  f2->SetParameter(2,4);
  f2->SetParLimits(2,3,10);
  f2->SetParameter(1,45);
  f2->SetParLimits(1,30,60);
  f2->SetParameter(0,180);
  f2->SetParLimits(0,0,500);
  f2->FixParameter(4,0);
  f2->FixParameter(5,0);

  gStyle->SetOptFit(11111);
  f2->SetNpx(10000);
  averageTriggered->Fit(f2,"LRB+","0",20,500);
  f2->SetLineColor(kMagenta);
  f2->SetLineWidth(4);
  f2->Draw("SAME");

  TLatex *text=new TLatex();
  text->DrawLatexNDC(0.4,0.8,Form("#tau_{sim}=45 ns"));
  text->DrawLatexNDC(0.6,0.8,Form("#tau_{fit}=%3.1f#pm%2.1f ns",f2->GetParameter(1),f2->GetParError(1)));
  text->DrawLatexNDC(0.4,0.74,Form("#sigma_{sim}=4 ns"));
  text->DrawLatexNDC(0.6,0.74,Form("#sigma_{fit}=%3.1f#pm%2.1f ns",f2->GetParameter(2),f2->GetParError(2)));
  
  frame->GetYaxis()->SetTitle("Amplitude (mv)");
  frame->GetXaxis()->SetTitle("Time (ns)");

  TString plotsDir = "~/cernbox/www/plots/LYBench/";

  c1->SaveAs(plotsDir+"eventsTriggered.pdf");
  c1->SaveAs(plotsDir+"eventsTriggered.png");

}
