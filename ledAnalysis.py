import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array

R.gROOT.SetBatch(1)

ledRuns = []
ledRuns.append("SinglePEAnalysis/LED-20190705-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190705-SCAN-2_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190708-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190709-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190709-SCAN-2_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190709-SCAN-3_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190709-SCAN-4_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190710-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190710-SCAN-2_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190710-SCAN-3_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190711-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190712-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190712-SCAN-2_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190712-SCAN-3_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190715-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190715-SCAN-2_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190716-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190716-SCAN-2_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190717-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190719-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190722-SCAN-1_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190722-SCAN-2_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190722-SCAN-4_simul_out.root")
ledRuns.append("SinglePEAnalysis/LED-20190724-SCAN-1_simul_out.root")

def Map(tf):
    """                                                                                                                  
    Maps objets as dict[obj_name][0] using a TFile (tf) and TObject to browse.                                           
    """
    m = {}
    for k in tf.GetListOfKeys():
        n = k.GetName()
        m[n] = tf.Get(n)
    return m

singlePEfits = {}
for r in ledRuns:
    histos=Map(R.TFile(r))
    if 'PMT_0' in histos.keys():
        singlePEfits[r]=histos


x,mu,mu_err,gain,gain_err,ped,ped_err = array('d'),array('d'),array('d'),array('d'),array('d'),array('d'),array('d')

histos = {}
histos['mu']=R.TH1F('mu','mu',200,0.,2.)
histos['gain']=R.TH1F('gain','gain',200,10,30)
histos['ped']=R.TH1F('ped','ped',200,0,100)
histos['gainVsMu']=R.TH2F('gainVsMu','gainVsMu',200,0.,2.,200,10,30)
histos['gainVsPed']=R.TH2F('gainVsPed','gainVsPed',200,0.,100.,200,10,30)

goodFits=[]
for r in singlePEfits.keys():
#    if ( abs(singlePEfits[r]['PMT_0'].GetParameter(4)-35)<0.01 or abs(singlePEfits[r]['PMT_0'].GetParameter(1) - 0.1)<0.001):
    if ( abs(singlePEfits[r]['PMT_0'].GetParameter(4)-35)<0.01):
        print "Bad Run (Fit not converging): "+r
        continue

    if (singlePEfits[r]['PMT_4'].GetParameter(1) < 1.):
        print "Bad Run (LED amplitude): "+r
        continue

    goodFits.append(r)

histos['gainFrame']=R.TH2F("gainFrame","gainFrame",len(goodFits),0,len(goodFits),10,10,20)
histos['gainFrame'].SetStats(0)
histos['gainFrame'].GetYaxis().SetTitle("Single PE Charge [ADC]")

histos['pedFrame']=R.TH2F("pedFrame","pedFrame",len(goodFits),0,len(goodFits),10,0,100)
histos['pedFrame'].SetStats(0)
histos['pedFrame'].GetYaxis().SetTitle("Pedestal [ADC]")

histos['muFrame']=R.TH2F("muFrame","muFrame",len(goodFits),0,len(goodFits),10,0,2)
histos['muFrame'].SetStats(0)
histos['muFrame'].GetYaxis().SetTitle("Average number of pe @ 4.180V")

goodFits.sort()
for i,r in enumerate(goodFits):
    label=r.split('SinglePEAnalysis/LED-')[1].split('_simul_out.root')[0].replace('-SCAN','')
    x.append(i+0.5)
    mu.append(singlePEfits[r]['PMT_0'].GetParameter(1))
    mu_err.append(singlePEfits[r]['PMT_0'].GetParError(1))
    histos['mu'].Fill(singlePEfits[r]['PMT_0'].GetParameter(1))
    gain.append(singlePEfits[r]['PMT_0'].GetParameter(2))
    gain_err.append(singlePEfits[r]['PMT_0'].GetParError(2))
    histos['gain'].Fill(singlePEfits[r]['PMT_0'].GetParameter(2))
    ped.append(singlePEfits[r]['PMT_0'].GetParameter(4))
    ped_err.append(singlePEfits[r]['PMT_0'].GetParError(4))
    histos['ped'].Fill(singlePEfits[r]['PMT_0'].GetParameter(4))
    histos['gainVsMu'].Fill(singlePEfits[r]['PMT_0'].GetParameter(1),singlePEfits[r]['PMT_0'].GetParameter(2))
    histos['gainVsPed'].Fill(singlePEfits[r]['PMT_0'].GetParameter(4),singlePEfits[r]['PMT_0'].GetParameter(2))
    for h in ['gainFrame','pedFrame','muFrame']:
        histos[h].GetXaxis().SetBinLabel(i+1,label)

histos['gainGraph']=R.TGraph(len(x),x,gain)
histos['gainGraph'].SetName("gainGraph")
histos['muGraph']=R.TGraph(len(x),x,mu)
histos['muGraph'].SetName("muGraph")
histos['pedGraph']=R.TGraph(len(x),x,ped)
histos['pedGraph'].SetName("pedGraph")

c1=R.TCanvas("c1","c1",800,600)
R.gStyle.SetOptTitle(0)

text=R.TLatex()
text.SetTextSize(0.03)

for h in ['gain','ped','mu']:
    histos[h+'Frame'].Draw()
    histos[h+'Graph'].SetMarkerColor(R.kBlack)
    histos[h+'Graph'].SetMarkerStyle(20)
    histos[h+'Graph'].SetMarkerSize(1.2)
    histos[h+'Graph'].Draw("PSAME")
    text.DrawLatexNDC(0.12,0.91,h+" vs RunID")
    c1.SaveAs("ledAnalysis/"+h+"Graph.pdf")

out=R.TFile("ledAnalysis/ledAnalysis.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
out.Write()
out.Close()
