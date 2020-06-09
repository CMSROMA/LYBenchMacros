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
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190909-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190910-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190911-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190911-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190911-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190911-4.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190912-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190912-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190912-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190913-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190913-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190913-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190918-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190918-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190919-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190912-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190912-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20190912-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20191022-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20191105-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20191113-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20191115-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20191118-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200203-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200520-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200520-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200520-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200520-4.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200527-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200527-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200527-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-20200527-4.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191118-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191119-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191119-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191120-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191120-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191121-1.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191121-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191122-2.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191122-3.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191122-4.root")
refRuns.append("SourceAnalysis/SourceAnalysis_REF-WS3-NW-NC-P2-SL-H2-20191206-1.root")


sourceFits = {}
histos = {}
files = {}
histos['ly']=R.TH1F('ly','ly',400,0.,2000.)
histos['dt']=R.TH1F('dt','dt',200,30.,50.)
histos['lyAll']=R.TH1F('lyAll','lyAll',400,0.,2000.)
histos['lyNorm']=R.TH1F('lyNorm','lyNorm',400,0.,2000.)
#histos['lyVsGain']=R.TH2F('lyVsGain','lyVsGain',200,0,20.,400,0.,2000.)

goodFits=[]

for r in refRuns:
    files[r]=R.TFile.Open(r)
    objs=Map(files[r])
    sourceFits[r]=objs

    if ((not 'charge_spill0' in objs.keys()) and (not 'charge_spill1' in objs.keys())):
        continue

    cH='charge_spill0'
    if not cH in objs.keys():
        cH='charge_spill1'

    histos['lyAll'].Fill(sourceFits[r][cH].GetFunction('fTot').GetParameter(10)/16.)
    if not 'peused' in objs.keys():
        continue
    if not 'peday' in objs.keys():
        continue
    if sourceFits[r]['peday'].GetMean()>21:
        continue

    print(r)
    goodFits.append(r)

x,ly,lyres,pe,dt,unixtime = array('d'),array('d'),array('d'),array('d'),array('d'),array('d')
#goodfits=0

goodFits.sort()

histos['lyFrame']=R.TH2F("lyFrame","lyFrame",len(goodFits),0,len(goodFits),10,5000,15000)
histos['lyFrame'].SetStats(0)
histos['lyFrame'].GetYaxis().SetTitle("511 Kev Peak [ADC]")

histos['peFrame']=R.TH2F("peFrame","peFrame",len(goodFits),0,len(goodFits),10,10,30)
histos['peFrame'].SetStats(0)
histos['peFrame'].GetYaxis().SetTitle("Single PE [ADC]")

histos['lypeFrame']=R.TH2F("lypeFrame","lypeFrame",len(goodFits),0,len(goodFits),10,500,750)
histos['lypeFrame'].SetStats(0)
histos['lypeFrame'].GetYaxis().SetTitle("#pe")

for i,r in enumerate(goodFits):
    label=r.split('SourceAnalysis/SourceAnalysis_REF')[1].split('SL-')[1].replace('.root','')
    x.append(i+0.5)
    cH='charge_spill0'
    if not cH in sourceFits[r].keys():
        cH='charge_spill1'
    unixtime.append(files[r].GetCreationDate().Convert(R.kTRUE))
    ly.append(sourceFits[r][cH].GetFunction('fTot').GetParameter(10))
    dt.append(sourceFits[r]['filteredWaveform_spill0'].GetFunction("f2").GetParameter(1))
    pe.append(sourceFits[r]['peday'].GetMean())
    histos['ly'].Fill(sourceFits[r][cH].GetFunction('fTot').GetParameter(10)/16.)
    histos['dt'].Fill(dt[i])
    histos['lyNorm'].Fill(sourceFits[r][cH].GetFunction('fTot').GetParameter(10)/sourceFits[r]['peday'].GetMean())
#    histos['lyVsGain'].Fill(sourceFits[r]['peday'].GetMean(),sourceFits[r][cH].GetFunction('fTot').GetParameter(10)/16.)
    histos['lyFrame'].GetXaxis().SetBinLabel(i+1,label)
    histos['peFrame'].GetXaxis().SetBinLabel(i+1,label)
    histos['lypeFrame'].GetXaxis().SetBinLabel(i+1,label)

histos['lyGraph']=R.TGraph(len(x),unixtime,ly)
histos['lyGraph'].SetName("lyGraph")
histos['peGraph']=R.TGraph(len(x),unixtime,pe)
histos['peGraph'].SetName("peGraph")
histos['lypeGraph']=R.TGraph(len(x))
histos['lypeGraph'].SetName("lypeGraph")
histos['lyVsGain']=R.TGraphErrors(len(pe))
histos['lyVsGain'].SetName("lyVsGain")
for i in range(0,len(pe)):
    histos['lyVsGain'].SetPoint(i,pe[i],ly[i])
    histos['lyVsGain'].SetPointError(i,pe[i]*0.01,ly[i]*0.01)
    histos['lypeGraph'].SetPoint(i,unixtime[i],ly[i]/pe[i])

c1=R.TCanvas("c1","c1",800,600)
R.gStyle.SetOptTitle(0)

text=R.TLatex()
text.SetTextSize(0.04)

for h in ['ly','pe', 'lype']:
#    histos[h+'Frame'].Draw()
    histos[h+'Graph'].SetMarkerColor(R.kBlack)
    histos[h+'Graph'].SetMarkerStyle(20)
    histos[h+'Graph'].SetMarkerSize(1.2)
    histos[h+'Graph'].Draw("AP")
    text.DrawLatexNDC(0.12,0.91,"PMT Bench - Ref crystal vs RunID")
    c1.SaveAs("refAnalysis/"+h+"Graph.pdf")

R.gStyle.SetOptStat(0)
R.gStyle.SetOptFit(111111)
histos['lyNorm'].Rebin(4)
histos['lyNorm'].SetMarkerStyle(20)
histos['lyNorm'].SetMarkerSize(1.2)
histos['lyNorm'].Draw("PE")
histos['lyNorm'].GetXaxis().SetRangeUser(500,750)
histos['lyNorm'].GetXaxis().SetTitle("LY [#pe]")
histos['lyNorm'].Fit('gaus','LL')
text.SetTextSize(0.04)
text.DrawLatexNDC(0.12,0.91,"PMT Bench - Ref crystal LY")
c1.SaveAs("refAnalysis/refLY.pdf")

R.gStyle.SetOptFit(11111)

fS=R.TF1('fS','800*x-2000',0,30)
histos['lyVsGain'].SetMarkerStyle(20)
histos['lyVsGain'].SetMarkerSize(1.2)
histos['lyVsGain'].Draw("AP")
#histos['lyVsGain'].Fit(fS)
histos['lyVsGain'].GetXaxis().SetTitle("Single PE [ADC]")
histos['lyVsGain'].GetYaxis().SetTitle("511 KeV Peak [ADC]")
#fS.Draw("SAME")
c1.SaveAs("refAnalysis/LYvsGain.pdf")

out=R.TFile("refAnalysis/refAnalysis.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
out.Write()
out.Close()
