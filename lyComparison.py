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
parser.add_argument('--tag1',dest='tag1')
parser.add_argument('--tag2',dest='tag2')
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
xtalsData=defaultdict(dict)

tags = [ args.tag1, args.tag2 ]
for t in tags:
    for crys in crystalsData:
        prod=crys.prod.rstrip('\x00')
        geo=crys.geo.rstrip('\x00')
        xtalType=crys.xtalType.strip()
        tag=crys.measTag.strip()
        myId=crys.myId

        if not t in crys.measId:
            continue

        if (args.bench=='pmt' and (crys.ly < 0 or crys.ref < 0 or crys.dt < 0 or crys.pe < 0)):
            continue

        if (args.bench=='tofpet' and (crys.ly < 0 or crys.lyRef < 0 or crys.ctr < 0 or crys.ctrRef < 0)):
            continue
    
        if (args.bench=='pmt'):
            xtalsData[myId].update({ 'LY_ABS_%s'%t: crys.ly/crys.pe, 'LY_NORM_%s'%t: crys.ly/crys.ref, 'DT_%s'%t:crys.dt })
        elif (args.bench=='tofpet'):
            xtalsData[myId].update({ 'LY_ABS_%s'%t: crys.ly, 'LY_NORM_%s'%t: crys.ly/crys.lyRef, 'CTR_ABS_%s'%t: mt.sqrt(crys.ctr*crys.ctr - 90*90), 'CTR_NORM_%s'%t: mt.sqrt(crys.ctr*crys.ctr - 90*90)/mt.sqrt(crys.ctrRef*crys.ctrRef - 90*90) })


graphs={}
graphs['lyAbsCorr']=R.TGraphErrors()
graphs['lyNormCorr']=R.TGraphErrors()
graphs['dtCorr']=R.TGraphErrors()

graphs['lyAbsRatio']=R.TH1F('lyAbsRatio','lyAbsRatio',20,0.8,1.2)
graphs['lyNormRatio']=R.TH1F('lyNormRatio','lyNormRatio',20,0.8,1.2)
graphs['dtDiff']=R.TH1F('dtDiff','dtDiff',20,-1,1)

ip=0

for c,d in  xtalsData.items():
    if (len(d))<6:
        continue
    graphs['lyAbsCorr'].SetPoint(ip,d['LY_ABS_%s'%tags[0]],d['LY_ABS_%s'%tags[1]])
    graphs['lyAbsCorr'].SetPointError(ip,d['LY_ABS_%s'%tags[0]]*0.04,d['LY_ABS_%s'%tags[1]]*0.04)
    graphs['lyAbsRatio'].Fill(d['LY_ABS_%s'%tags[0]]/d['LY_ABS_%s'%tags[1]])
    graphs['lyNormCorr'].SetPoint(ip,d['LY_NORM_%s'%tags[0]],d['LY_NORM_%s'%tags[1]])
    graphs['lyNormCorr'].SetPointError(ip,0.04,0.04)
    graphs['lyNormRatio'].Fill(d['LY_NORM_%s'%tags[0]]/d['LY_NORM_%s'%tags[1]])
    graphs['dtCorr'].SetPoint(ip,d['DT_%s'%tags[0]],d['DT_%s'%tags[1]])
    graphs['dtCorr'].SetPointError(ip,0.3,0.3)
    graphs['dtDiff'].Fill(d['DT_%s'%tags[0]]-d['DT_%s'%tags[1]])
    ip+=1

c1=R.TCanvas('c1','c1',800,600)
R.gStyle.SetOptTitle(0)

f=R.TF1('f','x',-1000,1000)
for g in [ 'lyAbs', 'lyNorm', 'dt' ]:
    graphs['%sCorr'%g].SetMarkerStyle(24)
    graphs['%sCorr'%g].SetMarkerColor(R.kBlack)
    graphs['%sCorr'%g].SetMarkerSize(1.2)
    graphs['%sCorr'%g].Draw('AP')
    graphs['%sCorr'%g].GetXaxis().SetTitle('%s_%s'%(g,tags[0]))
    graphs['%sCorr'%g].GetYaxis().SetTitle('%s_%s'%(g,tags[1]))
    f.Draw('SAME')

    for ext in ['png','pdf','root']:
        c1.SaveAs('LYComparisonPlots/%sCorr_%s_%s.%s'%(g,tags[0],tags[1],ext))

R.gStyle.SetOptStat(0)
R.gStyle.SetOptFit(11111)

for g in [ 'lyAbs', 'lyNorm', ]:
    graphs['%sRatio'%g].SetMarkerStyle(20)
    graphs['%sRatio'%g].SetMarkerColor(R.kBlack)
    graphs['%sRatio'%g].SetMarkerSize(1.2)
    graphs['%sRatio'%g].Draw('PE')
    graphs['%sRatio'%g].Fit('gaus','L')
    graphs['%sRatio'%g].GetXaxis().SetTitle('%s %s/%s'%(g,tags[0],tags[1]))

    for ext in ['png','pdf','root']:
        c1.SaveAs('LYComparisonPlots/%sRatio_%s_%s.%s'%(g,tags[0],tags[1],ext))

for g in [ 'dt' ]:
    graphs['%sDiff'%g].SetMarkerStyle(20)
    graphs['%sDiff'%g].SetMarkerColor(R.kBlack)
    graphs['%sDiff'%g].SetMarkerSize(1.2)
    graphs['%sDiff'%g].Draw('PE')
    graphs['%sDiff'%g].Fit('gaus','L')
    graphs['%sDiff'%g].GetXaxis().SetTitle('%s %s - %s'%(g,tags[0],tags[1]))

    for ext in ['png','pdf','root']:
        c1.SaveAs('LYComparisonPlots/%sDiff_%s_%s.%s'%(g,tags[0],tags[1],ext))

out=R.TFile(args.output,"RECREATE")
for h,histo in graphs.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()
