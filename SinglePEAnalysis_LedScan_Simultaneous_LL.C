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

#include <vector>
#include <iostream>

#include "Fit/Fitter.h"
#include "Fit/BinData.h"
#include "Fit/Chi2FCN.h"
#include "Fit/PoissonLikelihoodFCN.h"
#include "TH1.h"
#include "TList.h"
#include "Math/WrappedMultiTF1.h"
#include "HFitInterface.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "Math/GSLMinimizer.h"

//#include "Style.C"

#define START_ORDER 0
#define NORDERS 24

#define OFFSET 755

//uncomment the following line to fix the PE response sigma to 0.59*PE according 
#define FIXED_SIGMA

struct FitResults {

  std::vector<float> norm;

  std::vector<float> mu;
  std::vector<float> mu_err;

  float Q1;
  float Q1_err;
  float Q1_sigma;
  float Q1_sigma_err;

  float ped;
  float ped_err;
  float ped_sigma;
  float ped_sigma_err;

  float min_sigma;
  float min_sigma_err;
};

int debug=0;

struct GlobalChi2 { 
  GlobalChi2(  std::vector< ROOT::Math::IMultiGenFunction* > f ) : 
    f_(f) { };
  
  // parameter vector is first background (in common 1 and 2) and then is signal (only in 2)
  double operator() (const double *par) const {
    double retval=0;
    int nfun=f_.size();
    for (int ifun=0;ifun<nfun;++ifun)
      {
	double p1[7]; 
	p1[0] = par[2*ifun]; 
	p1[1] = par[2*ifun+1]; 
	p1[2] = par[2*nfun]; 
	p1[3] = par[2*nfun+1]; 
	p1[4] = par[2*nfun+2]; 
	p1[5] = par[2*nfun+3]; 
	p1[6] = par[2*nfun+4]; 
	retval += (*f_[ifun])(p1);
      }
    retval += (par[2*nfun+4] + 1.4)*(par[2*nfun+4] + 1.4) * 10.;
    return  retval;
  }

  std::vector< ROOT::Math::IMultiGenFunction* > f_;
};

TString plotsDir = "SinglePEAnalysis";

Double_t PMTFunction(Double_t *x, Double_t *par)
{

  float N = par[0];
  float mu = par[1];
  float Q1 = par[2];
  float sigma = par[3];
  float ped = par[4];
  float sigmaped = par[5];
  float xx = x[0];

 #ifdef FIXED_SIGMA
  sigma=0.59*par[2];
#endif
  double value = 0.;
  double tot_frac = 0;

  for( unsigned i=1; i<NORDERS; ++i ) {
    double sigma_n = sqrt( (double)(i)*sigma*sigma + sigmaped*sigmaped);
    double gauss = 0;
    double fraction = (1.-TMath::Erf(( i*Q1 - par[6]*sigmaped )/(sqrt(2)*sigma_n)))*0.5;
    tot_frac+=fraction;
  }


  for( unsigned i=0; i<NORDERS; ++i ) {
    double sigma_n = sqrt( (double)(i)*sigma*sigma + sigmaped*sigmaped);
    double gauss = 0;

    if (i!=0 && xx<(ped+par[6]*sigmaped) )
      {
	double fraction = TMath::Gaus( ped+par[6]*sigmaped, ((double)i*Q1 + ped), sigma_n, kTRUE) / TMath::Gaus( ped+par[6]*sigmaped, ped, sigmaped, kTRUE); 
	gauss = fraction * TMath::Gaus( xx, ped, sigmaped, kTRUE); 
      }
    else if (i!=0)
      gauss = TMath::Gaus( xx, ((double)i*Q1 + ped), sigma_n, kTRUE) ;
    else if (i==0)
      gauss = TMath::Gaus( xx, ped, sigmaped, kTRUE);

    value += N*(TMath::Poisson( i, mu ) * gauss );
  }
  return value;
}

FitResults fitSimultaneous( std::vector<TH1F*> histos, double xMin, double xMax ) 
{
  FitResults fr;
  int nHistos=histos.size();

  std::vector<TF1*> fun;
  std::vector<ROOT::Math::WrappedMultiTF1*> wf;
  std::vector<ROOT::Fit::BinData*> data;
  std::vector< ROOT::Math::IMultiGenFunction* > chi2;

  ROOT::Fit::DataOptions opt; 
  ROOT::Fit::DataRange range; 
  range.SetRange(xMin,xMax);

  const int Npar = 2*nHistos + 5; //norm and mu for each histo, Q1, Q1_sigma, ped, ped_sigma, min_gain
  double par0[Npar]; 
  ROOT::Fit::Fitter fitter;

  int nBins=0;
  for (int ifun=0;ifun<nHistos;++ifun)
    {
      TF1* f = new TF1( Form("fPMT_%d",ifun) , PMTFunction, xMin, xMax, 7 );
      fun.push_back(f);

      ROOT::Math::WrappedMultiTF1* wf1= new ROOT::Math::WrappedMultiTF1(*f,1);
      wf.push_back(wf1);

      ROOT::Fit::BinData* data1=new ROOT::Fit::BinData(opt,range);
      data.push_back(data1);
      ROOT::Fit::FillData(*(data[ifun]), histos[ifun]);
      ROOT::Fit::PoissonLLFunction* chi2_1= new ROOT::Fit::PoissonLLFunction(*(data[ifun]), *(wf[ifun]));
//       ROOT::Fit::Chi2Function* chi2_1=new ROOT::Fit::Chi2Function(*(data[ifun]), *(wf[ifun]));
      chi2.push_back((ROOT::Math::IMultiGenFunction*) chi2_1);

      par0[2*ifun]= histos[ifun]->Integral()/2.; //N
      par0[2*ifun+1]= 1; //mu

      nBins += (*(data[ifun])).Size();
    }

  GlobalChi2 globalChi2(chi2);

  par0[2*nHistos]=20; //Q1
  par0[2*nHistos+1]=0.59*par0[2*nHistos]; //Q1 sigma
  par0[2*nHistos+2]=20; 
  par0[2*nHistos+3]=6 ; 
  par0[2*nHistos+4]=-1.5; 

  // create before the parameter settings in order to fix or set range on them
  fitter.Config().SetParamsSettings(Npar,par0);
  //  fitter.GetMinimizer()->SetTolerance(0.001);
  // fix 5-th parameter  
  //fitter.Config().ParSettings(4).Fix();

  for (int ifun=0;ifun<nHistos;++ifun)
    fitter.Config().ParSettings(2*ifun+1).SetLimits(0.1, 10);
  
  fitter.Config().ParSettings(2*nHistos).SetLimits(12,22);
#ifndef FIXED_SIGMA
  fitter.Config().ParSettings(2*nHistos+1).SetLimits(7,20);
 #else
  fitter.Config().ParSettings(2*nHistos+1).Fix();
#endif
  fitter.Config().ParSettings(2*nHistos+2).SetLimits(0,70);
  fitter.Config().ParSettings(2*nHistos+3).SetLimits(3.5, 8.);
  fitter.Config().ParSettings(2*nHistos+4).SetLimits(-5.,0.);

  ROOT::Math::MinimizerOptions fitopt;
  fitopt.SetTolerance(0.001);
  fitopt.SetErrorDef(0.5); 
  //  fitopt.Print();
  fitter.Config().SetMinimizerOptions(fitopt);  

  fitter.FitFCN(Npar,globalChi2,par0,nBins,kTRUE);
  ROOT::Fit::FitResult result = fitter.Result();
  result.Print(std::cout);

  for (int ifun=0;ifun<nHistos;++ifun)
    {
      fr.norm.push_back(result.Value(2*ifun));
      fr.mu.push_back(result.Value(2*ifun+1));
      fr.mu_err.push_back(result.Error(2*ifun+1));
    }

  fr.Q1= result.Value(2*nHistos);
  fr.Q1_err= result.Error(2*nHistos);
  fr.Q1_sigma= result.Value(2*nHistos+1);
  fr.Q1_sigma_err= result.Error(2*nHistos+1);
  fr.ped= result.Value(2*nHistos+2);
  fr.ped_err= result.Error(2*nHistos+2);
  fr.ped_sigma= result.Value(2*nHistos+3);
  fr.ped_sigma_err= result.Error(2*nHistos+3);
  fr.min_sigma= result.Value(2*nHistos+4);
  fr.min_sigma_err= result.Error(2*nHistos+4);

  return fr;
}

void SinglePEAnalysis_LedScan_Simultaneous_LL(TString inputDir, TString runId, bool longRun=true)
{
  // TString baseName(gSystem->BaseName(inputFile.Data()));
  // TString fileName;
  // TString runId;
  // Ssiz_t from = 0;
  // baseName.Tokenize(fileName, from, ".root");
  // from=0;
  // TString tok;
  // from = 0;
  // while (fileName.Tokenize(tok, from, "h4Reco_")) {
  //   runId=tok;
  // }

  TCanvas *c=new TCanvas("c","c",800,700);
  TFile* out=TFile::Open(Form("%s/%s_simul_out.root",plotsDir.Data(),runId.Data()),"RECREATE");
  TPaveText *pt=new TPaveText(0.5,0.6,0.9,0.9,"ndc");
  pt->SetBorderSize(0);

  int led[8];
  int led_err[8];

  double x[8];
  double x_err[8];
  double pe[8];
  double pe_err[8];
  double gain[8];
  double gain_err[8];
  double peres[8];
  double peres_err[8];
  double mu[8];
  double mu_err[8];

  std::vector<TH1F*> adcData;
  TFile* f[8];
  TH1F* pechar=new TH1F("singlePE", "singlePE", 60, 10,25);

  for (int i=0;i<5;++i)
    {
      led[i]=4180+20*i;
      led_err[i]=0;
      x[i]=led[i];
      x_err[i]=led_err[i];
      if (!longRun)
	{
	  f[i]=TFile::Open(Form("%s/h4Reco_%s-%d.root",inputDir.Data(),runId.Data(),led[i]));
	  TTree* tree=(TTree*)f[i]->Get("h4");
	  adcData.push_back(new TH1F(Form("ledData_led%d",led[i]),Form("ledData_led%d",led[i]),600,0,300));
	  tree->Project(Form("ledData_led%d",led[i]),"charge_tot[C0]");
	  //	  tree->Project(Form("ledData_led%d",led[i]),"charge_sig[C0]");
	  adcData[i]->Print();
	}
      else
	{
	  f[i]=TFile::Open(Form("%s/h4Reco_%s.root",inputDir.Data(),runId.Data()));
	  TTree* tree=(TTree*)f[i]->Get("h4");
	  adcData.push_back(new TH1F(Form("ledData_led%d",led[i]),Form("ledData_led%d",led[i]),600,0,300));
	  tree->Project(Form("ledData_led%d",led[i]),"charge_tot[C0]",Form("spill==%d",i+1));
	  //tree->Project(Form("ledData_led%d",led[i]),"charge_sig[C0]",Form("spill==%d",i+1));
	  adcData[i]->Print();
	}
    }

  
  //  std::cout << "FIT RANGE " << adcData[i]->GetMean()-3*adcData[i]->GetRMS() << "," << adcData[i]->GetMean()+3*adcData[i]->GetRMS() << std::endl;
  FitResults fr=fitSimultaneous(adcData,0,300);

  TLatex* text= new TLatex();
  text->SetTextSize(0.03);

  for (int i=0;i<5;++i)
    {
      pe[i]=fr.Q1;
      pechar->Fill(pe[i]);
      pe_err[i]=fr.Q1_err;
      gain[i]=fr.Q1*5E-10*1E-3/50/1.6E-19;
      gain_err[i]=fr.Q1_err*5E-10*1E-3/50/1.6E-19;
      peres[i]=fr.Q1_sigma/fr.Q1;
      peres_err[i]=fr.Q1_sigma/fr.Q1*sqrt((fr.Q1_err*fr.Q1_err)/(fr.Q1*fr.Q1)+(fr.Q1_sigma_err*fr.Q1_sigma_err)/(fr.Q1_sigma*fr.Q1_sigma));
      mu[i]=fr.mu[i];
      mu_err[i]=fr.mu_err[i];
      c->SetLogy(1);
      gStyle->SetOptTitle(0);
      gStyle->SetOptStat(0);
      gStyle->SetOptFit(0);
      adcData[i]->SetMarkerStyle(20);
      adcData[i]->SetMarkerSize(0.6);
      adcData[i]->SetMarkerColor(kBlack);
      adcData[i]->SetLineColor(kBlack);
      adcData[i]->Draw("PE");
      adcData[i]->GetXaxis()->SetTitle("Charge [ADC Counts]");
      TF1* f = new TF1( Form("PMT_%d",i) , PMTFunction, 0, 300, 7 );
      f->SetParameter(0,fr.norm[i]);
      f->SetParameter(1,fr.mu[i]);
      f->SetParameter(2,fr.Q1);
      f->SetParameter(3,fr.Q1_sigma);
      f->SetParameter(4,fr.ped);
      f->SetParameter(5,fr.ped_sigma);
      f->SetParameter(6,fr.min_sigma);
      f->SetLineColor(kOrange);
      f->SetLineWidth(3);
      f->SetNpx(1000);
      f->Draw("SAME");
      
      for (int ipe=0; ipe<10;++ipe)
	{
	  //	  TF1* peFunc=new TF1(Form("peFunc_%d",ipe),"gaus",ipe!=0 ? fr.ped+fr.ped_sigma*fr.min_sigma : 0.,300);
	  TF1* peFunc=new TF1(Form("peFunc_%d",ipe),"gaus",0.,300);
	  peFunc->SetLineColor(1+ipe);
	  peFunc->SetLineStyle(kDashed);
	  peFunc->SetLineWidth(2);
	  float mean=ipe*fr.Q1+fr.ped;
	  float sigma=sqrt(ipe*fr.Q1_sigma*fr.Q1_sigma+fr.ped_sigma*fr.ped_sigma);
	  peFunc->SetParameter(0,fr.norm[i]*TMath::Poisson(ipe,fr.mu[i])/(sqrt(2*TMath::Pi())*sigma));
	  peFunc->SetParameter(1,mean);
      	  peFunc->SetParameter(2,sigma);
	  peFunc->SetNpx(1000);
	  peFunc->Draw("SAME");
	}
      //adcData[i]->Draw("PESAME");
      out->cd();
      adcData[i]->Write(Form("adcData_led%d",led[i]));
      f->Write();
      pt->SetFillColorAlpha(kWhite, 0);
      pt->AddText(Form("#mu= %.3f #pm %.4f",mu[i], mu_err[i])); 
      pt->AddText(Form("PE charge = %.2f #pm %.2f",pe[i], pe_err[i])); 
      pt->AddText(Form("Pedestal = %.2f #pm %.2f",fr.ped, fr.ped_err));
      pt->AddText(Form("Noise = %.2f #pm %.3f",fr.ped_sigma, fr.ped_sigma_err));
      pt->Draw("SAME");
      text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s     LED Voltage: %3.2f V",runId.Data(),led[i]/1000.));
      c->Write(Form("%s/singlePEfit_%s_led%d.root",plotsDir.Data(),runId.Data(),led[i]));
      c->SaveAs(Form("%s/singlePEfit_%s_led%d.pdf",plotsDir.Data(),runId.Data(),led[i]));
      //      c->SaveAs(Form("%s/singlePEfit_led%d.png",plotsDir.Data(),led[i]));
      pt->Clear();
    }


  c->SetLogy(0);
  TGraphErrors* muVsLed=new TGraphErrors(5,x,mu,x_err,mu_err);
  muVsLed->SetMarkerStyle(20);
  muVsLed->SetMarkerSize(1.1);
  muVsLed->GetXaxis()->SetTitle("Led Amplitude (mV)");
  muVsLed->GetYaxis()->SetTitle("#mu");
  muVsLed->GetYaxis()->SetRangeUser(0,10);
  muVsLed->Draw("APE");
  muVsLed->Fit("pol2");
  //  muVsLed->Write();
  text->DrawLatexNDC(0.12,0.91,Form("Run ID: %s",runId.Data()));
  c->SaveAs(Form("%s/muVsLed_%s.pdf",plotsDir.Data(),runId.Data()));
  //  c->SaveAs(Form("%s/muVsLed.png",plotsDir.Data()));
  out->Write();
  out->cd();
  pechar->Write("singlePE");
}
