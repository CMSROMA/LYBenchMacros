import ROOT as R
R.gROOT.SetBatch(1)

from array import array
import math as mt
import numpy as np
import re
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--csv',dest='csv')
parser.add_argument('--output',dest='output')
parser.add_argument('--bench',dest='bench')
args = parser.parse_args()

crystalsData=R.TTree("crystalsData","crystalsData");
if (args.bench == 'pmt'):
    crystalsData.ReadFile(args.csv,"measId/C:prod/C:geo/C:ref/F:measTime/I:measTag/C:pe/F:dt/F:xtalType/C:myId/I:ly/F")
else:
    crystalsData.ReadFile(args.csv,"measId/C:prod/C:xtalType/C:myId/I:geo/C:measTag/C:temp/F:posx/F:posy/F:ly/F:ctr/F:lyRef/F:ctrRef/F")

crystalsData.Show(0)

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

    if (args.bench=='pmt' and (crys.ly < 0 or crys.ref < 0 or crys.dt < 0 or crys.pe < 0)):
        continue

    if (args.bench=='tofpet' and (crys.ly < 0 or crys.lyRef < 0 or crys.ctr < 0 or crys.ctrRef < 0)):
        continue
    
    if (args.bench=='pmt'):
        xtalsData[myId]={ 'LY_REL_IRR0': crys.ly/crys.ref, 'LY_ABS_IRR0': crys.ly/crys.pe, 'DT_IRR0':crys.dt }
    elif (args.bench=='tofpet'):
        xtalsData[myId]={ 'LY_ABS_IRR0': crys.ly, 'LY_REL_IRR0': crys.ly/crys.lyRef, 'CTR_ABS_IRR0': mt.sqrt(crys.ctr*crys.ctr - 90*90), 'CTR_REL_IRR0': mt.sqrt(crys.ctr*crys.ctr - 90*90) }

data={}
for prod in producers: 
    data[prod]={}

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    xtalType=crys.xtalType.rstrip('\x00')
    tag=crys.measTag.rstrip('\x00')
    myId=crys.myId

    thisTag = "%s_%s"%(tag.split('_')[0],tag.split('_')[1])
    timeTag=''
    if (len(tag.split('_'))>2):
        timeTag = "%s"%(tag.split('_')[2])
    if 'IRR0' in thisTag: 
        thisTag='IRR0'

    m=re.search('^T(\d+)([HDM]).*',timeTag) #match the time tag format
    #skip measurements which are too fresh <15H
    if (m):
        if (m.group(2) == 'M' ):
            continue
        if (m.group(2) == 'H' and int(m.group(1))<15):
            continue
    else:
        if ( not thisTag=='IRR0' ):
            continue

    if ( myId == 170): #special prod5 crysta...price x4! violet after irradiation!
        continue

    if (args.bench=='pmt' and (crys.ly < 0 or crys.ref < 0 or crys.dt < 0 or crys.pe < 0)):
        continue

    if (args.bench=='tofpet' and (crys.ly < 0 or crys.lyRef < 0 or crys.ctr < 0 or crys.ctrRef < 0)):
        continue

    myDose=dose[thisTag]
    newTag='%s%s_%s'%(xtalType.upper(),str(myId).zfill(5),thisTag.upper())

    if (args.bench == 'pmt'):
        lyNormRel=(crys.ly/crys.ref)/xtalsData[myId]['LY_REL_IRR0']
        lyRel=(crys.ly/crys.pe)/xtalsData[myId]['LY_ABS_IRR0']
        if (not newTag in data[prod].keys()):
            data[prod][newTag]=[]
        data[prod][newTag].append({'lyNormRel':lyNormRel,'lyRel':lyRel,'dt':crys.dt,'dose':myDose})
    elif (args.bench == 'tofpet'):
        lyRel=(crys.ly/crys.lyRef)/xtalsData[myId]['LY_REL_IRR0']
        ctrRel=mt.sqrt(crys.ctr*crys.ctr - 90*90)/xtalsData[myId]['CTR_REL_IRR0']
        ctrAbs=mt.sqrt(crys.ctr*crys.ctr - 90*90)
        lyAbs=crys.ly/crys.lyRef
        if (not newTag in data[prod].keys()):
            data[prod][newTag]=[]
        data[prod][newTag].append({'ctrAbs':ctrAbs,'lyRel':lyRel,'lyAbs':lyAbs, 'ctrRel':ctrRel,'dose':myDose })

resultsByTag={} #this will be used later as output in csv 

for iprod,prod in enumerate(producers): 
    byDose=defaultdict(list)
    resultsByDose=defaultdict(dict)
    for t in data[prod]:
        mm={}
        for dt in data[prod][t][0].keys():
            mm[dt]=np.empty(len(data[prod][t]))
        for i,meas in enumerate(data[prod][t]):
            for dt in meas.keys():
                mm[dt][i]=data[prod][t][i][dt]
        
        #fill dictionary to be used as output. Results are averaged for all measurements with same tag (XTAL+DOSE)
        resultsByTag[t]={}        
        resultsByTag[t]['prod']=prod
        resultsByTag[t]['type']='xtal'
        resultsByTag[t]['nmeas']=len(data[prod][t])
        for dt in data[prod][t][0].keys():
            resultsByTag[t][dt]=mm[dt].mean()
#            if resultsByTag[t]['nmeas']>1:
#                resultsByTag[t][dt+'_rms']=mm[dt].std()
#            else:
#                resultsByTag[t][dt+'_rms']=0.
        byDose[mm['dose'].mean()].append( { key:val.mean() for key,val in mm.items() } ) 

    #fill resultsByDose with averages at same dose (per producer)
    for key,val in byDose.items():
        for dt in val[0].keys():
            if dt=='dose':
                continue
            lsm=[ v[dt] for v in val ] 
            resultsByDose[key].update( { dt:{ 'mean': np.asarray(lsm).mean(), 'rms': np.asarray(lsm).std(), 'nmeas':len(lsm) } } ) 

    for g in resultsByDose[0].keys():
        if (not 'Abs' in g):
            histos[g+'VsDose_'+prod]=R.TGraphErrors(len(resultsByDose.keys())-1) #skip the dose=0 point
        else:
            histos[g+'VsDose_'+prod]=R.TGraphErrors(len(resultsByDose.keys())) #do not skip the dose=0 point for ctrAbs measurements
        histos[g+'VsDose_'+prod].SetName(g+'VsDose_'+prod)
        histos[g+'VsDose_'+prod].SetTitle(g+'VsDose_'+prod)


    index= { g:0  for g in resultsByDose[0].keys() }
    for dose,meas in sorted(resultsByDose.iteritems()):
        for g,m in meas.iteritems():
            if ('Rel' in g and dose<1): #only *Abs measures are meaningful at dose 0 (*Rel are relative to IRR0)
                continue

            avg=m['mean']

            if (m['nmeas']>2):
                rms=m['rms']
            else:
                #single value measurents uncertainty
                if (args.bench=='pmt'):
                    rms=0.05 #relative values are ~5%? TO BE FIXED
                elif (args.bench=='tofpet'):
                    rms=0.02 #relative values are ~2%? TO BE FIXED
                if (g=='ctrAbs'):
                    rms=5 #5ps uncertainty?

            if (dose==0):
                dose=0.1 #for logX plots
            histos[g+'VsDose_'+prod].SetPoint(index[g],dose*(1+0.02*iprod),avg)
            histos[g+'VsDose_'+prod].SetPointError(index[g],0,rms)
            index[g]=index[g]+1


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

if (args.bench=='pmt'):
    graphs=['lyNormRel','lyRel']
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
            c1.SaveAs(args.output+"/"+g+"VsDose"+ext)
    
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
            c1.SaveAs(args.output+"/"+g+"RescaledVsDose"+ext)
    
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
            c1.SaveAs(args.output+"/"+g+"ExpFitSlopeVsProducer"+ext)
    
    graphs=['dt']
    c1.SetLogx(1)
    for g in graphs:
        a=R.TH2F("a","a",10,0.1,100000,10,37,52.)
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
            c1.SaveAs(args.output+"/"+g+"VsDose"+ext)

elif (args.bench=='tofpet'):
    graphs=['lyRel', 'lyAbs', 'ctrRel', 'ctrAbs']
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
        a.GetXaxis().SetTitle("Dose [Gy]")
        a.GetYaxis().SetTitle("LO/LO_{befIrr}")
        a.SetStats(0)
        a.Draw()

        if (g=='ctrAbs'):
            aCtr=R.TH2F("aCtr","aCtr",10,0.1,100000,10,50,250)
            aCtr.GetXaxis().SetTitle("Dose [Gy]")
            aCtr.GetYaxis().SetTitle("CTR [ps]")
            aCtr.SetStats(0)
            aCtr.Draw()

        if (g=='lyAbs'):
            aLy=R.TH2F("aLY","aLY",10,0.1,100000,10,0.5,1.3)
            aLy.GetXaxis().SetTitle("Dose [Gy]")
            aLy.GetYaxis().SetTitle("LO/LO_{REF}")
            aLy.SetStats(0)
            aLy.Draw()
        
        leg.Clear()
        for i,prod in enumerate(producers): 
            histos[g+'VsDose_'+prod].SetMarkerSize(1.)
            histos[g+'VsDose_'+prod].SetMarkerStyle(20+i)
            histos[g+'VsDose_'+prod].SetMarkerColor(1+i)
            histos[g+'VsDose_'+prod].SetLineColor(1+i)
            histos[g+'VsDose_'+prod].SetLineStyle(1+int(i/4))
            if ('lyRel' in g):
                print g
                histos[g+'VsDose_'+prod].Fit("expo")
                histos[g+'VsDose_'+prod].GetFunction("expo").SetLineColor(1+i)
                histos[g+'VsDose_'+prod].GetFunction("expo").SetLineStyle(1+int(i/4))
                histos[g+'ExpFitIntercept'].Fill(histos[g+'VsDose_'+prod].GetFunction("expo").Eval(0))
                histos[g+'ExpFitSlope'].Fill(histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1))
                
                histos[g+'ExpFitSlopeVsIntercept'].SetPoint(i,histos[g+'VsDose_'+prod].GetFunction("expo").Eval(0),histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1))
                
                histos[g+'ExpFitSlopeVsProducer'].SetPoint(i,i+1,histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1))
                histos[g+'ExpFitSlopeVsProducer'].SetPointError(i,0,histos[g+'VsDose_'+prod].GetFunction("expo").GetParError(1))
                leg.AddEntry(histos[g+'VsDose_'+prod],"%s ExpSlope %.1E #pm %.1E"%(prod,histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1),histos[g+'VsDose_'+prod].GetFunction("expo").GetParError(1)),"PL")
                histos[g+'VsDose_'+prod].Draw("PSAME")
            else:
                histos[g+'VsDose_'+prod].Fit("pol0","0+")
                histos[g+'VsDose_'+prod].GetFunction("pol0").SetLineColor(1+i)
                histos[g+'VsDose_'+prod].GetFunction("pol0").SetLineStyle(1+int(i/4))
                histos[g+'VsDose_'+prod].SetLineColor(1+i)
                histos[g+'VsDose_'+prod].SetLineStyle(1+int(i/4))
                histos[g+'VsDose_'+prod].Draw("PLSAME")

        if ('lyRel' in g):
            leg.Draw()
        text.DrawLatexNDC(0.12,0.91,"CMS Rome - TOFPET Bench")
        for ext in ['.pdf','.png']:
            c1.SaveAs(args.output+"/"+g+"VsDose"+ext)
    
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
                if ('lyRel' in g):
                    histos[g+'RescaledVsDose_'+prod].SetPoint(ip,x,y/histos[g+'VsDose_'+prod].GetFunction("expo").Eval(0))
                else:
                    histos[g+'RescaledVsDose_'+prod].SetPoint(ip,x,y/histos[g+'VsDose_'+prod].GetFunction("pol0").Eval(0))
                histos[g+'RescaledVsDose_'+prod].SetPointError(ip,0,0.03)
    
            histos[g+'RescaledVsDose_'+prod].SetMarkerSize(1.)
            histos[g+'RescaledVsDose_'+prod].SetMarkerStyle(20+i)
            histos[g+'RescaledVsDose_'+prod].SetMarkerColor(1+i)
            histos[g+'RescaledVsDose_'+prod].SetLineColor(1+i)
            if ('lyRel' in g):
                histos[g+'RescaledVsDose_'+prod].Fit("expo")
                histos[g+'RescaledVsDose_'+prod].GetFunction("expo").SetLineColor(1+i)
                histos[g+'RescaledVsDose_'+prod].GetFunction("expo").SetLineStyle(1+int(i/4))
                leg.AddEntry(histos[g+'VsDose_'+prod],"%s ExpSlope %.1E #pm %.1E"%(prod,histos[g+'VsDose_'+prod].GetFunction("expo").GetParameter(1),histos[g+'VsDose_'+prod].GetFunction("expo").GetParError(1)),"PL")
            else:
                histos[g+'RescaledVsDose_'+prod].Fit("pol0")
                histos[g+'RescaledVsDose_'+prod].GetFunction("pol0").SetLineColor(1+i)
                histos[g+'RescaledVsDose_'+prod].GetFunction("pol0").SetLineStyle(1+int(i/4))

            histos[g+'RescaledVsDose_'+prod].Draw("PSAME")
    
        leg.Draw()
        text.DrawLatexNDC(0.12,0.91,"CMS Rome - TOFPET Bench")
        for ext in ['.pdf','.png']:
            c1.SaveAs(args.output+"/"+g+"RescaledVsDose"+ext)

        if ('lyRel' in g):
            c1.SetLogx(0)
            histos[g+'ExpFitSlopeVsProducer'].SetMarkerStyle(20)
            histos[g+'ExpFitSlopeVsProducer'].SetMarkerColor(R.kBlack)
            histos[g+'ExpFitSlopeVsProducer'].SetLineColor(R.kBlack)
            histos[g+'ExpFitSlopeVsProducer'].SetMarkerSize(1.2)
            histos[g+'ExpFitSlopeVsProducer'].Draw("AP")
            histos[g+'ExpFitSlopeVsProducer'].GetXaxis().SetTitle("Prod #")
            histos[g+'ExpFitSlopeVsProducer'].GetYaxis().SetTitle("LO Ratio Vs Dose ExpSlope [Gy^{-1}]")
            text.DrawLatexNDC(0.6,0.91,"CMS Rome - TOFPET Bench")
            for ext in ['.pdf','.png']:
                c1.SaveAs(args.output+"/"+g+"ExpFitSlopeVsProducer"+ext)
        
out=R.TFile(args.output+"/LYplots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()

#Save CSV using Pandas DataFrame
import pandas as pd
df=pd.DataFrame.from_dict(resultsByTag,orient='index')
#df=df.drop(columns=['runs','ledRuns','refRuns'])
df.to_csv(args.output+"/resultsByTag.csv",header=True)
