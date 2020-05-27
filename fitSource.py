import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array

R.gROOT.SetBatch(1)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input',dest='input')
parser.add_argument('--output',dest='output')
parser.add_argument('--led',dest='led')
parser.add_argument('--longRun',dest='longRun',action='store_true')
parser.add_argument('--fromHistos',dest='fromHistos',action='store_true')

parser.set_defaults(longRun=False,fromHistos=False)

args = parser.parse_args()

#Very preliminary calibration to be updated (eg passed as parameter?)
pe=16.7

c=R.TCanvas("c","c",900,700)
f=R.TFile(args.input)
f2=R.TFile(args.led)

histos = {}

if (not args.fromHistos):
    h4=f.Get("h4")
    histos['spill']=R.TH1F("spill","spill",200,-0.5,199.5)
    if (h4.GetEntries()<=0):
        print("Empty input tree!")
    h4.Project("spill","spill")
    h4.GetEntry(1)
    ts=h4.time_stamps[1]
    runTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
else:
    histos['spill']=f.Get("spill")

maxSpill=histos['spill'].GetNbinsX() if args.longRun else 1

x,x_err,ly,ly_err,lyres,lyres_err,tb,tb_err = array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' )

runID=os.path.splitext(os.path.basename(args.input))[0]

if 'h4Reco_' in runID:
    runID=runID.split('h4Reco_')[1]
if 'histos_' in runID:
    runID=runID.split('histos_')[1]

out=R.TFile(args.output+"/SourceAnalysis_"+ runID +".root","RECREATE")

for ibin in range(1,maxSpill+1):
    if (ibin<5):
        print(histos['spill'].GetBinContent(ibin))
    if (args.longRun and histos['spill'].GetBinContent(ibin+1) < 1000 ):
        continue
    print("Events in spill %d=%d"%(ibin,histos['spill'].GetBinContent(ibin+1)))
    key="_spill%d"%(ibin)
    if (not args.fromHistos):
        histos['charge'+key]=R.TH1F("charge"+key,"charge"+key,1000,1000,101000)
        if (not args.longRun):
            h4.Project("charge"+key,"charge_tot[C0]")
        else:
            h4.Project("charge"+key,"charge_tot[C0]","spill==%d"%(ibin))
    else:
        histos['charge'+key]=f.Get('charge'+key)
        histos['tBench'+key]=f.Get('tBench'+key)
        histos['tLab'+key]=f.Get('tLab'+key)
        
    histos['charge'+key].SetMinimum(0.1)
    #get some inputs from the spectrum to set the par limits
    histos['charge'+key].GetXaxis().SetRangeUser(histos['charge'+key].GetMean(),100000)
    peak=histos['charge'+key].GetBinCenter(histos['charge'+key].GetMaximumBin())
    norm=float(histos['charge'+key].GetEntries())/histos['charge'+key].GetNbinsX()
    histos['charge'+key].GetXaxis().SetRangeUser(1000,100000)
    if (peak>20000):
        fTot=R.TF1("fTot","[0]*(1./(1+TMath::Exp([1]*(x-[2])))+[3]*TMath::Gaus(x,[4],[5])+[6]/(1+TMath::Exp([7]*(x-[8])))+[9]*TMath::Gaus(x,[10],[11])+[12]*TMath::Gaus(x,[13],[14])+[15]*TMath::Gaus(x,[16],[17]))",0,100000)
        fBkg=R.TF1("fBkg","[0]*(1./(1+TMath::Exp([1]*(x-[2])))+[3]*TMath::Gaus(x,[4],[5])+[6]/(1+TMath::Exp([7]*(x-[8])))+[9]*TMath::Gaus(x,[10],[11])+[12]*TMath::Gaus(x,[13],[14]))",0,100000)
        fTot.SetNpx(100000)
        fBkg.SetNpx(100000)
        #Normalisation 
        fTot.SetParameter(0,norm*0.3)
        fTot.SetParLimits(0,norm*0.1,norm)
        #1274 KeV compton 
        fTot.SetParameter(1,0.0015)
        fTot.SetParLimits(1,0.0005,0.003)
        fTot.SetParameter(2,1.7*peak)
        fTot.SetParLimits(2,1.5*peak,1.9*peak)
        #1274 KeV "photo-electric", in the high range this is saturated 
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
        fTot.SetParLimits(10,0.85*peak,1.15*peak)
        fTot.SetParameter(11,0.05*peak)
        fTot.SetParLimits(11,0.02*peak,0.2*peak)
        #511 KeV backscatter peak
        fTot.SetParameter(12,3.)
        fTot.SetParLimits(12,1.,15.)
        fTot.SetParameter(13,0.3*peak)
        fTot.SetParLimits(13,0.2*peak,0.4*peak)
        fTot.SetParameter(14,0.05*peak)
        fTot.SetParLimits(14,0.02*peak,0.15*peak)
        #1274 KeV backscatter peak?? (should not bee too far from the 511 KeV compton edge...)
        fTot.SetParameter(15,2.)
        fTot.SetParLimits(15,0,10)
        fTot.SetParameter(16,2*0.3*peak)
        fTot.SetParLimits(16,2*0.2*peak,2*0.4*peak)
        fTot.SetParameter(17,0.05*peak)
        fTot.SetParLimits(17,0.02*peak,0.15*peak)
    elif peak<20000:
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
        fTot.SetParLimits(3,0.2,5.)
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
        fTot.SetParLimits(8,0.05*peak,1.3*peak)
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

    R.gStyle.SetOptTitle(0)
    R.gStyle.SetOptStat(0)
    R.gStyle.SetOptFit(1111111)
    R.gStyle.SetStatH(0.09)

    histos['charge'+key].SetMarkerStyle(20)
    histos['charge'+key].SetMarkerSize(1.0)
    histos['charge'+key].SetMarkerColor(R.kBlack)
    histos['charge'+key].SetLineColor(R.kBlack)

    histos['charge'+key].Draw("PE")
    #histos['charge'+key].SetMaximum(histos['charge'+key].GetMaximum()*2.)
    if (peak>20000):
        histos['charge'+key].Fit("fTot","LR+","",5000,min(peak*3,100000))
        for ip in range(0,9):
            fBkg.SetParameter(ip,fTot.GetParameter(ip))
        for ip in range(0,6):
            fBkg.SetParameter(9+ip,fTot.GetParameter(12+ip))
    else:
        histos['charge'+key].Fit("fTot","LR+","",2000,min(peak*3,100000))
        for ip in range(0,14):
            fBkg.SetParameter(ip,fTot.GetParameter(ip))
        for ip in range(0,3):
            fBkg.SetParameter(9+ip,fTot.GetParameter(14+ip))
        
    histos['charge'+key].GetXaxis().SetRangeUser(0.2*peak,min(peak*3,100000))
    histos['charge'+key].GetXaxis().SetTitle("Charge [ADC]")
    histos['charge'+key].GetYaxis().SetTitle("Entries/%d ADC"%histos['charge'+key].GetBinWidth(1))

    fBkg.SetLineColor(R.kGreen)
    fBkg.SetLineWidth(6)

    fBkg.Draw("SAME")
    histos['charge'+key].GetFunction("fTot").Draw("SAME")
    histos['charge'+key].Draw("PESAME")

    spillID=runID
    if (args.longRun):
        spillID=spillID+key

    pedaytxt = f2.Get("singlePE").GetMean()
    ledID=os.path.splitext(os.path.basename(args.led))[0]
    if (not args.longRun):
        txtstring = str(spillID) + "  " + str(ibin) + "  " + str(pe) + "  " + str(ledID) + "  " + str(pedaytxt) + "  " + str(fTot.GetParameter(10)) + "  " + str(fTot.GetParError(10)) + "  " + str(fTot.GetParameter(11)) + "  " + str(fTot.GetParError(11)) + "  " + str(fTot.GetParameter(4)) + "  " + str(fTot.GetParError(4)) + "  " + str(fTot.GetParameter(5)) + "  " + str(fTot.GetParError(5)) + "  "
        outTS = open(args.output+"/SourceAnalysis_Summary.txt","a")       
        outTS.write(txtstring)
        outTS.close()

    text=R.TLatex()
    text.SetTextSize(0.03)
    #text.DrawLatexNDC(0.485,0.4,"511 KeV Peak: %.4e #pm %.2e"%(fTot.GetParameter(10),fTot.GetParError(10)))
    text.DrawLatexNDC(0.485,0.365,"LY (Preliminary): %5.1f #pm %3.1f pe/MeV"%(fTot.GetParameter(10)/pe/0.511,R.TMath.Sqrt(R.TMath.Power(fTot.GetParameter(10)/pe/0.511*0.02,2)+R.TMath.Power(fTot.GetParError(10)/pe/0.511,2))))
    text.DrawLatexNDC(0.485,0.33,"511 KeV Resolution: %3.1f %%"%(fTot.GetParameter(11)/fTot.GetParameter(10)*100))

    text.SetTextSize(0.03)
    text.DrawLatexNDC(0.12,0.91,"Run ID: %s"%(spillID))
    if (not args.fromHistos):
        text.SetTextSize(0.02)
        text.DrawLatexNDC(0.13,0.87,"Run time: %s UTC"%(runTime))

    for ext in ['png','pdf']:
        c.SaveAs(args.output+"/chargeFit_"+ spillID +"."+ext)

    out.cd()

    histos['charge'+key].Write()
    if (args.fromHistos):
        histos['tBench'+key].Write()
        histos['tLab'+key].Write()

    if (args.longRun):
        x.append(ibin)
        x_err.append(0)
        ly.append(fTot.GetParameter(10))
        ly_err.append(fTot.GetParError(10))
        lyres.append(fTot.GetParameter(11)/fTot.GetParameter(10))
        lyres_err.append(fTot.GetParError(11)/fTot.GetParameter(10))
        if (args.fromHistos):
            tb.append(histos['tBench'+key].GetMean())
            tb_err.append(histos['tBench'+key].GetRMS())

    #linearity only if feasible
    if (peak<20000 and not args.longRun):
        fitADC = np.empty(3, np.dtype('float64'))
        fitADC[0]=fTot.GetParameter(10)
        fitADC[1]=fTot.GetParameter(2)
        fitADC[2]=fTot.GetParameter(4)
        fitADC_err = np.empty(3, np.dtype('float64'))
        fitADC_err[0]=fTot.GetParError(10)
        fitADC_err[1]=2000
        fitADC_err[2]=fTot.GetParError(4)
        energy = np.empty(3, np.dtype('float64'))
        energy[0] = 0.511
        energy[1] = 1.2745*(1-1./(1+(2*1.2745)/0.511))
        energy[2] = 1.2745
        energy_err = np.full(3, 0., np.dtype('float64')) #10mv Error?

        # calling the TGraph constructor
        frame=R.TH2F('frame','frame',10,0,1.5,10,-1000,40000)
        frame.Draw()
        lyFit=R.TF1("lyFit","[0]+[1]*x",0,1.5)
        linearity =R.TGraphErrors(len(fitADC[:]),energy[:],fitADC[:],energy_err[:],fitADC_err[:])
        linearity.Draw('PSAME')
        linearity.SetMarkerStyle(20)
        linearity.SetMarkerSize(1.2)
        linearity.Fit("lyFit","R+","",0,1.5)

        frame.GetXaxis().SetTitle("Energy [MeV]")
        frame.GetYaxis().SetTitle("Charge [ADC]")

        text.SetTextSize(0.04)
        text.DrawLatexNDC(0.2,0.7,"LY (Preliminary): %5.1f #pm %3.1f pe/MeV"%(lyFit.GetParameter(1)/pe,R.TMath.Sqrt(R.TMath.Power(lyFit.GetParameter(1)/pe*0.02,2)+R.TMath.Power(lyFit.GetParError(1)/pe,2))))
        text.SetTextSize(0.03)
        text.DrawLatexNDC(0.12,0.91,"Run ID: %s"%(spillID))
        if (not args.fromHistos):
            text.SetTextSize(0.02)
            text.DrawLatexNDC(0.13,0.87,"Run time: %s UTC"%(runTime))

        for ext in ['png','pdf']:
            c.SaveAs(args.output+"/linearity_"+ spillID +"."+ext)
        out.cd()
        linearity.Write("linearity_"+ spillID)

if (args.longRun):
    lyVsSpill=R.TGraphErrors(len(x),x,ly,x_err,ly_err)
    c.SetLogy(0)
    lyVsSpill.Draw("APE")
    R.gStyle.SetOptTitle(0)
    R.gStyle.SetOptFit(1111)
    lyVsSpill.SetMarkerStyle(20)
    lyVsSpill.SetMarkerSize(1.1)
    lyVsSpill.GetXaxis().SetTitle("#Spill")
    lyVsSpill.GetYaxis().SetTitle("LY response (ADC)")
    lyVsSpill.GetYaxis().SetRangeUser(ly[0]*0.85,ly[0]*1.15)
#    lyVsSpill.Fit( "pol0" )
    for ext in ['png','pdf']:
        c.SaveAs(args.output+"/lySpill_"+ runID +"."+ext)
    out.cd()
    lyVsSpill.Write("lyVsSpill_"+runID)

    if (args.fromHistos):
        lyVsTBench=R.TGraphErrors(len(tb),tb,ly,tb_err,ly_err)
        c.SetLogy(0)
        lyVsTBench.Draw("APE")
        R.gStyle.SetOptTitle(0)
        R.gStyle.SetOptFit(1111)
        lyVsTBench.SetMarkerStyle(20)
        lyVsTBench.SetMarkerSize(1.1)
        lyVsTBench.GetXaxis().SetTitle("Temperature")
        lyVsTBench.GetYaxis().SetTitle("LY response (ADC)")
        lyVsTBench.GetYaxis().SetRangeUser(ly[0]*0.85,ly[0]*1.15)
        #    lyVsTBench.Fit( "pol0" )
        for ext in ['png','pdf']:
            c.SaveAs(args.output+"/lyTBench_"+ runID +"."+ext)
        out.cd()
        lyVsTBench.Write("lyVsTBench_"+runID)

        tbVsSpill=R.TGraphErrors(len(x),x,tb,x_err,tb_err)
        c.SetLogy(0)
        tbVsSpill.Draw("APEL")
        R.gStyle.SetOptTitle(0)
        R.gStyle.SetOptFit(1111)
        tbVsSpill.SetMarkerStyle(20)
        tbVsSpill.SetMarkerSize(1.1)
        tbVsSpill.GetXaxis().SetTitle("#Spill")
        tbVsSpill.GetYaxis().SetTitle("Temperature")
        tbVsSpill.GetYaxis().SetRangeUser(15,30)
        #    tbVsSpill.Fit( "pol0" )
        for ext in ['png','pdf']:
            c.SaveAs(args.output+"/tbSpill_"+ runID +"."+ext)
        out.cd()
        tbVsSpill.Write("TBenchVsSpill_"+runID)

    R.gStyle.SetOptStat(1111)

    histos['ly']=R.TH1F('ly_'+runID,'ly_'+runID,60,ly[0]*0.85,ly[0]*1.15)
    for val in ly:
        histos['ly'].Fill(val)
    histos['ly'].Draw()
    for ext in ['png','pdf']:
        c.SaveAs(args.output+"/ly_"+ runID +"."+ext)
    histos['ly'].Write("ly_"+runID)

    if (args.fromHistos):
        histos['tb']=R.TH1F('tb_'+runID,'tb_'+runID,300,15,30)
        for val in tb:
            histos['tb'].Fill(val)
        histos['tb'].Draw()
        for ext in ['png','pdf']:
            c.SaveAs(args.output+"/tb_"+ runID +"."+ext)
        histos['tb'].Write("TBench_"+runID)

out.cd()
histos['peused']=R.TH1F('peused','peused',60,10,25)
histos['peused'].Fill(pe)
histos['peused'].Draw()
histos['peused'].Write("peused")

histos['peday']=f2.Get("singlePE")
histos['peday'].Write("peday")
