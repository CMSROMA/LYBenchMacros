import ROOT as R
R.gROOT.SetBatch(1)

crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("LYAnalysis/crystalsData.csv","id/C:prod/C:geo/C:pe/F:dt/F:ref/F:ly/F");

producers = [ 'prod'+str(i) for i in range(1,9) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

histos = {}
data = {}
for prod in producers: 
    histos['ly_'+prod]=R.TH1F('ly_'+prod,'ly_'+prod,400,0.,2000.)
    histos['lyAbs_'+prod]=R.TH1F('lyAbs_'+prod,'lyAbs_'+prod,400,0.,2000.)
    histos['lyAbsOverDt_'+prod]=R.TH1F('lyAbsOverDt_'+prod,'lyAbsOverDt_'+prod,400,0.,40.)
    histos['dt_'+prod]=R.TH1F('dt_'+prod,'dt_'+prod,100,20.,50.)
    histos['lyNorm_'+prod]=R.TH1F('lyNorm_'+prod,'lyNorm_'+prod,400,0.5,1.5)
    for geo in geoms:
        histos['ly_'+prod+'_'+geo]=R.TH1F('ly_'+prod+'_'+geo,'ly_'+prod+'_'+geo,400,0.,2000.)
        histos['lyAbs_'+prod+'_'+geo]=R.TH1F('lyAbs_'+prod+'_'+geo,'lyAbs_'+prod+'_'+geo,400,0.,2000.)
        histos['lyAbsOverDt_'+prod+'_'+geo]=R.TH1F('lyAbsOverDt_'+prod+'_'+geo,'lyAbsOverDt_'+prod+'_'+geo,400,0.,40.)
        histos['dt_'+prod+'_'+geo]=R.TH1F('dt_'+prod+'_'+geo,'dt_'+prod+'_'+geo,100,20.,50.)
        histos['lyNorm_'+prod+'_'+geo]=R.TH1F('lyNorm_'+prod+'_'+geo,'lyNorm_'+prod+'_'+geo,400,0.5,1.5)
        data[prod+'_'+geo] = []

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    if ( crys.ly < 0 or crys.ref < 0 or crys.dt < 0):
        continue
    histos['ly_'+prod].Fill(crys.ly/16.)
    histos['ly_'+prod+'_'+geo].Fill(crys.ly/16.)
    histos['lyAbs_'+prod].Fill(crys.ly/crys.ref*10000./16.)
    histos['lyAbs_'+prod+'_'+geo].Fill(crys.ly/crys.ref*10000./16.)
    histos['lyAbsOverDt_'+prod].Fill(crys.ly/crys.ref*10000./16./crys.dt)
    histos['lyAbsOverDt_'+prod+'_'+geo].Fill(crys.ly/crys.ref*10000./16./crys.dt)
    histos['lyNorm_'+prod].Fill(crys.ly/crys.ref)
    histos['lyNorm_'+prod+'_'+geo].Fill(crys.ly/crys.ref)
    histos['dt_'+prod].Fill(crys.dt)
    histos['dt_'+prod+'_'+geo].Fill(crys.dt)
    data[prod+'_'+geo].append({ 'lyNorm': crys.ly/crys.ref, 'dt': crys.dt })

for prod in producers: 
    for geo in geoms:
        histos['dtVslyNorm_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['dtVslyNorm_'+prod+'_'+geo].SetName('dtVslyNorm_'+prod+'_'+geo)
        for i,bar in enumerate(data[prod+'_'+geo]):
            histos['dtVslyNorm_'+prod+'_'+geo].SetPoint(i,bar['lyNorm'],bar['dt'])


c1=R.TCanvas("c1","c1",800,600)
R.gStyle.SetOptTitle(0)

text=R.TLatex()
text.SetTextSize(0.04)

leg=R.TLegend(0.5,0.6,0.92,0.88)
leg.SetBorderSize(0)
leg.SetFillColorAlpha(0,0)
leg.SetTextSize(0.03)

frame=R.TH2F("frame","frame",20,0.8,1.3,20,35,60)
frame.SetStats(0)
frame.GetXaxis().SetTitle("LO Normalised to REF bar")
frame.GetYaxis().SetTitle("Decay time [ns]")
frame.Draw()

for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['dtVslyNorm_'+prod+'_'+geo].SetMarkerStyle(20+iprod)
        histos['dtVslyNorm_'+prod+'_'+geo].SetMarkerColor(R.kBlack+igeo)
        histos['dtVslyNorm_'+prod+'_'+geo].Draw("PSAME")

text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/dtVslyNorm_GeomDifferentColors"+ext)

frame.Draw()
leg.Clear()
for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['dtVslyNorm_'+prod+'_'+geo].SetMarkerStyle(20+iprod)
        histos['dtVslyNorm_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['dtVslyNorm_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['dtVslyNorm_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['dtVslyNorm_'+prod+'_'+geo],"%s - Mean LO:%3.2f, DT: %3.1f"%(prod,histos['dtVslyNorm_'+prod+'_'+geo].GetMean(1),histos['dtVslyNorm_'+prod+'_'+geo].GetMean(2)),"P")
        
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/dtVslyNorm_ProdDifferentColors"+ext)

maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
    histos['ly_'+prod].Rebin(4)
    histos['ly_'+prod].SetStats(0)
    histos['ly_'+prod].GetXaxis().SetTitle("LO [#pe]")
    histos['ly_'+prod].SetLineColor(R.kBlack+iprod)
    histos['ly_'+prod].SetLineWidth(3)
    histos['ly_'+prod].SetLineStyle(iprod/4+1)
    histos['ly_'+prod].SetFillStyle(3001)
    histos['ly_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['ly_'+prod],"%s - Mean:%3.1f, RMS:%2.1f"%(prod,histos['ly_'+prod].GetMean(),histos['ly_'+prod].GetRMS()),'F')

    if (histos['ly_'+prod].GetMaximum()>maxH):
        maxH=histos['ly_'+prod].GetMaximum()

    if (iprod==0):
        histos['ly_'+prod].Draw()
        mainHisto='ly_'+prod
    else:
        histos['ly_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(450,950)
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/ly_ProdDifferentColors"+ext)

maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
    histos['lyNorm_'+prod].Rebin(8)
    histos['lyNorm_'+prod].SetStats(0)
    histos['lyNorm_'+prod].GetXaxis().SetTitle("LO normalised to REF daily")
    histos['lyNorm_'+prod].SetLineColor(R.kBlack+iprod)
    histos['lyNorm_'+prod].SetLineWidth(3)
    histos['lyNorm_'+prod].SetLineStyle(iprod/4+1)
    histos['lyNorm_'+prod].SetFillStyle(3001)
    histos['lyNorm_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['lyNorm_'+prod],"%s - Mean:%3.2f, RMS:%3.2f"%(prod,histos['lyNorm_'+prod].GetMean(),histos['lyNorm_'+prod].GetRMS()),'F')
    if (histos['lyNorm_'+prod].GetMaximum()>maxH):
        maxH=histos['lyNorm_'+prod].GetMaximum()

    if (iprod==0):
        histos['lyNorm_'+prod].Draw()
        mainHisto='lyNorm_'+prod
    else:
        histos['lyNorm_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(0.8,1.4)
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/lyNorm_ProdDifferentColors"+ext)

maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
    histos['lyAbs_'+prod].Rebin(4)
    histos['lyAbs_'+prod].SetStats(0)
    histos['lyAbs_'+prod].GetXaxis().SetTitle("LO normalised to REF daily [#pe]")
    histos['lyAbs_'+prod].SetLineColor(R.kBlack+iprod)
    histos['lyAbs_'+prod].SetLineWidth(3)
    histos['lyAbs_'+prod].SetLineStyle(iprod/4+1)
    histos['lyAbs_'+prod].SetFillStyle(3001)
    histos['lyAbs_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['lyAbs_'+prod],"%s - Mean:%3.1f, RMS:%3.1f"%(prod,histos['lyAbs_'+prod].GetMean(),histos['lyAbs_'+prod].GetRMS()),'F')

    if (histos['lyAbs_'+prod].GetMaximum()>maxH):
        maxH=histos['lyAbs_'+prod].GetMaximum()

    if (iprod==0):
        histos['lyAbs_'+prod].Draw()
        mainHisto='lyAbs_'+prod
    else:
        histos['lyAbs_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(500.,900.)
leg.Draw()

text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/lyAbs_ProdDifferentColors"+ext)

maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
    histos['lyAbsOverDt_'+prod].Rebin(4)
    histos['lyAbsOverDt_'+prod].SetStats(0)
    histos['lyAbsOverDt_'+prod].GetXaxis().SetTitle("LO/Decay Time [#pe/ns]")
    histos['lyAbsOverDt_'+prod].SetLineColor(R.kBlack+iprod)
    histos['lyAbsOverDt_'+prod].SetLineWidth(3)
    histos['lyAbsOverDt_'+prod].SetLineStyle(iprod/4+1)
    histos['lyAbsOverDt_'+prod].SetFillStyle(3001)
    histos['lyAbsOverDt_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['lyAbsOverDt_'+prod],"%s - Mean:%3.1f, RMS:%2.1f"%(prod,histos['lyAbsOverDt_'+prod].GetMean(),histos['lyAbsOverDt_'+prod].GetRMS()),'F')

    if (histos['lyAbsOverDt_'+prod].GetMaximum()>maxH):
        maxH=histos['lyAbsOverDt_'+prod].GetMaximum()

    if (iprod==0):
        histos['lyAbsOverDt_'+prod].Draw()
        mainHisto='lyAbsOverDt_'+prod
    else:
        histos['lyAbsOverDt_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(10.,20.)
leg.Draw()

text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/lyAbsOverDt_ProdDifferentColors"+ext)

out=R.TFile("LYAnalysis/LYplots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()
