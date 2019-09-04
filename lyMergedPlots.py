import pandas as pd
import ROOT as R
R.gROOT.SetBatch(1)

lyBenchData = pd.read_csv("LYAnalysis/crystalsData.csv",header=None,index_col=0) 
tofpetData = pd.read_csv("LYAnalysis/lyAnalysisTOFPET.csv",header=None,index_col=0,usecols=[0,3,4,5,6,7,8]) 
result = pd.concat([lyBenchData,tofpetData], axis=1, join='inner')
result.to_csv("LYAnalysis/lyAnalysisMerged.csv",header=False)

crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("LYAnalysis/lyAnalysisMerged.csv","id/C:prod/C:geo/C:pe/F:dt/F:ref/F:ly/F:lyTof/F:lyTofCoinc/F:ctrTof/F:lyRefTof/F:lyRefTofCoinc/F:ctrRefTof/F");

producers = [ 'prod'+str(i) for i in range(1,7) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

histos = {}
data = {}
histos['lyRatio']=R.TH1F('lyRatio','lyRatio',100,0.5,1.5)
for prod in producers: 
    histos['lyRatio_'+prod]=R.TH1F('lyRatio_'+prod,'lyRatio_'+prod,100,0.5,1.5)
    for geo in geoms:
        histos['lyRatio_'+prod+'_'+geo]=R.TH1F('lyRatio_'+prod+'_'+geo,'lyRatio_'+prod+'_'+geo,100,0.5,1.5)
        data[prod+'_'+geo] = []

#1.06 needed to get average ratio between producers@ 1 
ratiosTof = { 'geo1': 0.9/1.06, 'geo2':1/1.06, 'geo3':1.03/1.06 }

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    if ( crys.ly < 0 or crys.ref < 0 or crys.dt < 0 or crys.lyTofCoinc<0 or crys.ctrTof<0 or crys.lyRefTofCoinc<0 or crys.ctrRefTof<0 ):
        continue
    data[prod+'_'+geo].append({ 'ly':crys.ly, 'lyGeoRatio':crys.ly*ratiosTof[geo], 'lyTof':crys.lyTofCoinc/ratiosTof[geo], 'lyNorm': crys.ly/crys.ref, 'lyNormGeoRatio': crys.ly*ratiosTof[geo]/crys.ref, 'dt': crys.dt, 'lyTofNorm': crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo], 'ctr': crys.ctrTof, 'lyTofNoGeoRatio':crys.lyTofCoinc, 'lyTofNormNoGeoRatio': crys.lyTofCoinc/crys.lyRefTofCoinc })
    histos['lyRatio'].Fill((crys.ly/crys.ref)/(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo]))
    histos['lyRatio_'+prod+'_'+geo].Fill((crys.ly/crys.ref)/(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo]))
    histos['lyRatio_'+prod].Fill((crys.ly/crys.ref)/(crys.lyTofCoinc/crys.lyRefTofCoinc/ratiosTof[geo]))

for prod in producers: 
    for geo in geoms:
        histos['lyNormCorr_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['lyNormCorr_'+prod+'_'+geo].SetName('lyNormCorr_'+prod+'_'+geo)
        histos['lyCorr_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['lyCorr_'+prod+'_'+geo].SetName('lyCorr_'+prod+'_'+geo)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetName('ctrVslyAbsOverDt__'+prod+'_'+geo)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetName('ctrVslyAbsTofOverDt_'+prod+'_'+geo)
        histos['ctrVslyTofNorm_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetName('ctrVslyTofNorm_'+prod+'_'+geo)
        for i,barData in enumerate(data[prod+'_'+geo]):
            histos['lyNormCorr_'+prod+'_'+geo].SetPoint(i,barData['lyNorm'],barData['lyTofNorm'])
            histos['lyCorr_'+prod+'_'+geo].SetPoint(i,barData['ly'],barData['lyTof'])
            histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetPoint(i,barData['lyNormGeoRatio']*10000./16./barData['dt']/13.,barData['ctr']/160.,)
            histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetPoint(i,barData['lyTofNormNoGeoRatio']*10000./16./barData['dt']/13.,barData['ctr']/160.)
            histos['ctrVslyTofNorm_'+prod+'_'+geo].SetPoint(i,barData['lyTofNormNoGeoRatio']*1.06,barData['ctr']/160.)

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
frame.GetXaxis().SetTitle("LO Normalised to REF bar (LO Bench)")
frame.GetYaxis().SetTitle("LO Normalised to REF bar (TOFPET Bench+GeoCorr)")

frame.Draw()
leg.Clear()

f=R.TF1("f","x",0.8,1.2)
f.SetLineColor(R.kRed+3)
f.SetLineWidth(4)
for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['lyNormCorr_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['lyNormCorr_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['lyNormCorr_'+prod+'_'+geo],"%s - <LO>:%3.2f, <TOFPET>: %3.2f"%(prod,histos['lyNormCorr_'+prod+'_'+geo].GetMean(1),histos['lyNormCorr_'+prod+'_'+geo].GetMean(2)),"P")
f.Draw("SAME")        
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - LO & TOFPET Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/lyNormCorr_ProdDifferentColors"+ext)

frame2=R.TH2F("frame2","frame2",20,0.7,1.5,20,0.7,1.5)
frame2.SetStats(0)
frame2.GetXaxis().SetTitle("LO LO Bench (GeoCorr)/Decay Time/13 #pe/ns")
frame2.GetYaxis().SetTitle("CTR/160 ps")

frame2.Draw()
leg.Clear()

for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyAbsOverDt_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['ctrVslyAbsOverDt_'+prod+'_'+geo],"%s - <LO/#tau>:%3.2f, <CTR>: %3.2f"%(prod,histos['ctrVslyAbsOverDt_'+prod+'_'+geo].GetMean(1),histos['ctrVslyAbsOverDt_'+prod+'_'+geo].GetMean(2)),"P")

leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - LO & TOFPET Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/ctrVslyAbsOverDt_ProdDifferentColors"+ext)

frame3=R.TH2F("frame3","frame3",20,0.7,1.5,20,0.7,1.5)
frame3.SetStats(0)
frame3.GetXaxis().SetTitle("LO TOFPET Bench (NoGeoCorr)/Decay Time/ 13 #pe/ns")
frame3.GetYaxis().SetTitle("CTR/160 ps")

frame3.Draw()
leg.Clear()

for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo],"%s - <LO/#tau>:%3.2f, <CTR>: %3.2f"%(prod,histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(1),histos['ctrVslyAbsTofOverDt_'+prod+'_'+geo].GetMean(2)),"P")

leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - LO & TOFPET Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/ctrVslyAbsTofOverDt_ProdDifferentColors"+ext)

frame4=R.TH2F("frame4","frame4",20,0.7,1.5,20,0.7,1.5)
frame4.SetStats(0)
frame4.GetXaxis().SetTitle("LO TOFPET Bench normalised to REF (NoGeoCorr)")
frame4.GetYaxis().SetTitle("CTR/160 ps")

frame4.Draw()
leg.Clear()

for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerStyle(20+igeo)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyTofNorm_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['ctrVslyTofNorm_'+prod+'_'+geo],"%s - <LO>:%3.2f, <CTR>: %3.2f"%(prod,histos['ctrVslyTofNorm_'+prod+'_'+geo].GetMean(1),histos['ctrVslyTofNorm_'+prod+'_'+geo].GetMean(2)),"P")

leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - LO & TOFPET Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/ctrVslyTofNorm_ProdDifferentColors"+ext)

#mainHisto=''
leg.Clear()
histos['lyRatioStacked']=R.THStack('lyRatioStacked','lyRatioStacked')
for iprod,prod in enumerate(producers): 
    histos['lyRatio_'+prod].Rebin(4)
    histos['lyRatio_'+prod].SetStats(0)
    histos['lyRatio_'+prod].GetXaxis().SetTitle("LO [#pe]")
    histos['lyRatio_'+prod].SetLineColor(R.kBlack+iprod)
    histos['lyRatio_'+prod].SetLineWidth(3)
    histos['lyRatio_'+prod].SetFillStyle(3001)
    histos['lyRatio_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    histos['lyRatio_'+prod].GetXaxis().SetTitle("LO LO Bench/TOFPET Bench")
    histos['lyRatioStacked'].Add(histos['lyRatio_'+prod])
    leg.AddEntry(histos['lyRatio_'+prod],"%s - Mean:%3.2f, RMS:%2.2f"%(prod,histos['lyRatio_'+prod].GetMean(),histos['lyRatio_'+prod].GetRMS()),'F')

histos['lyRatioStacked'].Draw()
histos['lyRatioStacked'].GetXaxis().SetTitle("LO Ratio LO Bench/TOFPET Bench")
histos['lyRatioStacked'].SetMaximum(histos['lyRatioStacked'].GetMaximum()*1.7)

histos['lyRatio'].Rebin(4)
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
text.DrawLatexNDC(0.12,0.91,"CMS Rome - LO & TOFPET Bench")
text.SetTextSize(0.05)
text.DrawLatexNDC(0.6,0.47,"#sigma=%2.1f#pm%3.1f%%"%(histos['lyRatio'].GetFunction("gaus").GetParameter(2)*100,histos['lyRatio'].GetFunction("gaus").GetParError(2)*100))
text.SetTextSize(0.04)
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/lyRatio_ProdDifferentColors"+ext)

out=R.TFile("LYAnalysis/LYMergedPlots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()


