import ROOT as R
R.gROOT.SetBatch(1)

from array import array
import math as mt
import numpy as np

crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("LYIrradAnalysis/crystalsDB_Casaccia_Nov2019.csv","measId/C:prod/C:geo/C:ref/F:measTime/I:measTag/C:pe/F:dt/F:xtalType/C:myId/I:ly/F");

producers = [ 'prod'+str(i) for i in range(1,10) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

histos = {}
data = {}
xtalsData={}

dose={
    'IRR0':0,
    'IRR2_1H':2,
    'IRR20_1H':20,
    'IRR200_1H':210,
    'IRR20_14H':240,
    'IRR2K_1H':2200,
    'IRR200_14H':2400,
    'IRR9K_1H':9200,
    'IRR2K_14H':25000,
    'IRR9K_5H':34000,
}

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    xtalType=crys.xtalType.strip()
    tag=crys.measTag.strip()
    myId=crys.myId

    if not 'IRR0' in crys.measId:
        continue

    if ( crys.ly < 0 or crys.ref < 0 or crys.dt < 0):
        continue

    xtalsData[myId]={ 'LY_REL_IRR0': crys.ly/crys.ref, 'LY_ABS_IRR0': crys.ly/crys.pe, 'DT_IRR0':crys.dt }

data={}
for prod in producers: 
    data[prod]=[]

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    xtalType=crys.xtalType.strip()
    tag=crys.measTag.strip()
    myId=crys.myId

    thisTag = "%s_%s"%(tag.split('_')[0],tag.split('_')[1])
    if 'IRR0' in thisTag:
        thisTag='IRR0'

    if ( myId == 170):
        continue
    if ( crys.ly < 0 or crys.ref < 0 or crys.dt < 0):
        continue

    loRel=(crys.ly/crys.ref)/xtalsData[myId]['LY_REL_IRR0']
    loAbs=(crys.ly/crys.pe)/xtalsData[myId]['LY_ABS_IRR0']
    myDose=dose[thisTag]
    data[prod].append({'loAbs':loAbs,'loRel':loRel,'dt':crys.dt,'dose':myDose})
    
for iprod,prod in enumerate(producers): 
    print("#### %s ####"%prod)
    loRelDose={}
    loAbsDose={}
    dtDose={}
    for i,meas in enumerate(data[prod]):
        if (not meas['dose'] in loRelDose.keys()):
            loRelDose[meas['dose']]=array('d')
            loAbsDose[meas['dose']]=array('d')
            dtDose[meas['dose']]=array('d')
        loRelDose[meas['dose']].append(meas['loRel'])
        loAbsDose[meas['dose']].append(meas['loAbs'])
        dtDose[meas['dose']].append(meas['dt'])

    graphs=['lyRel','lyAbs','dt']
    for g in graphs:
        histos[g+'VsDose_'+prod]=R.TGraphErrors(len(loRelDose)-1) #skip the dose=0 point
        histos[g+'VsDose_'+prod].SetName(g+'VsDose_'+prod)
        histos[g+'VsDose_'+prod].SetTitle(g+'VsDose_'+prod)

    i=0
    for dose,meas in sorted(loRelDose.iteritems()):
        if (dose==0):
            continue
        m=np.asarray(meas)
        avg=m.mean()
        if (len(meas)>3):
            rms=m.std()
        else:
            rms=0.05
        print i,dose,avg,rms,len(meas)
        histos['lyRelVsDose_'+prod].SetPoint(i,dose*(1+0.02*iprod),avg)
        histos['lyRelVsDose_'+prod].SetPointError(i,0,rms)
        i=i+1

    i=0
    for dose,meas in sorted(loAbsDose.iteritems()):
        if (dose==0):
            continue
        m=np.asarray(meas)
        avg=m.mean()
        if (len(meas)>3):
            rms=m.std()
        else:
            rms=0.05
        print i,dose,avg,rms,len(meas)
        histos['lyAbsVsDose_'+prod].SetPoint(i,dose*(1+0.02*iprod),avg)
        histos['lyAbsVsDose_'+prod].SetPointError(i,0,rms)
        i=i+1

    i=0
    for dose,meas in sorted(dtDose.iteritems()):
        if (dose==0):
            continue
        m=np.asarray(meas)
        avg=m.mean()
        if (len(meas)>3):
            rms=m.std()
        else:
            rms=0.3
        print i,dose,avg,rms,len(meas)
        histos['dtVsDose_'+prod].SetPoint(i,dose*(1+0.02*iprod),avg)
        histos['dtVsDose_'+prod].SetPointError(i,0,rms)
        i=i+1


R.gStyle.SetOptTitle(0)
c1=R.TCanvas("c1","c1",900,600)
c1.SetLogx(1)

text=R.TLatex()
text.SetTextSize(0.04)

leg=R.TLegend(0.13,0.16,0.5,0.45)
leg.SetBorderSize(0)
leg.SetFillColorAlpha(0,0)
leg.SetTextSize(0.03)

leg1=R.TLegend(0.75,0.6,0.92,0.88)
leg1.SetBorderSize(0)
leg1.SetFillColorAlpha(0,0)
leg1.SetTextSize(0.03)

graphs=['lyRel','lyAbs']

for g in graphs:
    c1.SetLogx(1)
    histos[g+'ExpFitIntercept']=R.TH1F(g+'ExpFitIntercept',g+'ExpFitIntercept',100,0.8,1.2)
    histos[g+'ExpFitSlope']=R.TH1F(g+'ExpFitSlope',g+'ExpFitSlope',40,-2E-5,2E-5)

    histos[g+'ExpFitSlopeVsIntercept']=R.TGraph(len(producers))
    histos[g+'ExpFitSlopeVsIntercept'].SetName(g+'ExpFitSlopeVsIntercept')
    histos[g+'ExpFitSlopeVsIntercept'].SetTitle(g+'ExpFitSlopeVsIntercept')

    histos[g+'ExpFitSlopeVsProducer']=R.TGraphErrors(len(producers))
    histos[g+'ExpFitSlopeVsProducer'].SetName(g+'ExpFitSlopeVsProducer')
    histos[g+'ExpFitSlopeVsProducer'].SetTitle(g+'ExpFitSlopeVsProducer')

    a=R.TH2F("a","a",10,1,100000,10,0.5,1.3)
    a.Draw()
    a.GetXaxis().SetTitle("Dose [Gy]")
    a.GetYaxis().SetTitle("LO/LO_{befIrr}")
    a.SetStats(0)

    leg.Clear()
    for i,prod in enumerate(producers): 
        histos[g+'VsDose_'+prod].SetMarkerSize(1.)
        histos[g+'VsDose_'+prod].SetMarkerStyle(20+i)
        histos[g+'VsDose_'+prod].SetMarkerColor(1+i)
        histos[g+'VsDose_'+prod].SetLineColor(1+i)
        histos[g+'VsDose_'+prod].SetLineStyle(1+int(i/4))
        histos[g+'VsDose_'+prod].Fit("expo")
        histos[g+'VsDose_'+prod].GetFunction("expo").SetLineColor(1+i)
        histos[g+'VsDose_'+prod].GetFunction("expo").SetLineStyle(1+int(i/4))
        histos[g+'VsDose_'+prod].Draw("PSAME")

        histos[g+'ExpFitIntercept'].Fill(histos[g+'VsDose_'+prod].GetFunction("expo").Eval(0))
        histos[g+'ExpFitSlope'].Fill(histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1))

        histos[g+'ExpFitSlopeVsIntercept'].SetPoint(i,histos[g+'VsDose_'+prod].GetFunction("expo").Eval(0),histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1))

        histos[g+'ExpFitSlopeVsProducer'].SetPoint(i,i+1,histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1))
        histos[g+'ExpFitSlopeVsProducer'].SetPointError(i,0,histos[g+'VsDose_'+prod].GetFunction("expo").GetParError(1))
        leg.AddEntry(histos[g+'VsDose_'+prod],"%s ExpSlope %.1E #pm %.1E"%(prod,histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1),histos[g+'VsDose_'+prod].GetFunction("expo").GetParError(1)),"PL")

    leg.Draw()
    text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
    for ext in ['.pdf','.png']:
        c1.SaveAs("LYIrradAnalysis/"+g+"VsDose"+ext)

    a.Draw()
#    a.GetYaxis().SetRangeUser(0.5,1.2)
    #rescaling for the fit intercept
    leg.Clear()
    for i,prod in enumerate(producers): 
        histos[g+'RescaledVsDose_'+prod]=R.TGraphErrors(histos[g+'VsDose_'+prod].GetN()) 
        histos[g+'RescaledVsDose_'+prod].SetName(g+'RescaledVsDose_'+prod)
        histos[g+'RescaledVsDose_'+prod].SetTitle(g+'RescaledVsDose_'+prod)
        for ip in range(0,histos[g+'VsDose_'+prod].GetN()):
            x,y=R.Double(0.),R.Double(0.)
            histos[g+'VsDose_'+prod].GetPoint(ip,x,y)
            histos[g+'RescaledVsDose_'+prod].SetPoint(ip,x,y/histos[g+'VsDose_'+prod].GetFunction("expo").Eval(0))
            histos[g+'RescaledVsDose_'+prod].SetPointError(ip,0,0.05)

        histos[g+'RescaledVsDose_'+prod].SetMarkerSize(1.)
        histos[g+'RescaledVsDose_'+prod].SetMarkerStyle(20+i)
        histos[g+'RescaledVsDose_'+prod].SetMarkerColor(1+i)
        histos[g+'RescaledVsDose_'+prod].SetLineColor(1+i)
        histos[g+'RescaledVsDose_'+prod].Fit("expo")
        histos[g+'RescaledVsDose_'+prod].GetFunction("expo").SetLineColor(1+i)
        histos[g+'RescaledVsDose_'+prod].GetFunction("expo").SetLineStyle(1+int(i/4))
        histos[g+'RescaledVsDose_'+prod].Draw("PSAME")
        leg.AddEntry(histos[g+'VsDose_'+prod],"%s ExpSlope %.1E #pm %.1E"%(prod,histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1),histos[g+'VsDose_'+prod].GetFunction("expo").GetParError(1)),"PL")

    leg.Draw()
    text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
    for ext in ['.pdf','.png']:
        c1.SaveAs("LYIrradAnalysis/"+g+"RescaledVsDose"+ext)

    c1.SetLogx(0)
    histos[g+'ExpFitSlopeVsProducer'].SetMarkerStyle(20)
    histos[g+'ExpFitSlopeVsProducer'].SetMarkerColor(R.kBlack)
    histos[g+'ExpFitSlopeVsProducer'].SetLineColor(R.kBlack)
    histos[g+'ExpFitSlopeVsProducer'].SetMarkerSize(1.2)
    histos[g+'ExpFitSlopeVsProducer'].Draw("AP")
    histos[g+'ExpFitSlopeVsProducer'].GetXaxis().SetTitle("Prod #")
    histos[g+'ExpFitSlopeVsProducer'].GetYaxis().SetTitle("LO Ratio Vs Dose ExpSlope [Gy^{-1}]")
    text.DrawLatexNDC(0.6,0.91,"CMS Rome - PMT Bench")
    for ext in ['.pdf','.png']:
        c1.SaveAs("LYIrradAnalysis/"+g+"ExpFitSlopeVsProducer"+ext)

graphs=['dt']
c1.SetLogx(1)
for g in graphs:
    a=R.TH2F("a","a",10,1,100000,10,37,52.)
    a.Draw()
    a.GetXaxis().SetTitle("Dose [Gy]")
    a.GetYaxis().SetTitle("#tau [ns]")
    a.SetStats(0)

    leg1.Clear()
    for i,prod in enumerate(producers): 
        histos[g+'VsDose_'+prod].SetMarkerSize(1.)
        histos[g+'VsDose_'+prod].SetMarkerStyle(20+i)
        histos[g+'VsDose_'+prod].SetMarkerColor(1+i)
        histos[g+'VsDose_'+prod].SetLineColor(1+i)
        histos[g+'VsDose_'+prod].SetLineStyle(1+int(i/4))
        histos[g+'VsDose_'+prod].Draw("LPSAME")
        leg1.AddEntry(histos[g+'VsDose_'+prod],"%s"%(prod),"PL")

    leg1.Draw()
    text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
    for ext in ['.pdf','.png']:
        c1.SaveAs("LYIrradAnalysis/"+g+"VsDose"+ext)

out=R.TFile("LYIrradAnalysis/LYplots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()

    
