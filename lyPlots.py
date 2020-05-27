import ROOT as R
R.gROOT.SetBatch(1)

crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("LYAnalysis/crystalsData.csv","id/C:prod/C:geo/C:i0/F:i3/F:i2/F:i1/F:pe/F:dt/F:ref/F:ly/F");

producers = [ 'prod'+str(i) for i in range(1,10) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

histos = {}
data = {}

refLY=624.3 #from refAnalysis
qe=0.25 #rough average QE around 420nm from datasheet
 
histos['lyVSlyAbs']=R.TH2F('lyVSlyAbs','lyVSlyAbs',400,0.,2000.,400,0.,2000.)
for prod in producers: 
    histos['i0_'+prod]=R.TH1F('i0_'+prod,'i0_'+prod,200,0.,1.)
    histos['i1_'+prod]=R.TH1F('i1_'+prod,'i1_'+prod,200,0.,1.)
    histos['i2_'+prod]=R.TH1F('i2_'+prod,'i2_'+prod,100,0.95,1.)
    histos['ly_'+prod]=R.TH1F('ly_'+prod,'ly_'+prod,400,0.,2000.)
    histos['lyAbs_'+prod]=R.TH1F('lyAbs_'+prod,'lyAbs_'+prod,400,0.,2000.)
    histos['lyAbsAvgQECorr_'+prod]=R.TH1F('lyAbsAvgQECorr_'+prod,'lyAbsAvgQECorr_'+prod,400,0.,10000.)
    histos['lyAbsOverDt_'+prod]=R.TH1F('lyAbsOverDt_'+prod,'lyAbsOverDt_'+prod,400,0.,400.)
    histos['dt_'+prod]=R.TH1F('dt_'+prod,'dt_'+prod,100,20.,50.)
    histos['lyNorm_'+prod]=R.TH1F('lyNorm_'+prod,'lyNorm_'+prod,400,0.5,1.5)
    for geo in geoms:
        histos['ly_'+prod+'_'+geo]=R.TH1F('ly_'+prod+'_'+geo,'ly_'+prod+'_'+geo,400,0.,2000.)
        histos['lyAbs_'+prod+'_'+geo]=R.TH1F('lyAbs_'+prod+'_'+geo,'lyAbs_'+prod+'_'+geo,400,0.,2000.)
        histos['lyAbsOverDt_'+prod+'_'+geo]=R.TH1F('lyAbsOverDt_'+prod+'_'+geo,'lyAbsOverDt_'+prod+'_'+geo,400,0.,400.)
        histos['dt_'+prod+'_'+geo]=R.TH1F('dt_'+prod+'_'+geo,'dt_'+prod+'_'+geo,100,20.,50.)
        histos['lyNorm_'+prod+'_'+geo]=R.TH1F('lyNorm_'+prod+'_'+geo,'lyNorm_'+prod+'_'+geo,400,0.5,1.5)
        data[prod+'_'+geo] = []

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    if ( crys.ly < 0 or crys.ref < 0 or crys.dt < 0):
        continue
    lyAbsAvgQECorr=(crys.ly/crys.ref*refLY+crys.ly/crys.pe)/2./qe/0.511
    histos['lyVSlyAbs'].Fill(crys.ly/crys.ref*refLY,crys.ly/crys.pe)
    histos['ly_'+prod].Fill(crys.ly/crys.pe)
    histos['i0_'+prod].Fill(crys.i0/crys.i3)
    histos['i1_'+prod].Fill(crys.i1/crys.i3)
    histos['i2_'+prod].Fill(crys.i2/crys.i3)
    histos['lyAbsAvgQECorr_'+prod].Fill(lyAbsAvgQECorr)
    histos['ly_'+prod+'_'+geo].Fill(crys.ly/crys.pe)
    histos['lyAbs_'+prod].Fill(crys.ly/crys.ref*refLY)
    histos['lyAbs_'+prod+'_'+geo].Fill(crys.ly/crys.ref*refLY)
    histos['lyAbsOverDt_'+prod].Fill(lyAbsAvgQECorr/crys.dt)
    histos['lyAbsOverDt_'+prod+'_'+geo].Fill(lyAbsAvgQECorr/crys.dt)
    histos['lyNorm_'+prod].Fill(crys.ly/crys.ref)
    histos['lyNorm_'+prod+'_'+geo].Fill(crys.ly/crys.ref)
    histos['dt_'+prod].Fill(crys.dt)
    histos['dt_'+prod+'_'+geo].Fill(crys.dt)
    data[prod+'_'+geo].append({ 'lyNorm': crys.ly/crys.ref, 'dt': crys.dt, 'lyAbsAvgQECorr':lyAbsAvgQECorr })

for prod in producers: 
    for geo in geoms:
        histos['dtVslyNorm_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['dtVslyNorm_'+prod+'_'+geo].SetName('dtVslyNorm_'+prod+'_'+geo)
        histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo].SetName('dtVslyAbsAvgQECorr_'+prod+'_'+geo)
        for i,bar in enumerate(data[prod+'_'+geo]):
            histos['dtVslyNorm_'+prod+'_'+geo].SetPoint(i,bar['lyNorm'],bar['dt'])
            histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo].SetPoint(i,bar['lyAbsAvgQECorr'],bar['dt'])


c1=R.TCanvas("c1","c1",800,600)
R.gStyle.SetOptTitle(0)

text=R.TLatex()
text.SetTextSize(0.04)

leg=R.TLegend(0.45,0.6,0.92,0.88)
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
            leg.AddEntry(histos['dtVslyNorm_'+prod+'_'+geo],"%s - LO:%3.2f, DT: %3.1f"%(prod,histos['dtVslyNorm_'+prod+'_'+geo].GetMean(1),histos['dtVslyNorm_'+prod+'_'+geo].GetMean(2)),"P")
        
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/dtVslyNorm_ProdDifferentColors"+ext)


frame1=R.TH2F("frame1","frame1",20,4000,7000,20,35,60)
frame1.SetStats(0)
frame1.GetXaxis().SetTitle("LO [photons/MeV]")
frame1.GetYaxis().SetTitle("Decay time [ns]")
frame1.Draw()

leg.Clear()
for iprod,prod in enumerate(producers): 
    for igeo,geo in enumerate(geoms):
        histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo].SetMarkerStyle(20+iprod)
        histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo].Draw("PSAME")
        if (igeo==0):
            leg.AddEntry(histos['dtVslyAbsAvgQECorr_'+prod+'_'+geo],"%s - LO:%.2E, DT: %3.1f"%(prod,histos['lyAbsAvgQECorr_'+prod].GetMean(),histos['dt_'+prod].GetMean()),"P")
        
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/dtVslyAbsAvgQECorr_ProdDifferentColors"+ext)

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
#    histos['dt_'+prod].Rebin(4)
    histos['dt_'+prod].SetStats(0)
    histos['dt_'+prod].GetXaxis().SetTitle("Decay Time [ns]")
    histos['dt_'+prod].SetLineColor(R.kBlack+iprod)
    histos['dt_'+prod].SetLineWidth(3)
    histos['dt_'+prod].SetLineStyle(iprod/4+1)
    histos['dt_'+prod].SetFillStyle(3001)
    histos['dt_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['dt_'+prod],"%s - Mean:%3.2f, RMS:%2.3f"%(prod,histos['dt_'+prod].GetMean(),histos['dt_'+prod].GetRMS()),'F')

    if (histos['dt_'+prod].GetMaximum()>maxH):
        maxH=histos['dt_'+prod].GetMaximum()

    if (iprod==0):
        histos['dt_'+prod].Draw()
        mainHisto='dt_'+prod
    else:
        histos['dt_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(35,50)
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")

arr0=R.TArrow(45,4,45,0,0.03,"|>")
arr0.SetLineWidth(3)
arr0.SetArrowSize(0.03)
arr0.SetFillColor(1)
#arr0.Draw()

for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/dt_ProdDifferentColors"+ext)

maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
#    histos['i0_'+prod].Rebin(4)
    histos['i0_'+prod].SetStats(0)
    histos['i0_'+prod].GetXaxis().SetTitle("LO(30ns)/LO(450ns)")
    histos['i0_'+prod].SetLineColor(R.kBlack+iprod)
    histos['i0_'+prod].SetLineWidth(3)
    histos['i0_'+prod].SetLineStyle(iprod/4+1)
    histos['i0_'+prod].SetFillStyle(3001)
    histos['i0_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['i0_'+prod],"%s - Mean:%3.2f, RMS:%2.3f"%(prod,histos['i0_'+prod].GetMean(),histos['i0_'+prod].GetRMS()),'F')

    if (histos['i0_'+prod].GetMaximum()>maxH):
        maxH=histos['i0_'+prod].GetMaximum()

    if (iprod==0):
        histos['i0_'+prod].Draw()
        mainHisto='i0_'+prod
    else:
        histos['i0_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(0.25,0.4)
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")

arr0=R.TArrow(0.26,4,0.26,0,0.03,"|>")
arr0.SetLineWidth(3)
arr0.SetArrowSize(0.03)
arr0.SetFillColor(1)
#arr0.Draw()

for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/i0_ProdDifferentColors"+ext)


maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
#    histos['i1_'+prod].Rebin(4)
    histos['i1_'+prod].SetStats(0)
    histos['i1_'+prod].GetXaxis().SetTitle("LO(50ns)/LO(450ns)")
    histos['i1_'+prod].SetLineColor(R.kBlack+iprod)
    histos['i1_'+prod].SetLineWidth(3)
    histos['i1_'+prod].SetLineStyle(iprod/4+1)
    histos['i1_'+prod].SetFillStyle(3001)
    histos['i1_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['i1_'+prod],"%s - Mean:%3.2f, RMS:%2.3f"%(prod,histos['i1_'+prod].GetMean(),histos['i1_'+prod].GetRMS()),'F')

    if (histos['i1_'+prod].GetMaximum()>maxH):
        maxH=histos['i1_'+prod].GetMaximum()

    if (iprod==0):
        histos['i1_'+prod].Draw()
        mainHisto='i1_'+prod
    else:
        histos['i1_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(0.45,0.65)
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")

arr1=R.TArrow(0.5,4,0.5,0,0.03,"|>")
arr1.SetLineWidth(3)
arr1.SetArrowSize(0.03)
arr1.SetFillColor(1)
#arr1.Draw()

for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/i1_ProdDifferentColors"+ext)

maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
#    histos['i2_'+prod].Rebin(4)
    histos['i2_'+prod].SetStats(0)
    histos['i2_'+prod].GetXaxis().SetTitle("LO(300ns)/LO(450ns)")
    histos['i2_'+prod].SetLineColor(R.kBlack+iprod)
    histos['i2_'+prod].SetLineWidth(3)
    histos['i2_'+prod].SetLineStyle(iprod/4+1)
    histos['i2_'+prod].SetFillStyle(3001)
    histos['i2_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['i2_'+prod],"%s - Mean:%3.3f, RMS:%2.3f"%(prod,histos['i2_'+prod].GetMean(),histos['i2_'+prod].GetRMS()),'F')

    if (histos['i2_'+prod].GetMaximum()>maxH):
        maxH=histos['i2_'+prod].GetMaximum()

    if (iprod==0):
        histos['i2_'+prod].Draw()
        mainHisto='i2_'+prod
    else:
        histos['i2_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(0.99,1.)
leg.Draw()
text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")

arr2=R.TArrow(0.992,4,0.992,0,0.03,"|>")
arr2.SetLineWidth(3)
arr2.SetArrowSize(0.03)
arr2.SetFillColor(1)
#arr2.Draw()

for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/i2_ProdDifferentColors"+ext)

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
    histos['lyAbsAvgQECorr_'+prod].Rebin(4)
    histos['lyAbsAvgQECorr_'+prod].SetStats(0)
    histos['lyAbsAvgQECorr_'+prod].GetXaxis().SetTitle("LO [photons/MeV]")
    histos['lyAbsAvgQECorr_'+prod].SetLineColor(R.kBlack+iprod)
    histos['lyAbsAvgQECorr_'+prod].SetLineWidth(2)
    histos['lyAbsAvgQECorr_'+prod].SetLineStyle(iprod/4+1)
    histos['lyAbsAvgQECorr_'+prod].SetFillStyle(3001)
    histos['lyAbsAvgQECorr_'+prod].SetFillColorAlpha(R.kBlack+iprod,0.45)
    leg.AddEntry(histos['lyAbsAvgQECorr_'+prod],"%s Mean:%.1E,RMS:%.1E"%(prod,histos['lyAbsAvgQECorr_'+prod].GetMean(),histos['lyAbsAvgQECorr_'+prod].GetRMS()),'F')

    if (histos['lyAbsAvgQECorr_'+prod].GetMaximum()>maxH):
        maxH=histos['lyAbsAvgQECorr_'+prod].GetMaximum()

    if (iprod==0):
        histos['lyAbsAvgQECorr_'+prod].Draw()
        mainHisto='lyAbsAvgQECorr_'+prod
    else:
        histos['lyAbsAvgQECorr_'+prod].Draw("SAME")

histos[mainHisto].SetMaximum(maxH*1.7)
histos[mainHisto].GetXaxis().SetRangeUser(3500.,8000.)
leg.Draw()

text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
text.DrawLatexNDC(0.14,0.82,"Dry optical coupling")
text.DrawLatexNDC(0.14,0.77,"No wrapping")
text.DrawLatexNDC(0.14,0.72,"One end open")

arr=R.TArrow(4000,4,4000,0,0.03,"|>")
arr.SetLineWidth(3)
arr.SetArrowSize(0.03)
arr.SetFillColor(1)
#arr.Draw()

R.gPad.RedrawAxis()
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/lyAbsAvgQECorr_ProdDifferentColors"+ext)

maxH=0
mainHisto=''
leg.Clear()
for iprod,prod in enumerate(producers): 
    histos['lyAbsOverDt_'+prod].Rebin(2)
    histos['lyAbsOverDt_'+prod].SetStats(0)
    histos['lyAbsOverDt_'+prod].GetXaxis().SetTitle("LO/Decay Time [photons/MeV/ns]")
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
histos[mainHisto].GetXaxis().SetRangeUser(80.,180.)
leg.Draw()

arr4=R.TArrow(100,4,100,0,0.03,"|>")
arr4.SetLineWidth(3)
arr4.SetArrowSize(0.03)
arr4.SetFillColor(1)
#arr4.Draw()

text.DrawLatexNDC(0.12,0.91,"CMS Rome - PMT Bench")
for ext in ['.pdf','.png','.C']:
    c1.SaveAs("LYAnalysis/lyAbsOverDt_ProdDifferentColors"+ext)

out=R.TFile("LYAnalysis/LYplots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()
