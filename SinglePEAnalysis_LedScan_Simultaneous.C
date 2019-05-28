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
#include "TLegend.h"
#include "TRandom.h"

#include <vector>
#include <iostream>

#include "Fit/Fitter.h"
#include "Fit/BinData.h"
#include "Fit/Chi2FCN.h"
#include "TH1.h"
#include "TList.h"
#include "Math/WrappedMultiTF1.h"
#include "HFitInterface.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "Math/GSLMinimizer.h"

//#include "Style.C"

#define START_ORDER 0
#define NORDERS 15

#define OFFSET 755
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
    retval += (par[2*nfun+4] - 2.)*(par[2*nfun+4] - 2.) * 4.;
    return  retval;
  }

  std::vector< ROOT::Math::IMultiGenFunction* > f_;
};

Double_t PMTFunction(Double_t *x, Double_t *par)
{

  float N = par[0];
  float mu = par[1];
  float Q1 = par[2];
  float sigma = par[3];
  float ped = par[4];
  float sigmaped = par[5];

  float xx = x[0];

  double value = 0.;
  for( unsigned i=START_ORDER; i<NORDERS; ++i ) {
    double sigma_n = sqrt( (double)(i)*sigma*sigma + sigmaped*sigmaped);
    double gauss = TMath::Gaus( xx, ((double)i*Q1 + ped), sigma_n, kTRUE) ;
    if (i!=0 && xx<(ped-par[6]*sigmaped))
      gauss = 0;
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
      ROOT::Fit::Chi2Function* chi2_1=new ROOT::Fit::Chi2Function(*(data[ifun]), *(wf[ifun]));
      chi2.push_back((ROOT::Math::IMultiGenFunction*) chi2_1);

      par0[2*ifun]= histos[ifun]->Integral(); //N
      par0[2*ifun+1]= 1; //mu

      nBins += (*(data[ifun])).Size();
    }

  GlobalChi2 globalChi2(chi2);

  par0[2*nHistos]=22; //Q1
  par0[2*nHistos+1]=11; //Q1 sigma
  par0[2*nHistos+2]=30; 
  par0[2*nHistos+3]=4.2; 
  par0[2*nHistos+4]=2; 

  // create before the parameter settings in order to fix or set range on them
  fitter.Config().SetParamsSettings(Npar,par0);
  //  fitter.GetMinimizer()->SetTolerance(0.001);
  // fix 5-th parameter  
  //fitter.Config().ParSettings(4).Fix();

  for (int ifun=0;ifun<nHistos;++ifun)
    fitter.Config().ParSettings(2*ifun+1).SetLimits(0.1, 5);
  
  fitter.Config().ParSettings(2*nHistos).SetLimits(15,30);
  fitter.Config().ParSettings(2*nHistos+1).SetLimits(10,20);
  fitter.Config().ParSettings(2*nHistos+2).SetLimits(25,32);
  fitter.Config().ParSettings(2*nHistos+3).SetLimits(3.5,4.5);
  fitter.Config().ParSettings(2*nHistos+4).SetLimits(1.,5.);
  
  ROOT::Math::MinimizerOptions fitopt;
  fitopt.SetTolerance(0.001);
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

void SinglePEAnalysis_LedScan_Simultaneous()
{
  TCanvas *c=new TCanvas("c","c",800,700);
  TFile* out=TFile::Open("SinglePEAnalysis_ledScan.root","RECREATE");
  //  TFile *f=TFile::Open("h4Reco_test100kevents.root");

  int led[7];
  int led_err[7];

  double x[7];
  double x_err[7];
  double pe[7];
  double pe_err[7];
  double gain[7];
  double gain_err[7];
  double peres[7];
  double peres_err[7];
  double mu[7];
  double mu_err[7];

  std::vector<TH1F*> adcData;
  TFile* f[7];

  for (int i=0;i<7;++i)
    {
      led[i]=4200+20*i;
      led_err[i]=0;
      x[i]=led[i];
      x_err[i]=led_err[i];
      f[i]=TFile::Open(Form("h4Reco_pmt1350led%d.root",led[i]));
      TTree* tree=(TTree*)f[i]->Get("h4");
      
      adcData.push_back(new TH1F(Form("ledData_led%d",led[i]),Form("ledData_led%d",led[i]),1200,0,300));
      tree->Project(Form("ledData_led%d",led[i]),"charge_tot[C0]");
      adcData[i]->Print();
    }

  
  //  std::cout << "FIT RANGE " << adcData[i]->GetMean()-3*adcData[i]->GetRMS() << "," << adcData[i]->GetMean()+3*adcData[i]->GetRMS() << std::endl;
  FitResults fr=fitSimultaneous(adcData,0,300);
      
  for (int i=0;i<7;++i)
    {
      pe[i]=fr.Q1;
      pe_err[i]=fr.Q1_err;
      gain[i]=fr.Q1*5E-10*1E-3/50/1.6E-19;
      gain_err[i]=fr.Q1_err*5E-10*1E-3/50/1.6E-19;
      peres[i]=fr.Q1_sigma/fr.Q1;
      peres_err[i]=fr.Q1_sigma/fr.Q1*sqrt((fr.Q1_err*fr.Q1_err)/(fr.Q1*fr.Q1)+(fr.Q1_sigma_err*fr.Q1_sigma_err)/(fr.Q1_sigma*fr.Q1_sigma));
      mu[i]=fr.mu[i];
      mu_err[i]=fr.mu_err[i];
      c->SetLogy(1);
      gStyle->SetOptStat(0);
      gStyle->SetOptFit(11111);
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
	  TF1* peFunc=new TF1(Form("peFunc_%d",ipe),"gaus",ipe!=0 ? fr.ped-fr.ped_sigma*fr.min_sigma : 0.,300);
	  peFunc->SetLineColor(1+ipe);
	  peFunc->SetLineWidth(2);
	  float mean=ipe*fr.Q1+fr.ped;
	  float sigma=sqrt(ipe*fr.Q1_sigma*fr.Q1_sigma+fr.ped_sigma*fr.ped_sigma);
	  peFunc->SetParameter(0,fr.norm[i]*TMath::Poisson(ipe,fr.mu[i])/(sqrt(2*TMath::Pi())*sigma));
	  peFunc->SetParameter(1,mean);
	  peFunc->SetParameter(2,sigma);
	  peFunc->SetNpx(1000);
	  peFunc->Draw("SAME");
	}
      
      out->cd();
      adcData[i]->Write(Form("adcData_led%d",led[i]));
      f->Write();
      c->Write(Form("singlePEfit_led%d.pdf",led[i]));
      c->SaveAs(Form("singlePEfit_led%d.pdf",led[i]));
    }


  c->SetLogy(0);
  TGraphErrors* muVsLed=new TGraphErrors(7,x,mu,x_err,mu_err);
  muVsLed->SetMarkerStyle(20);
  muVsLed->SetMarkerSize(1.1);
  muVsLed->GetXaxis()->SetTitle("Led (V)");
  muVsLed->GetYaxis()->SetTitle("#mu");
  muVsLed->GetYaxis()->SetRangeUser(0,7);
  muVsLed->Draw("APE");
  muVsLed->Fit("pol2");
  //  muVsLed->Write();
  
  c->SaveAs("muVsLed.pdf");
  out->Write();
}
