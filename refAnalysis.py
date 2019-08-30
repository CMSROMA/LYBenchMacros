import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array

def Map(tf):
    """                                                                                                                  
    Maps objets as dict[obj_name][0] using a TFile (tf) and TObject to browse.                                           
    """
    m = {}
    for k in tf.GetListOfKeys():
        n = k.GetName()
        m[n] = tf.Get(n)
    return m

R.gROOT.SetBatch(1)

refRuns = []
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190710-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190710-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190711-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190712-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190712-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190715-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190715-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190716-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190716-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190717-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190719-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190722-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190722-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190724-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190724-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190726-1.root")

sourceFits = {}
histos = {}
files = {}
histos['ly']=R.TH1F('ly','ly',400,0.,2000.)
histos['lyAll']=R.TH1F('lyAll','lyAll',400,0.,2000.)
histos['lyNorm']=R.TH1F('lyNorm','lyNorm',400,0.,2000.)
histos['lyVsGain']=R.TH2F('lyVsGain','lyVsGain',200,0,20.,400,0.,2000.)

goodFits=[]

for r in refRuns:
    files[r]=R.TFile.Open(r)
    objs=Map(files[r])
    sourceFits[r]=objs

    if not 'charge_spill0' in objs.keys():
        continue
    histos['lyAll'].Fill(sourceFits[r]['charge_spill0'].GetFunction('fTot').GetParameter(10)/16.)
    if not 'peused' in objs.keys():
        continue
    if not 'peday' in objs.keys():
        continue
    goodFits.append(r)

x,ly,lyres = array('d'),array('d'),array('d')
#goodfits=0

goodFits.sort()

histos['lyFrame']=R.TH2F("lyFrame","lyFrame",len(goodFits),0,len(goodFits),10,5000,15000)
histos['lyFrame'].SetStats(0)
histos['lyFrame'].GetYaxis().SetTitle("511 Kev Peak [ADC]")

for i,r in enumerate(goodFits):
    label=r.split('SourceAnalysis/SourceAnalysis_REF')[1].split('SL-')[1].replace('.root','')
    x.append(i+0.5)
    ly.append(sourceFits[r]['charge_spill0'].GetFunction('fTot').GetParameter(10))
    histos['ly'].Fill(sourceFits[r]['charge_spill0'].GetFunction('fTot').GetParameter(10)/16.)
    histos['lyNorm'].Fill(sourceFits[r]['charge_spill0'].GetFunction('fTot').GetParameter(10)/sourceFits[r]['peday'].GetMean())
    histos['lyVsGain'].Fill(sourceFits[r]['peday'].GetMean(),sourceFits[r]['charge_spill0'].GetFunction('fTot').GetParameter(10)/16.)
    histos['lyFrame'].GetXaxis().SetBinLabel(i+1,label)

histos['lyGraph']=R.TGraph(len(x),x,ly)
histos['lyGraph'].SetName("lyGraph")

c1=R.TCanvas("c1","c1",800,600)
R.gStyle.SetOptTitle(0)

text=R.TLatex()
text.SetTextSize(0.03)

for h in ['ly']:
    histos[h+'Frame'].Draw()
    histos[h+'Graph'].SetMarkerColor(R.kBlack)
    histos[h+'Graph'].SetMarkerStyle(20)
    histos[h+'Graph'].SetMarkerSize(1.2)
    histos[h+'Graph'].Draw("PSAME")
    text.DrawLatexNDC(0.12,0.91,"Ref crystal vs RunID")
    c1.SaveAs("refAnalysis/"+h+"Graph.pdf")

R.gStyle.SetOptStat(0)
R.gStyle.SetOptFit(111111)
histos['ly'].Draw()
histos['ly'].GetXaxis().SetTitle("LY [#pe]")
histos['ly'].Fit('gaus','LL')
text.DrawLatexNDC(0.12,0.91,"Ref crystal LY")
c1.SaveAs("refAnalysis/refLY.pdf")

out=R.TFile("refAnalysis/refAnalysis.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
out.Write()
out.Close()
