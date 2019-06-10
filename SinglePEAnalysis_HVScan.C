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

//#include "Style.C"

#define START_ORDER 0
#define NORDERS 6

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
  f1->SetParameter( 4, 27. ); //offset
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
   f1->SetParLimits( 4, 20, 40.); //offset
   f1->SetParLimits( 5, 4., 4.5 ); //gauss sigma

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


void SinglePEAnalysis()
{
  TCanvas *c=new TCanvas("c","c",800,700);
  TFile* out=TFile::Open("SinglePEAnalysis.root","RECREATE");
  //  TFile *f=TFile::Open("h4Reco_test100kevents.root");

  int HV[9];
  int HV_err[9];

  double x[9];
  double x_err[9];
  double pe[9];
  double pe_err[9];
  double gain[9];
  double gain_err[9];
  double peres[9];
  double peres_err[9];
  double mu[9];
  double mu_err[9];

  for (int i=0;i<9;++i)
    {
      HV[i]=1350-25*i;
      HV_err[i]=0;
      x[i]=HV[i];
      x_err[i]=HV_err[i];
      TFile *f=TFile::Open(Form("h4Reco_calib%dV.root",HV[i]));
      TTree* tree=(TTree*)f->Get("h4");
      
      TH1F* adcData= new TH1F("ledData","ledData",400,0,200);
      tree->Project("ledData","charge_tot[C0]");
      adcData->Print();
      //  std::cout << "FIT RANGE " << adcData->GetMean()-3*adcData->GetRMS() << "," << adcData->GetMean()+3*adcData->GetRMS() << std::endl;
      FitResults fr=fitSingleHisto(adcData,16,160);
      pe[i]=fr.Q1;
      pe_err[i]=fr.Q1_err;
      gain[i]=fr.Q1*5E-10*1E-3/50/1.6E-19;
      gain_err[i]=fr.Q1_err*5E-10*1E-3/50/1.6E-19;
      peres[i]=fr.sigma/fr.Q1;
      peres_err[i]=fr.sigma/fr.Q1*sqrt((fr.Q1_err*fr.Q1_err)/(fr.Q1*fr.Q1)+(fr.sigma_err*fr.sigma_err)/(fr.sigma*fr.sigma));
      mu[i]=fr.mu;
      mu_err[i]=fr.mu_err;
      c->SetLogy(1);
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
	  float sigma_pe=sqrt(ipe*adcData->GetFunction("fPMT")->GetParameter(3)*adcData->GetFunction("fPMT")->GetParameter(3)+adcData->GetFunction("fPMT")->GetParameter(5)*adcData->GetFunction("fPMT")->GetParameter(5));
	  peFunc->SetParameter(0,adcData->GetFunction("fPMT")->GetParameter(0)*TMath::Poisson(ipe,adcData->GetFunction("fPMT")->GetParameter(1))/(sqrt(2*TMath::Pi())*sigma_pe));
	  peFunc->SetParameter(1,mu_pe);
	  peFunc->SetParameter(2,sigma_pe);
	  peFunc->Draw("SAME");
	}
      
      out->cd();
      adcData->Write(Form("adcData_%dV",HV[i]));
      c->SaveAs(Form("singlePEfit_%dV.pdf",HV[i]));
    }

  TGraphErrors* peVsHV=new TGraphErrors(9,x,pe,x_err,pe_err);
  c->SetLogy(1);
  peVsHV->Draw("APE");
  gStyle->SetOptTitle(0);
  gStyle->SetOptFit(1111);
  TF1* peVsHVFunc=new TF1("peVsHVFunc","TMath::Power([0]*x,[1])",1100,1400);
  //  peVsHVFunc->SetParameter(0,0.01);
  peVsHVFunc->SetParameter(0,1E-5);
  peVsHVFunc->SetParameter(1,2);
  peVsHV->SetMarkerStyle(20);
  peVsHV->SetMarkerSize(1.1);
  peVsHV->GetXaxis()->SetTitle("HV (V)");
  peVsHV->GetYaxis()->SetTitle("PE response (ADC)");
  peVsHV->GetYaxis()->SetRangeUser(2,50);
  peVsHV->Fit( peVsHVFunc, "R+");
  c->SaveAs("peVsHV.pdf");
  peVsHV->Write("peVsHV");

  TGraphErrors* gainVsHV=new TGraphErrors(9,x,gain,x_err,gain_err);
  c->SetLogy(1);
  gainVsHV->Draw("APE");
  gStyle->SetOptTitle(0);
  gStyle->SetOptFit(1111);
  TF1* gainVsHVFunc=new TF1("gainVsHVFunc","TMath::Power([0]*x,[1])",1100,1400);
  //  gainVsHVFunc->SetParameter(0,0.01);
  gainVsHVFunc->SetParameter(0,1);
  gainVsHVFunc->SetParameter(1,2);
  gainVsHV->SetMarkerStyle(20);
  gainVsHV->SetMarkerSize(1.1);
  gainVsHV->GetXaxis()->SetTitle("HV (V)");
  gainVsHV->GetYaxis()->SetTitle("Gain");
  gainVsHV->GetYaxis()->SetRangeUser(2E5,5E6);
  gainVsHV->Fit( gainVsHVFunc, "R+");
  c->SaveAs("gainVsHV.pdf");
  gainVsHV->Write("gainVsHV");

  c->SetLogy(0);

  TGraphErrors* peResVsHV=new TGraphErrors(9,x,peres,x_err,peres_err);
  peResVsHV->SetMarkerStyle(20);
  peResVsHV->SetMarkerSize(1.1);
  peResVsHV->GetXaxis()->SetTitle("HV (V)");
  peResVsHV->GetYaxis()->SetTitle("SPR Resolution");
  peResVsHV->GetYaxis()->SetRangeUser(0,1);
  peResVsHV->Draw("APE");
  peResVsHV->Fit("pol0");
  c->SaveAs("peResVsHV.pdf");

  TGraphErrors* peResVsGain=new TGraphErrors(9,gain,peres,gain_err,peres_err);
  peResVsGain->SetMarkerStyle(20);
  peResVsGain->SetMarkerSize(1.1);
  peResVsGain->GetXaxis()->SetTitle("Gain");
  peResVsGain->GetYaxis()->SetTitle("SPR Resolution");
  peResVsGain->GetYaxis()->SetRangeUser(0,1);
  peResVsGain->Draw("APE");
  peResVsGain->Fit("pol0");
  c->SaveAs("peResVsGain.pdf");

  TGraphErrors* muVsHV=new TGraphErrors(9,x,mu,x_err,mu_err);
  muVsHV->SetMarkerStyle(20);
  muVsHV->SetMarkerSize(1.1);
  muVsHV->GetXaxis()->SetTitle("HV (V)");
  muVsHV->GetYaxis()->SetTitle("#mu");
  muVsHV->GetYaxis()->SetRangeUser(0,1);
  muVsHV->Draw("APE");
  muVsHV->Fit("pol0");
  c->SaveAs("muVsHV.pdf");

  out->Write();
}
