 #include "TH1F.h"
 #include "TF1.h"
 #include "TFile.h"
 #include "TString.h"
 #include "TTree.h"
 #include "TStyle.h"
 #include "TGraphErrors.h"
 #include "TCanvas.h"
 #include "TMath.h"
 #include "TH2D.h"
 #include "TPaveText.h"
 #include "TLatex.h"
 #include "TLegend.h"
 #include "TRandom.h"
 #include "TSystem.h"

 #include <vector>
 #include <iostream>

 //#include "Style.C"

 #define START_ORDER 0
 #define NORDERS 24

 #define OFFSET 755
 struct FitResults {

   float ped_mu;
   float ped_mu_err;
   float ped_sigma;
   float ped_sigma_err;

   float mu;
   float mu_err;
   float offset;
   float offset_err;
   float Q1;
   float Q1_err;
   float sigma;
   float sigma_err;

 };

 Double_t PMTFunction(Double_t *x, Double_t *par)
 {

   float N = par[0];
   float mu = par[1];
   float Q1 = par[2];
   float sigma = par[3];
   float offset = par[4];
   float sigmaoffset = par[5];
 //   float alpha = par[6];
 //   float w = par[7];
 //   float frac = par[8];

   float xx = x[0];
   double value = 0.;

   //fixing width according to PMT resolution
   sigma=par[2]*0.59; 

   for( unsigned i=START_ORDER; i<NORDERS; ++i ) {

     //double Qn = offset + (double)(i)*Q1;
     double sigma_n = sqrt( (double)(i)*sigma*sigma + sigmaoffset*sigmaoffset);

     //double poisson = TMath::Poisson( i, mu );
     //double gauss   = TMath::Gaus( xx, Qn, sigma_n );

     //double xxp = xx     - Qn - alpha*sigma_n*sigma_n;
     //double Q0p = offset - Qn - alpha*sigma_n*sigma_n;
     //double bg      = 0.5*alpha * TMath::Exp(-alpha*xxp)* (
     //                     TMath::Erf( abs(Q0p)/(sigma_n*sqrt(2) ) ) +  xxp/abs(xxp) * TMath::Erf( abs(xxp)/(sigma_n*sqrt(2)) ) );
     //value = value + N*( poisson * ( (1.-w)*gauss + w*bg ) );
     float norm;
 //     if (i==0)
 //       norm=N*(1+frac);
 //     else
     norm=N;
     value += norm*(TMath::Poisson( i, mu ) * TMath::Gaus( xx, ((double)i*Q1 + offset), sigma_n, kTRUE) );
     //value = value + N*(TMath::Poisson( i, mu ) * TMath::Gaus( xx, (double)i*Q1 + offset, sqrt((double)i)*sigma ));
   }

   return value;

 }

 FitResults fitSingleHisto( TH1F* histo, double xMin, double xMax ) 
 {
   FitResults fr;
   TF1* f1 = new TF1( "fPMT", PMTFunction, xMin, xMax, 6 );
   f1->SetParameter( 0, histo->Integral()); //normalization
   f1->SetParameter( 1, 0.4); //poiss mu
   f1->SetParameter( 2, 20. ); //gauss step
   f1->SetParameter( 3, 10. ); //gauss sigma
   f1->SetParameter( 4, 40. ); //offset
   f1->SetParameter( 5, 4. ); //sigmaoffset
 //   f1->SetParameter( 6, 0.03 ); //alpha
 //   f1->SetParameter( 7, 0.4 ); //w
 //   f1->SetParameter( 8, 0.3 ); //w

   f1->SetParName(0,"Norm");
   f1->SetParName(1,"#mu");
   f1->SetParName(2,"PE charge");
   f1->SetParName(3,"PE resolution");
   f1->SetParName(4,"Pedestal");
   f1->SetParName(5,"Noise");
   // f1->FixParameter( 1, 1. ); //mu
   //   f1->FixParameter( 2, 29.5 ); //Q1
   //   //  f1->FixParameter( 3, 14.3 ); //sigmaQ1
   //   f1->FixParameter( 4, 0. ); //offset
   //   f1->FixParameter( 5, 0. ); //sigmaoffset
   //    f1->FixParameter( 6, 0. ); //alpha
   //    f1->FixParameter( 7, 0. ); //w
   //    f1->FixParameter( 8, 0. ); //w

    f1->SetParLimits( 1, 0.1, 5.  ); //poiss mu
    f1->SetParLimits( 2, 5., 40. ); //gauss step
    f1->SetParLimits( 3, 3., 30. ); //gauss sigma
    f1->SetParLimits( 4, 10, 70.); //offset
    f1->SetParLimits( 5, 3., 6. ); //gauss sigma

   f1->FixParameter( 3, 0. ); //removing unused parameter

   f1->SetLineColor(kBlue+1);
   f1->SetLineWidth(2);


   histo->Fit( f1, "LR+" );
   TString histoName(histo->GetName());

   fr.mu = f1->GetParameter(1);
   fr.mu_err = f1->GetParError(1);
   fr.Q1= f1->GetParameter(2);
   fr.Q1_err= f1->GetParError(2);
   fr.sigma=f1->GetParameter(3);
   fr.sigma_err= f1->GetParError(3);
   delete f1;
   return fr;
 }


 void SinglePEAnalysis_longRun(TString inputFile,bool longRun=false,bool fromHistos=false)
 {
   TString baseName(gSystem->BaseName(inputFile.Data()));
   TString fileName;
   TString runId;
   Ssiz_t from = 0;
   baseName.Tokenize(fileName, from, ".root");
   from=0;
   TString tok;
   from = 0;
   while (fileName.Tokenize(tok, from, "h4Reco_")) {
     runId=tok;
   }

   TCanvas *c=new TCanvas("c","c",800,700);
   TFile* out=TFile::Open(Form("SinglePEAnalysis/%s_out.root",runId.Data()),"RECREATE");
   //  TFile *f=TFile::Open("h4Reco_test100kevents.root");

   double x[200];
   double x_err[200];
   double tb[200];
   double tb_err[200];
   double tl[200];
   double tl_err[200];
   double pe[200];
   double pe_err[200];
   double gain[200];
   double gain_err[200];
   double peres[200];
   double peres_err[200];
   double mu[200];
   double mu_err[200];

   TFile *f=TFile::Open(inputFile);
   TTree* tree=NULL;

   if (!fromHistos)
     tree=(TTree*)f->Get("h4");

   TH1F* spills=NULL;

   if(!fromHistos)
     {
       spills=new TH1F("spill","spill",200,-0.5,199.5);
       tree->Project("spill","spill");
     }
   else
     spills=(TH1F*)f->Get("spill");

   int ispill=0;

   int maxSpill=longRun ? spills->GetNbinsX() : 1;

   TLatex* text= new TLatex();
   text->SetTextSize(0.03);

   for(int ibin=1;ibin<=maxSpill;++ibin)
     {
       TH1F* adcData=NULL;
       TH1F* tBench=NULL;
       TH1F* tLab=NULL;

       if (longRun && (spills->GetBinContent(ibin)<1000 || ispill>=200) )
	 continue;

       if (!fromHistos)
	 {
	   adcData=new TH1F(Form("charge_spill%d",ibin-1),Form("charge_spill%d",ibin-1),400,0,200);
	   if (longRun)
	     tree->Project(Form("charge_spill%d",ibin-1),"charge_tot[C0]",Form("spill==%d",ibin-1));
	    //tree->Project(Form("charge_spill%d",ibin-1),"charge_sig[C0]+10",Form("spill==%d",ibin-1));
	  else
	    tree->Project(Form("charge_spill%d",ibin-1),"charge_tot[C0]");
	    //	    tree->Project(Form("charge_spill%d",ibin-1),"charge_sig[C0]+10");
	}
      else
	{
	  adcData=(TH1F*)f->Get(Form("charge_spill%d",ibin-1));
	  tBench=(TH1F*)f->Get(Form("tBench_spill%d",ibin-1));
	  tLab=(TH1F*)f->Get(Form("tLab_spill%d",ibin-1));
	}
      
      adcData->SetMinimum(0.1);
      adcData->Print();
      //  std::cout << "FIT RANGE " << adcData->GetMean()-3*adcData->GetRMS() << "," << adcData->GetMean()+3*adcData->GetRMS() << std::endl;
      FitResults fr=fitSingleHisto(adcData,0,160);
      x[ispill]=ibin-1;
      x_err[ispill]=0;
      if (tBench)
	{
	  tb[ispill]=tBench->GetMean();
	  tb_err[ispill]=tBench->GetRMS();
	}
      if (tLab)
	{
	  tl[ispill]=tLab->GetMean();
	  tl_err[ispill]=tLab->GetRMS();
	}
      
      pe[ispill]=fr.Q1;
      pe_err[ispill]=fr.Q1_err;
      gain[ispill]=fr.Q1*5E-10*1E-3/50/1.6E-19;
      gain_err[ispill]=fr.Q1_err*5E-10*1E-3/50/1.6E-19;
      peres[ispill]=fr.sigma/fr.Q1;
      peres_err[ispill]=fr.sigma/fr.Q1*sqrt((fr.Q1_err*fr.Q1_err)/(fr.Q1*fr.Q1)+(fr.sigma_err*fr.sigma_err)/(fr.sigma*fr.sigma));
      mu[ispill]=fr.mu;
      mu_err[ispill]=fr.mu_err;
      c->SetLogy(1);
      gStyle->SetOptTitle(0);
      gStyle->SetOptStat(0);
      gStyle->SetOptFit(11111);
      adcData->SetMarkerStyle(20);
      adcData->SetMarkerSize(0.6);
      adcData->SetMarkerColor(kBlack);
      adcData->SetLineColor(kBlack);
      adcData->Draw("PE");
      adcData->GetXaxis()->SetTitle("Charge [ADC Counts]");
      
      for (int ipe=0; ipe<4;++ipe)
	{
	  TF1* peFunc=new TF1(Form("peFunc_%d",ipe),"gaus",0,200);
	  peFunc->SetLineColor(1+ipe);
	  peFunc->SetLineWidth(2);
	  float mu_pe=ipe*adcData->GetFunction("fPMT")->GetParameter(2)+adcData->GetFunction("fPMT")->GetParameter(4);
	  //	      float sigma_pe=sqrt(ipe*adcData->GetFunction("fPMT")->GetParameter(3)*adcData->GetFunction("fPMT")->GetParameter(3)+adcData->GetFunction("fPMT")->GetParameter(5)*adcData->GetFunction("fPMT")->GetParameter(5));
	  float sigma_pe=sqrt(ipe*0.59*0.59*adcData->GetFunction("fPMT")->GetParameter(2)*adcData->GetFunction("fPMT")->GetParameter(2)+adcData->GetFunction("fPMT")->GetParameter(5)*adcData->GetFunction("fPMT")->GetParameter(5));
	  peFunc->SetParameter(0,adcData->GetFunction("fPMT")->GetParameter(0)*TMath::Poisson(ipe,adcData->GetFunction("fPMT")->GetParameter(1))/(sqrt(2*TMath::Pi())*sigma_pe));
	  peFunc->SetParameter(1,mu_pe);
	  peFunc->SetParameter(2,sigma_pe);
	  peFunc->Draw("SAME");
	}
	  
      out->cd();
      adcData->Write(Form("charge_%s_spill%d",runId.Data(),ibin-1));
      if (fromHistos)
	{
	  tBench->Write(Form("tBench_%s_spill%d",runId.Data(),ibin-1));
	  tLab->Write(Form("tLab_%s_spill%d",runId.Data(),ibin-1));
	}
      text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s     Spill: %d",runId.Data(),ibin-1));
      c->SaveAs(Form("SinglePEAnalysis/singlePEfit_%s_%d.pdf",runId.Data(),ibin-1));
      ++ispill;
    }

  if (longRun)
    {
      TGraphErrors* peVsSpill=new TGraphErrors(ispill,x,pe,x_err,pe_err);
      c->SetLogy(0);
      peVsSpill->Draw("APE");
      gStyle->SetOptTitle(0);
      gStyle->SetOptFit(1111);
      TF1* peVsSpillFunc=new TF1("peVsSpillFunc","TMath::Power([0]*x,[1])",1100,1400);
      //  peVsSpillFunc->SetParameter(0,0.01);
      peVsSpillFunc->SetParameter(0,1E-5);
      peVsSpillFunc->SetParameter(1,2);
      peVsSpill->SetMarkerStyle(20);
      peVsSpill->SetMarkerSize(1.1);
      peVsSpill->GetXaxis()->SetTitle("#Spill");
      peVsSpill->GetYaxis()->SetTitle("PE response (ADC)");
      peVsSpill->GetYaxis()->SetRangeUser(13,25);
      peVsSpill->Fit( "pol0" );
      text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
      c->SaveAs(Form("SinglePEAnalysis/peVsSpill_%s.pdf",runId.Data()));
      peVsSpill->Write("peVsSpill");

      if (fromHistos)
	{
	  TGraphErrors* peVsTBench=new TGraphErrors(ispill,tb,pe,tb_err,pe_err);
	  c->SetLogy(0);
	  peVsTBench->Draw("APE");
	  gStyle->SetOptTitle(0);
	  gStyle->SetOptFit(1111);
	  peVsTBench->SetMarkerStyle(20);
	  peVsTBench->SetMarkerSize(1.1);
	  peVsTBench->GetXaxis()->SetTitle("Bench Temperature (#degreeC)");
	  peVsTBench->GetYaxis()->SetTitle("PE response (ADC)");
	  peVsTBench->GetYaxis()->SetRangeUser(13,25);
	  peVsTBench->Fit( "pol1" );
	  text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
	  c->SaveAs(Form("SinglePEAnalysis/peVsTBench_%s.pdf",runId.Data()));
	  peVsTBench->Write("peVsTBench");

	  TGraphErrors* tbVsSpill=new TGraphErrors(ispill,x,tb,x_err,tb_err);
	  c->SetLogy(0);
	  tbVsSpill->Draw("APEL");
	  gStyle->SetOptTitle(0);
	  gStyle->SetOptFit(1111);
	  tbVsSpill->SetMarkerStyle(20);
	  tbVsSpill->SetMarkerSize(1.1);
	  tbVsSpill->GetXaxis()->SetTitle("#Spill");
	  tbVsSpill->GetYaxis()->SetTitle("TBench (#degreeC)");
	  tbVsSpill->GetYaxis()->SetRangeUser(19,30);
	  text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
	  c->SaveAs(Form("SinglePEAnalysis/tbVsSpill_%s.pdf",runId.Data()));
	  tbVsSpill->Write("TBenchVsSpill");
	}

      TGraphErrors* gainVsSpill=new TGraphErrors(ispill,x,gain,x_err,gain_err);
      c->SetLogy(0);
      gainVsSpill->Draw("APE");
      gStyle->SetOptTitle(0);
      gStyle->SetOptFit(1111);
      TF1* gainVsSpillFunc=new TF1("gainVsSpillFunc","TMath::Power([0]*x,[1])",1100,1400);
      //  gainVsSpillFunc->SetParameter(0,0.01);
      gainVsSpillFunc->SetParameter(0,1);
      gainVsSpillFunc->SetParameter(1,2);
      gainVsSpill->SetMarkerStyle(20);
      gainVsSpill->SetMarkerSize(1.1);
      gainVsSpill->GetXaxis()->SetTitle("#Spill");
      gainVsSpill->GetYaxis()->SetTitle("Gain");
      gainVsSpill->GetYaxis()->SetRangeUser(2E5,5E6);
      gainVsSpill->Fit( "pol0" );
      text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
      c->SaveAs(Form("SinglePEAnalysis/gainVsSpill_%s.pdf",runId.Data()));
      gainVsSpill->Write("gainVsSpill");

      c->SetLogy(0);

      TGraphErrors* peResVsSpill=new TGraphErrors(ispill,x,peres,x_err,peres_err);
      peResVsSpill->SetMarkerStyle(20);
      peResVsSpill->SetMarkerSize(1.1);
      peResVsSpill->GetXaxis()->SetTitle("#Spill");
      peResVsSpill->GetYaxis()->SetTitle("SPR Resolution");
      peResVsSpill->GetYaxis()->SetRangeUser(0,1);
      peResVsSpill->Draw("APE");
      peResVsSpill->Fit("pol0");
      text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
      c->SaveAs(Form("SinglePEAnalysis/peResVsSpill_%s.pdf",runId.Data()));

      TGraphErrors* peResVsGain=new TGraphErrors(ispill,gain,peres,gain_err,peres_err);
      peResVsGain->SetMarkerStyle(20);
      peResVsGain->SetMarkerSize(1.1);
      peResVsGain->GetXaxis()->SetTitle("Gain");
      peResVsGain->GetYaxis()->SetTitle("SPR Resolution");
      peResVsGain->GetYaxis()->SetRangeUser(0,1);
      peResVsGain->Draw("APE");
      peResVsGain->Fit("pol0");
      text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
      c->SaveAs(Form("SinglePEAnalysis/peResVsGain_%s.pdf",runId.Data()));

      TGraphErrors* muVsSpill=new TGraphErrors(ispill,x,mu,x_err,mu_err);
      muVsSpill->SetMarkerStyle(20);
      muVsSpill->SetMarkerSize(1.1);
      muVsSpill->GetXaxis()->SetTitle("#Spill");
      muVsSpill->GetYaxis()->SetTitle("#mu");
      muVsSpill->GetYaxis()->SetRangeUser(0,2);
      muVsSpill->Draw("APE");
      muVsSpill->Fit("pol0");
      text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
      c->SaveAs(Form("SinglePEAnalysis/muVsSpill_%s.pdf",runId.Data()));
    }
  out->Write();
}
