import ROOT as R
import math as m
import os

R.gROOT.SetBatch(1)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input',dest='input')
parser.add_argument('--output',dest='output')
args = parser.parse_args()

c=R.TCanvas("c","c",900,700)
f=R.TFile(args.input)

charge=R.TH1F("charge","charge",1000,1000,101000)

h4=f.Get("h4")
h4.Project("charge","charge_tot[C0]")

#get some inputs from the spectrum to set the par limits
peak=charge.GetBinCenter(charge.GetMaximumBin())
norm=float(charge.GetEntries())/charge.GetNbinsX()

if (peak>20000):
    fTot=R.TF1("fTot","[0]*(1./(1+TMath::Exp([1]*(x-[2])))+[3]*TMath::Gaus(x,[4],[5])+[6]/(1+TMath::Exp([7]*(x-[8])))+[9]*TMath::Gaus(x,[10],[11])+[12]*TMath::Gaus(x,[13],[14])+[15]*TMath::Gaus(x,[16],[17]))",0,100000)
    fBkg=R.TF1("fBkg","[0]*(1./(1+TMath::Exp([1]*(x-[2])))+[3]*TMath::Gaus(x,[4],[5])+[6]/(1+TMath::Exp([7]*(x-[8])))+[9]*TMath::Gaus(x,[10],[11])+[12]*TMath::Gaus(x,[13],[14]))",0,100000)
    fTot.SetNpx(100000)
    fBkg.SetNpx(100000)

    fTot.SetParameter(0,norm*0.3)
    fTot.SetParLimits(0,norm*0.1,norm)
#1274 KeV compton 
    fTot.SetParameter(1,0.0015)
    fTot.SetParLimits(1,0.0005,0.003)
    fTot.SetParameter(2,1.7*peak)
    fTot.SetParLimits(2,1.5*peak,1.9*peak)
#1274 KeV "photo-electric" 
    fTot.SetParameter(3,2.)
    fTot.SetParLimits(3,0.5,3.)
    fTot.SetParameter(4,2*peak)
    fTot.SetParLimits(4,1.8*peak,2.2*peak)
    fTot.SetParameter(5,0.1*peak)
    fTot.SetParLimits(5,0.03*peak,0.2*peak)
#511 KeV compton
    fTot.SetParameter(6,4.5)
    fTot.SetParLimits(6,2,20.)
    fTot.SetParameter(7,0.003)
    fTot.SetParLimits(7,0.0001,0.006)
    fTot.SetParameter(8,0.5*peak)
    fTot.SetParLimits(8,0.3*peak,0.9*peak)
#511 KeV photoelectric
    fTot.SetParameter(9,15.)
    fTot.SetParLimits(9,5,40.)
    fTot.SetParameter(10,peak)
    fTot.SetParLimits(10,0.9*peak,1.1*peak)
    fTot.SetParameter(11,0.05*peak)
    fTot.SetParLimits(11,0.02*peak,0.2*peak)
#511 KeV backscatter peak
    fTot.SetParameter(12,3.)
    fTot.SetParLimits(12,1.,15.)
    fTot.SetParameter(13,0.3*peak)
    fTot.SetParLimits(13,0.2*peak,0.4*peak)
    fTot.SetParameter(14,0.05*peak)
    fTot.SetParLimits(14,0.02*peak,0.15*peak)
#1274 KeV backscatter peak??
    fTot.SetParameter(15,2.)
    fTot.SetParLimits(15,0,10)
    fTot.SetParameter(16,2*0.3*peak)
    fTot.SetParLimits(16,2*0.2*peak,2*0.4*peak)
    fTot.SetParameter(17,0.05*peak)
    fTot.SetParLimits(17,0.02*peak,0.15*peak)
elif peak<10000:
    #compressed spectrum, compton and backscatter now within trigger turnon we may need a
    fTot=R.TF1("fTot","[0]*(1./(1+TMath::Exp([1]*(x-[2])))+[3]*TMath::Gaus(x,[4],[5])+(1+TMath::Erf((x-[12])/([13]*TMath::Sqrt(x))))*([6]/(1+TMath::Exp([7]*(x-[8])))+[14]*TMath::Gaus(x,[15],[16]))+[9]*TMath::Gaus(x,[10],[11]))",0,100000)
    fBkg=R.TF1("fBkg","[0]*(1./(1+TMath::Exp([1]*(x-[2])))+[3]*TMath::Gaus(x,[4],[5])+(1+TMath::Erf((x-[12])/([13]*TMath::Sqrt(x))))*([6]/(1+TMath::Exp([7]*(x-[8])))+[9]*TMath::Gaus(x,[10],[11])))",0,100000)
    fTot.SetNpx(100000)
    fBkg.SetNpx(100000)

#Normalisation
    fTot.SetParameter(0,norm)
    fTot.SetParLimits(0,norm*0.1,norm*3)
#1274 KeV compton 
    fTot.SetParameter(1,0.003)
    fTot.SetParLimits(1,0.0001,0.01)
    fTot.SetParameter(2,1.7*peak)
    fTot.SetParLimits(2,1.1*peak,2.5*peak)
#1274 KeV "photo-electric" 
    fTot.SetParameter(3,1.)
    fTot.SetParLimits(3,0.5,5.)
    fTot.SetParameter(4,2.5*peak)
    fTot.SetParLimits(4,2.*peak,3*peak)
    fTot.SetParameter(5,0.1*peak)
    fTot.SetParLimits(5,0.03*peak,0.2*peak)
#511 KeV compton
    fTot.SetParameter(6,10.)
    fTot.SetParLimits(6,2,50.)
    fTot.SetParameter(7,0.003)
    fTot.SetParLimits(7,0.0001,0.005)
    fTot.SetParameter(8,0.6*peak)
    fTot.SetParLimits(8,0.1*peak,0.9*peak)
#Trigger turn on (Compton+BS)
    fTot.SetParameter(12,3000)
    fTot.SetParLimits(12,1000,5000)
    fTot.SetParameter(13,10)
    fTot.SetParLimits(13,1,100)
#511 KeV photoelectric
    fTot.SetParameter(9,15.)
    fTot.SetParLimits(9,5,50.)
    fTot.SetParameter(10,peak)
    fTot.SetParLimits(10,0.9*peak,1.1*peak)
    fTot.SetParameter(11,0.05*peak)
    fTot.SetParLimits(11,0.02*peak,0.2*peak)
#Back scatter
    fTot.SetParameter(14,2.)
    fTot.SetParLimits(14,1,10.)
    fTot.SetParameter(15,0.6*peak)
    fTot.SetParLimits(15,0.5*peak,0.7*peak)
    fTot.SetParameter(16,0.07*peak)
    fTot.SetParLimits(16,0.05*peak,0.2*peak)
else:
    print("Intermediate conditions still to be studied")

R.gStyle.SetOptStat(0)
R.gStyle.SetOptFit(1111111)
R.gStyle.SetStatH(0.09)

charge.SetMarkerStyle(20)
charge.SetMarkerSize(1.0)
charge.SetMarkerColor(R.kBlack)
charge.SetLineColor(R.kBlack)

charge.Draw("PE")
#charge.SetMaximum(charge.GetMaximum()*2.)
if (peak>20000):
    charge.Fit("fTot","LR+","",5000,min(peak*3,100000))
    for ip in range(0,9):
        fBkg.SetParameter(ip,fTot.GetParameter(ip))
    for ip in range(0,6):
        fBkg.SetParameter(9+ip,fTot.GetParameter(12+ip))
else:
    charge.Fit("fTot","LR+","",2000,min(peak*3,100000))
    for ip in range(0,14):
        fBkg.SetParameter(ip,fTot.GetParameter(ip))
    for ip in range(0,3):
        fBkg.SetParameter(9+ip,fTot.GetParameter(14+ip))
        
charge.GetXaxis().SetRangeUser(0.2*peak,min(peak*3,100000))

fBkg.SetLineColor(R.kGreen)
fBkg.SetLineWidth(6)

fBkg.Draw("SAME")
charge.GetFunction("fTot").Draw("SAME")
charge.Draw("PESAME")

for ext in ['png','pdf','root']:
    c.SaveAs(args.output+"/chargeFit_"+ os.path.splitext(os.path.basename(args.input))[0] +"."+ext)