import pandas as pd
import ROOT as R
R.gROOT.SetBatch(1)

lyBenchData = pd.read_csv("LYAnalysis/crystalsData.csv",header=None,index_col=0) 
tofpetData = pd.read_csv("LYAnalysis/lyAnalysisTOFPET.csv",header=None,index_col=0,usecols=[0,3,4,5,6,7,8]) 
result = pd.concat([lyBenchData,tofpetData], axis=1, join='inner')
result.to_csv("LYAnalysis/lyAnalysisMerged.csv",header=False)

crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("LYAnalysis/lyAnalysisMerged.csv","id/C:prod/C:geo/C:pe/F:dt/F:ref/F:ly/F:lyTof/F:lyTofCoinc/F:ctrTof/F:lyRefTof/F:lyRefTofCoinc/F:ctrRefTof/F");

producers = [ 'prod'+str(i) for i in range(1,9) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

histos = {}
data = {}
histos['lyRatio']=R.TH1F('lyRatio','lyRatio',100,0.5,1.5)
for prod in producers: 
    histos['lyRatio_'+prod]=R.TH1F('lyRatio_'+prod,'lyRatio_'+prod,100,0.5,1.5)
    histos['lyPMT_'+prod]=R.TH1F('lyPMT_'+prod,'lyPMT_'+prod,400,0.,2000.)
    histos['lyPMTAbs_'+prod]=R.TH1F('lyPMTAbs_'+prod,'lyPMTAbs_'+prod,400,0.,2000.)
    histos['lyPMTAbsOverDt_'+prod]=R.TH1F('lyPMTAbsOverDt_'+prod,'lyPMTAbsOverDt_'+prod,400,0.,40.)
    histos['lyPMTNorm_'+prod]=R.TH1F('lyPMTNorm_'+prod,'lyPMTNorm_'+prod,400,0.5,1.5)
    histos['lyTOFPET_'+prod]=R.TH1F('lyTOFPET_'+prod,'lyTOFPET_'+prod,200,0.,100.)
    histos['lyTOFPETNorm_'+prod]=R.TH1F('lyTOFPETNorm_'+prod,'lyTOFPETNorm_'+prod,400,0.5,1.5)
    histos['dt_'+prod]=R.TH1F('dt_'+prod,'dt_'+prod,100,20.,50.)
    histos['lyAbsTofOverDt_'+prod]=R.TH1F('lyAbsTofOverDt_'+prod,'lyAbsTofOverDt_'+prod,200,5.,25.)
    histos['ctr_'+prod]=R.TH1F('ctr_'+prod,'ctr_'+prod,200,50.,250.)
    for geo in geoms:
        histos['lyRatio_'+prod+'_'+geo]=R.TH1F('lyRatio_'+prod+'_'+geo,'lyRatio_'+prod+'_'+geo,100,0.5,1.5)
        histos['lyPMT_'+prod+'_'+geo]=R.TH1F('lyPMT_'+prod+'_'+geo,'lyPMT_'+prod+'_'+geo,400,0.,2000.)
        histos['lyPMTAbs_'+prod+'_'+geo]=R.TH1F('lyPMTAbs_'+prod+'_'+geo,'lyPMTAbs_'+prod+'_'+geo,400,0.,2000.)
        histos['lyPMTAbsOverDt_'+prod+'_'+geo]=R.TH1F('lyPMTAbsOverDt_'+prod+'_'+geo,'lyPMTAbsOverDt_'+prod+'_'+geo,400,0.,40.)
        histos['lyPMTNorm_'+prod+'_'+geo]=R.TH1F('lyPMTNorm_'+prod+'_'+geo,'lyPMTNorm_'+prod+'_'+geo,400,0.5,1.5)
        histos['lyTOFPET_'+prod+'_'+geo]=R.TH1F('lyTOFPET_'+prod+'_'+geo,'lyTOFPET_'+prod+'_'+geo,200,0.,100.)
        histos['lyTOFPETNorm_'+prod+'_'+geo]=R.TH1F('lyTOFPETNorm_'+prod+'_'+geo,'lyTOFPETNorm_'+prod+'_'+geo,400,0.5,1.5)
        histos['dt_'+prod+'_'+geo]=R.TH1F('dt_'+prod+'_'+geo,'dt_'+prod+'_'+geo,100,20.,50.)
        histos['lyAbsTofOverDt_'+prod+'_'+geo]=R.TH1F('lyAbsTofOverDt_'+prod+'_'+geo,'lyAbsTofOverDt_'+prod+'_'+geo,200,5.,25.)
        histos['ctr_'+prod+'_'+geo]=R.TH1F('ctr_'+prod+'_'+geo,'ctr_'+prod+'_'+geo,200,50.,250.)
        data[prod+'_'+geo] = []


for prod in producers: 
    for geo in geoms:
        data[prod+'_'+geo] = []

#1.06 needed to get average ratio between producers@ 1 
ratiosTof = { 'geo1': 0.9/1.06, 'geo2':1/1.06, 'geo3':1.03/1.06 }

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    if ( crys.ly < 0 or crys.ref < 0 or crys.dt < 0 or crys.lyTofCoinc<0 or crys.ctrTof<0 or crys.lyRefTofCoinc<0 or crys.ctrRefTof<0 ):
        continue
    if ( crys.lyTofCoinc == crys.lyRefTofCoinc ):
        print "******* "+crys.id
        continue

    data[prod+'_'+geo].append({ 'ly':crys.ly, 'lyGeoRatio':crys.ly*ratiosTof[geo], 'lyTof':crys.lyTofCoinc/ratiosTof[geo], 'lyNorm': crys.ly/crys.ref, 'lyNormGeoRatio': crys.ly*ratiosTof[geo]/crys.ref, 'dt': crys.dt, 'lyTofNorm': crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo], 'ctr': R.TMath.Sqrt(crys.ctrTof*crys.ctrTof-90*90), 'lyTofNoGeoRatio':crys.lyTofCoinc, 'lyTofNormNoGeoRatio': crys.lyTofCoinc/crys.lyRefTofCoinc })
    histos['lyRatio'].Fill((crys.ly/crys.ref)/(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo]))
    histos['lyRatio_'+prod+'_'+geo].Fill((crys.ly/crys.ref)/(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo]))
    histos['lyRatio_'+prod].Fill((crys.ly/crys.ref)/(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo]))
    histos['lyPMT_'+prod].Fill(crys.ly/16.)
    histos['lyPMT_'+prod+'_'+geo].Fill(crys.ly/16.)
    histos['lyPMTAbs_'+prod].Fill(crys.ly/crys.ref*10000./16.)
    histos['lyPMTAbs_'+prod+'_'+geo].Fill(crys.ly/crys.ref*10000./16.)
    histos['lyPMTAbsOverDt_'+prod].Fill(crys.ly/crys.ref*10000./16./crys.dt)
    histos['lyPMTAbsOverDt_'+prod+'_'+geo].Fill(crys.ly/crys.ref*10000./16./crys.dt)
    histos['lyPMTNorm_'+prod].Fill(crys.ly/crys.ref)
    histos['lyPMTNorm_'+prod+'_'+geo].Fill(crys.ly/crys.ref)
    histos['lyTOFPET_'+prod].Fill(crys.lyTofCoinc)
    histos['lyTOFPET_'+prod+'_'+geo].Fill(crys.lyTofCoinc)
    histos['lyTOFPETNorm_'+prod].Fill(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo])
    histos['lyTOFPETNorm_'+prod+'_'+geo].Fill(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo])
    histos['lyAbsTofOverDt_'+prod].Fill(data[prod+'_'+geo][-1]['lyTofNormNoGeoRatio']*(10000./16)/crys.dt)
    histos['lyAbsTofOverDt_'+prod+'_'+geo].Fill(data[prod+'_'+geo][-1]['lyTofNormNoGeoRatio']*(10000./16)/crys.dt)
    histos['ctr_'+prod].Fill(data[prod+'_'+geo][-1]['ctr'])
    histos['ctr_'+prod+'_'+geo].Fill(data[prod+'_'+geo][-1]['ctr'])

for prod in producers: 
    histos['ctrVslyAbsTofOverDt_'+prod]=R.TGraph(sum([len(data[prod+'_'+x]) for x in geoms ]))
    histos['ctrVslyAbsTofOverDt_'+prod].SetName('ctrVslyAbsTofOverDt_'+prod)
    ncry=0
    for geo in geoms:
        print data[prod+'_'+geo]
        histos['lyNormCorr_'+prod+'_'+geo]=R.TGraphErrors(len(data[prod+'_'+geo]))
        histos['lyNormCorr_'+prod+'_'+geo].SetName('lyNormCorr_'+prod+'_'+geo)
        histos['lyCorr_'+prod+'_'+geo]=R.TGraphErrors(len(data[prod+'_'+geo]))
        histos['lyCorr_'+prod+'_'+geo].SetName('lyCorr_'+prod+'_'+geo)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo]=R.TGraphErrors(len(data[prod+'_'+geo]))
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetName('ctrVslyAbsOverDt__'+prod+'_'+geo)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo]=R.TGraphErrors(len(data[prod+'_'+geo]))
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetName('ctrVslyAbsTofOverDt_'+prod+'_'+geo)
        histos['ctrVslyTofNorm_'+prod+'_'+geo]=R.TGraphErrors(len(data[prod+'_'+geo]))
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetName('ctrVslyTofNorm_'+prod+'_'+geo)
        for i,barData in enumerate(data[prod+'_'+geo]):
            print ncry
            histos['lyNormCorr_'+prod+'_'+geo].SetPoint(i,barData['lyNorm'],barData['lyTofNorm'])
            histos['lyNormCorr_'+prod+'_'+geo].SetPointError(i,0.05,0.05)
            histos['lyCorr_'+prod+'_'+geo].SetPoint(i,barData['ly'],barData['lyTof'])
            histos['lyCorr_'+prod+'_'+geo].SetPointError(i,barData['ly']*0.05,barData['lyTof']*0.05)
            histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetPoint(i,1/(barData['lyNormGeoRatio']*10000./16./barData['dt']/12.5),barData['ctr']/120.,)
            histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetPointError(i,0.05/(barData['lyNormGeoRatio']*10000./16./barData['dt']/12.5),barData['ctr']*0.05/120.,)
#            print (barData['lyTofNormNoGeoRatio']/barData['dt'])
            histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetPoint(i,1/(barData['lyTofNormNoGeoRatio']/barData['dt']/0.02),barData['ctr']/120.)
#            histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetPoint(i,1/(barData['lyTofNormNoGeoRatio']*10000./16./barData['dt']/12.5),barData['ctr']/120.)
            histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetPointError(i,0.05/(barData['lyTofNormNoGeoRatio']/barData['dt']/0.02),barData['ctr']*0.05/120.)
#            histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetPointError(i,0.05/(barData['lyTofNormNoGeoRatio']*10000./16./barData['dt']/12.5),barData['ctr']*0.05/120.)
            histos['ctrVslyTofNorm_'+prod+'_'+geo].SetPoint(i,1/(barData['lyTofNormNoGeoRatio']*1.06),barData['ctr']/120.)
            histos['ctrVslyTofNorm_'+prod+'_'+geo].SetPointError(i,0.05/(barData['lyTofNormNoGeoRatio']*1.06),barData['ctr']*0.05/120.)
            ncry+=1

c1=R.TCanvas("c1","c1",800,600)
R.gStyle.SetOptTitle(0)

text=R.TLatex()
text.SetTextSize(0.04)

leg=R.TLegend(0.4,0.6,0.92,0.88)
leg.SetBorderSize(0)
leg.SetFillColorAlpha(0,0)
leg.SetTextSize(0.03)
frame=R.TH2F("frame","frame",20,0.7,1.5,20,0.7,1.5)
frame.SetStats(0)
frame.GetXaxis().SetTitle("LO Normalised to REF bar (PMT)")
frame.GetYaxis().SetTitle("LO Normalised to REF bar (TOFPET+GeoCorr)")

frame.Draw()
leg.Clear()

f=R.TF1("f","x",0.8,1.2)
f.SetLineColor(R.kRed+3)
f.SetLineWidth(4)
for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['lyNormCorr_'+prod+'_'+geo].SetLineColor(R.kBlack+iprod)
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['lyNormCorr_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['lyNormCorr_'+prod+'_'+geo],"%s - <PMT>:%3.2f, <TOFPET>: %3.2f"%(prod,histos['lyPMTNorm_'+prod].GetMean(),histos['lyTOFPETNorm_'+prod].GetMean()),"P")
f.Draw("SAME")        
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/lyNormCorr_ProdDifferentColors"+ext)


for igeo,geo in enumerate(geoms):
    frame.Draw()
    leg.Clear()
    for iprod,prod in enumerate(producers): 
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['lyNormCorr_'+prod+'_'+geo].SetLineColor(R.kBlack+iprod)
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['lyNormCorr_'+prod+'_'+geo].Draw("PSAME")
        leg.AddEntry(histos['lyNormCorr_'+prod+'_'+geo],"%s - <PMT>:%3.2f, <TOFPET>: %3.2f"%(prod,histos['lyNormCorr_'+prod+'_'+geo].GetMean(1),histos['lyNormCorr_'+prod+'_'+geo].GetMean(2)),"P")
    f.Draw("SAME")        
    leg.Draw()
    text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench -"+geo)
    for ext in ['.pdf','.png']:
        c1.SaveAs("LYAnalysis/lyNormCorr_ProdDifferentColors_"+geo+ext)

frame.Draw()
leg.Clear()

graphs=[]
for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        g=R.TGraphErrors(1)
        g.SetPoint(0,histos['lyPMTNorm_'+prod+'_'+geo].GetMean(),histos['lyTOFPETNorm_'+prod+'_'+geo].GetMean())
        g.SetPointError(0,histos['lyPMTNorm_'+prod+'_'+geo].GetRMS(),histos['lyTOFPETNorm_'+prod+'_'+geo].GetRMS())
        g.SetMarkerStyle(20+igeo)
        g.SetMarkerSize(1.2)
        g.SetMarkerColor(R.kBlack+iprod)
        g.SetLineColor(R.kBlack+iprod)
        graphs.append(g)
        if (igeo==0):
            leg.AddEntry(graphs[-1],"%s - <PMT>:%3.2f, <TOFPET>: %3.2f"%(prod,histos['lyPMTNorm_'+prod].GetMean(),histos['lyTOFPETNorm_'+prod].GetMean()),"P")

for g in graphs:
    g.Draw("PSAME")
f.Draw("SAME")        
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/lyNormMeanCorr_ProdDifferentColors"+ext)

frame2=R.TH2F("frame2","frame2",20,0.5,1.7,20,0.5,1.7)
frame2.SetStats(0)
frame2.GetXaxis().SetTitle("Relative Decay Time/LO PMT")
frame2.GetYaxis().SetTitle("#sigma_{t} @ 511 KeV/120 ps")

f=R.TF1("f","x",0.8,1.3)
f.SetLineColor(R.kBlack)
f.SetLineWidth(4)

frame2.Draw()
leg.Clear()

for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetLineColor(R.kBlack+iprod)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['ctrVslyAbsOverDt_'+prod+'_'+geo],"%s - <LO/#tau>:%3.2f, <CTR>: %3.2f"%(prod,histos['ctrVslyAbsOverDt_'+prod+'_'+geo].GetMean(1),histos['ctrVslyAbsOverDt_'+prod+'_'+geo].GetMean(2)),"P")

#leg.Draw()
f.Draw("SAME")        
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/ctrVslyAbsOverDt_ProdDifferentColors"+ext)

frame3=R.TH2F("frame3","frame3",20,0.5,1.7,20,0.5,1.7)
frame3.SetStats(0)
frame3.GetXaxis().SetTitle("Relative Decay Time/LO TOFPET (NoGeoCorr)")
frame3.GetYaxis().SetTitle("#sigma_{t} @ 511 KeV/120 ps")

f1=R.TF1("f1","2*x-1",0.8,1.2)
f1.SetLineColor(R.kRed+3)
f1.SetLineWidth(4)



frame3.Draw()
leg.Clear()
leg.SetTextSize(0.025)
#f1.Draw("SAME")

histos['ctrVslyAbsTofOverDtSlope']=R.TH1F("ctrVslyAbsTofOverDtSlope","ctrVslyAbsTofOverDtSlope",100,0.,2.)
for iprod,prod in enumerate(producers): 
#    histos['ctrVslyAbsTofOverDt_'+prod].SetMarkerStyle(24)
#    histos['ctrVslyAbsTofOverDt_'+prod].SetMarkerColor(R.kBlack+iprod)
#    histos['ctrVslyAbsTofOverDt_'+prod].SetLineColor(R.kBlack+iprod)
#    histos['ctrVslyAbsTofOverDt_'+prod].SetMarkerSize(0)
#    histos['ctrVslyAbsTofOverDt_'+prod].Fit("pol1","","0+")
#    histos['ctrVslyAbsTofOverDt_'+prod].GetFunction("pol1").SetLineColor(R.kBlack+iprod)
#    histos['ctrVslyAbsTofOverDt_'+prod].GetFunction("pol1").SetLineWidth(1)
#    histos['ctrVslyAbsTofOverDt_'+prod].GetFunction("pol1").SetLineStyle(2)
#    histos['ctrVslyAbsTofOverDt_'+prod].Draw("PSAME")
#    histos['ctrVslyAbsTofOverDtSlope'].Fill(histos['ctrVslyAbsTofOverDt_'+prod].GetFunction("pol1").GetParameter(1))
    for igeo,geo in enumerate(geoms):
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetLineColor(R.kBlack+iprod)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
#            leg.AddEntry(histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo],"%s - <LO/#tau>:%3.2f <CTR>: %3.2f <Slope> %2.1f"%(prod,histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(1),histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(2),histos['ctrVslyAbsTofOverDt_'+prod].GetFunction("pol1").GetParameter(1)),"P")
            leg.AddEntry(histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo],"%s - <LO/#tau>:%3.2f <CTR>: %3.2f"%(prod,histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(1),histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(2)),"P")


#leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
#text.DrawLatexNDC(0.63,0.28,"<Slope>: %2.1f #pm %2.1f"%(histos['ctrVslyAbsTofOverDtSlope'].GetMean(),histos['ctrVslyAbsTofOverDtSlope'].GetRMS()))
f.Draw("SAME")        
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/ctrVslyAbsTofOverDt_ProdDifferentColors"+ext)

    
#f1.Draw("SAME")
for igeo,geo in enumerate(geoms):
    frame3.Draw()
    leg.Clear()
    leg.SetTextSize(0.025)
    for iprod,prod in enumerate(producers): 
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetLineColor(R.kBlack+iprod)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].Draw("PSAME")
        leg.AddEntry(histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo],"%s - <LO/#tau>:%3.2f <CTR>: %3.2f"%(prod,histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(1),histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(2)),"P")

    #leg.Draw()
    text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench - "+geo)
    f.Draw("SAME")        
    for ext in ['.pdf','.png']:
        c1.SaveAs("LYAnalysis/ctrVslyAbsTofOverDt_ProdDifferentColors_"+geo+ext)

frame3.Draw()
leg.SetTextSize(0.03)
leg.Clear()
#f1.Draw("SAME")
graphs3=[]
for iprod,prod in enumerate(producers): 
#    histos['ctrVslyAbsTofOverDt_'+prod].GetFunction("pol1").Draw("SAME")
    for igeo,geo in enumerate(geoms):
        g=R.TGraphErrors(1)
        if (histos['lyAbsTofOverDt_'+prod+'_'+geo].GetEntries()==0):
            continue
        g.SetPoint(0,13/histos['lyAbsTofOverDt_'+prod+'_'+geo].GetMean(),histos['ctr_'+prod+'_'+geo].GetMean()/120.)
        g.SetPointError(0,13/(histos['lyAbsTofOverDt_'+prod+'_'+geo].GetMean()*histos['lyAbsTofOverDt_'+prod+'_'+geo].GetMean())*histos['lyAbsTofOverDt_'+prod+'_'+geo].GetRMS(),histos['ctr_'+prod+'_'+geo].GetRMS()/120.)
        g.SetMarkerStyle(20+igeo)
        g.SetMarkerSize(1.2)
        g.SetMarkerColor(R.kBlack+iprod)
        g.SetLineColor(R.kBlack+iprod)
        graphs3.append(g)
        if (igeo==0):
            leg.AddEntry(graphs3[-1],"%s - <#tau/LO>:%3.2f, <#sigma_{t}>: %3.2f"%(prod,13/histos['lyAbsTofOverDt_'+prod].GetMean(),histos['ctr_'+prod].GetMean()),"P")

for g in graphs3:
    g.Draw("PSAME")

#leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
f.Draw("SAME")        
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/ctrVslyAbsTofOverDtMean_ProdDifferentColors"+ext)

frame4=R.TH2F("frame4","frame4",20,0.5,1.7,20,0.5,1.7)
frame4.SetStats(0)
frame4.GetXaxis().SetTitle("1/LO TOFPET normalised to REF (NoGeoCorr)")
frame4.GetYaxis().SetTitle("#sigma_{t} @ 511 KeV/120 ps")

frame4.Draw()
leg.Clear()
for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetLineColor(R.kBlack+iprod)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['ctrVslyTofNorm_'+prod+'_'+geo],"%s - <PMT>:%3.2f, <CTR>: %3.2f"%(prod,histos['ctrVslyTofNorm_'+prod+'_'+geo].GetMean(1),histos['ctrVslyTofNorm_'+prod+'_'+geo].GetMean(2)),"P")

#leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
f.Draw("SAME")        
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/ctrVslyTofNorm_ProdDifferentColors"+ext)

for igeo,geo in enumerate(geoms):
    frame4.Draw()
    leg.Clear()
    for iprod,prod in enumerate(producers): 
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetLineColor(R.kBlack+iprod)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].Draw("PSAME")
        leg.AddEntry(histos['ctrVslyTofNorm_'+prod+'_'+geo],"%s - <PMT>:%3.2f, <CTR>: %3.2f"%(prod,histos['ctrVslyTofNorm_'+prod+'_'+geo].GetMean(1),histos['ctrVslyTofNorm_'+prod+'_'+geo].GetMean(2)),"P")
    #leg.Draw()
    text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench - "+geo)
    f.Draw("SAME")        
    for ext in ['.pdf','.png']:
        c1.SaveAs("LYAnalysis/ctrVslyTofNorm_ProdDifferentColors"+geo+ext)

leg.Clear()
histos['lyRatio'].Rebin(2)
histos['lyRatio'].SetStats(0)
histos['lyRatio'].SetMarkerStyle(20)
histos['lyRatio'].SetMarkerSize(1.2)
histos['lyRatio'].SetMarkerColor(R.kBlack)
histos['lyRatio'].SetLineColor(R.kBlack)
histos['lyRatio'].SetLineWidth(4)
histos['lyRatio'].SetLineStyle(3)
histos['lyRatio'].Fit("gaus","LL","HSAME")
#histos['lyRatioStacked'].GetXaxis().SetTitle("LO LO Bench/TOFPET Bench")  
histos['lyRatio'].GetFunction("gaus").SetLineWidth(4)
histos['lyRatio'].GetFunction("gaus").SetLineStyle(2)
histos['lyRatio'].GetFunction("gaus").SetLineColor(R.kBlack)
histos['lyRatio'].Draw()
histos['lyRatio'].GetXaxis().SetTitle("LO Ratio PMT/TOFPET")
histos['lyRatio'].SetMaximum(histos['lyRatio'].GetMaximum()*1.7)

for iprod,prod in enumerate(producers): 
    histos['lyRatio_'+prod].Rebin(2)
    histos['lyRatio_'+prod].SetStats(0)
    histos['lyRatio_'+prod].SetLineColor(R.kBlack+iprod)
    histos['lyRatio_'+prod].SetLineWidth(1)
    histos['lyRatio_'+prod].SetFillStyle(3001)
    histos['lyRatio_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    histos['lyRatio_'+prod].GetXaxis().SetTitle("LO PMT/TOFPET")
    histos['lyRatio_'+prod].Fit("gaus","LL","HSAME")
    histos['lyRatio_'+prod].GetFunction("gaus").SetLineColor(R.kBlack+iprod)
    histos['lyRatio_'+prod].GetFunction("gaus").SetLineWidth(3)
    leg.AddEntry(histos['lyRatio_'+prod],"%s - Mean:%3.2f, RMS:%2.2f"%(prod,histos['lyRatio_'+prod].GetMean(),histos['lyRatio_'+prod].GetRMS()),'F')
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
text.SetTextSize(0.05)
text.DrawLatexNDC(0.6,0.47,"#sigma=%2.1f#pm%3.1f%%"%(histos['lyRatio'].GetFunction("gaus").GetParameter(2)*100,histos['lyRatio'].GetFunction("gaus").GetParError(2)*100))
text.SetTextSize(0.04)
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/lyRatioUnStacked_ProdDifferentColors"+ext)

#mainHisto=''
leg.Clear()

histos['lyRatioStacked']=R.THStack('lyRatioStacked','lyRatioStacked')
for iprod,prod in enumerate(producers): 
    histos['lyRatio_'+prod].Rebin(2)
    histos['lyRatio_'+prod].SetStats(0)
    histos['lyRatio_'+prod].GetXaxis().SetTitle("LO [#pe]")
    histos['lyRatio_'+prod].SetLineColor(R.kBlack+iprod)
    histos['lyRatio_'+prod].SetLineWidth(3)
    histos['lyRatio_'+prod].SetFillStyle(3001)
    histos['lyRatio_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    histos['lyRatio_'+prod].GetXaxis().SetTitle("LO PMT/TOFPET")
    histos['lyRatioStacked'].Add(histos['lyRatio_'+prod])
    leg.AddEntry(histos['lyRatio_'+prod],"%s - Mean:%3.2f, RMS:%2.2f"%(prod,histos['lyRatio_'+prod].GetMean(),histos['lyRatio_'+prod].GetRMS()),'F')

histos['lyRatioStacked'].Draw()
histos['lyRatioStacked'].GetXaxis().SetTitle("LO Ratio PMT/TOFPET")
histos['lyRatioStacked'].SetMaximum(histos['lyRatioStacked'].GetMaximum()*1.7)

histos['lyRatio'].Rebin(2)
histos['lyRatio'].SetMarkerStyle(20)
histos['lyRatio'].SetMarkerSize(1.2)
histos['lyRatio'].SetMarkerColor(R.kBlack)
histos['lyRatio'].SetLineColor(R.kBlack)
histos['lyRatio'].SetLineWidth(4)
histos['lyRatio'].SetLineStyle(3)
histos['lyRatio'].Fit("gaus","LL","HSAME")
#histos['lyRatioStacked'].GetXaxis().SetTitle("LO LO Bench/TOFPET Bench")  
histos['lyRatio'].GetFunction("gaus").SetLineWidth(4)
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT & TOFPET Bench")
text.SetTextSize(0.05)
text.DrawLatexNDC(0.6,0.47,"#sigma=%2.1f#pm%3.1f%%"%(histos['lyRatio'].GetFunction("gaus").GetParameter(2)*100,histos['lyRatio'].GetFunction("gaus").GetParError(2)*100))
text.SetTextSize(0.04)
for ext in ['.pdf','.png']:
    c1.SaveAs("LYAnalysis/lyRatio_ProdDifferentColors"+ext)



out=R.TFile("LYAnalysis/LYMergedPlots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()


