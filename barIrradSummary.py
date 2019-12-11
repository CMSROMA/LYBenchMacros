import ROOT as R

def Map(tf):
    """                                                                                                                  
    Maps objets as dict[obj_name][0] using a TFile (tf) and TObject to browse.                                           
    """
    m = {}
    for k in tf.GetListOfKeys():
        n = k.GetName()
        m[n] = tf.Get(n)
    return m


f=R.TFile("LYIrradAnalysisMerged/LYMergedPlots.root","UPDATE")
objs=Map(f)

R.gStyle.SetOptTitle(0)
R.gStyle.SetOptStat(0)
R.gStyle.SetOptFit(111111)

c=R.TCanvas("c","c",900,600)

objs['lyNormAbs_Ratio'].Rebin(4)
objs['lyNormAbs_Ratio'].Draw("")
objs['lyNormAbs_Ratio'].Fit("gaus","LR","",0.8,1.2)
objs['lyNormAbs_Ratio'].GetXaxis().SetTitle("LY Ratio PMT/TOFPET")

for ext in ['.pdf','.png']:
    c.SaveAs("LYIrradAnalysisMerged/lyNormRatio"+ext)

a=R.TH2F("a","a",10,0.7,1.2,10,0.7,1.2)
a.GetXaxis().SetTitle("LY/LY_{ref} PMT")
a.GetYaxis().SetTitle("LY/LY_{ref} TOFPET")
a.Draw()

objs['lyNormAbs_TOFPETvsPMT'].SetMarkerStyle(21)
objs['lyNormAbs_TOFPETvsPMT'].SetMarkerColor(R.kBlack)
objs['lyNormAbs_TOFPETvsPMT'].SetMarkerSize(0.5)
objs['lyNormAbs_TOFPETvsPMT'].Draw("PSAME")

f1=R.TF1("f1","x",0.7,1.3)
f1.SetLineWidth(3)
f1.Draw("SAME")

for ext in ['.pdf','.png']:
    c.SaveAs("LYIrradAnalysisMerged/lyNormCorrelation"+ext)

a1={}
a1_Y_Range={ 'lyNormAbs_AVG' : [0.7,1.2], 'ctr' : [80,200], 'dt': [35,50], 'lyNormAbsOverDt': [0.018,0.028], 'lyNormRelRescaled_AVG' : [0.8,1.1], 'lyNormRelRescaled_AVG_ExpFitSlope' : [-3E-5,2E-5], 'lyNormAbs_Ratio': [0.8,1.2] }
a1_Y_Title={ 'lyNormAbs_AVG' : 'LY/LY_{ref} (PMT+TOFPET)', 'ctr' : '#sigma_{t} [ps]', 'dt': 'Decay time [ns]' , 'lyNormAbsOverDt': 'Normalized LY/Decay time [ns^{-1}]', 'lyNormRelRescaled_AVG' : 'LY_{bef}/LY_{aft} (PMT+TOFPET)', 'lyNormRelRescaled_AVG_ExpFitSlope': 'Exp Fit Slope', 'lyNormAbs_Ratio' : 'LY(PMT)/LY(TOFPET)'}

labels={ '': 'Before Irr', '_IRR9K':'9 kGy' }

leg=R.TLegend(0.75,0.75,0.86,0.91)
leg.SetBorderSize(0)
leg.SetFillColorAlpha(0,0)
leg.SetTextSize(0.04)

for ig,g in enumerate(['lyNormAbs_AVG','ctr','dt','lyNormAbsOverDt','lyNormAbs_Ratio']):
    a1[g]=R.TH2F("a1_"+g,"a1_"+g,10,0,10,10,a1_Y_Range[g][0],a1_Y_Range[g][1])
    a1[g].GetXaxis().SetTitle("Prod #")
    a1[g].GetYaxis().SetTitle(a1_Y_Title[g])
    a1[g].Draw()
    leg.Clear()
    for id,dose in enumerate(['','_IRR9K']):
        objs[g+dose+'_ByProd'].SetMarkerStyle(21)
        objs[g+dose+'_ByProd'].SetMarkerColor(R.kBlack+id)
        objs[g+dose+'_ByProd'].SetLineColor(R.kBlack+id)
        objs[g+dose+'_ByProd'].SetMarkerSize(1.2)
        objs[g+dose+'_ByProd'].Draw("PSAME")
        leg.AddEntry(objs[g+dose+'_ByProd'],labels[dose],"PL")
    leg.Draw()

    for ext in ['.pdf','.png']:
        c.SaveAs("LYIrradAnalysisMerged/"+g+"ByProd"+ext)

a2=R.TH2F("a2","a2",10,1,1E5,10,0.7,1.2)
a2.GetXaxis().SetTitle("Dose [Gy]")
a2.GetYaxis().SetTitle("LY_{bef}/LY_{after} (PMT+TOFPET)")
a2.Draw()

R.gStyle.SetOptFit(0)
c.SetLogx(1)

objs['lyNormRelRescaled_AVG_ExpFitSlope_ByProd']=R.TGraphErrors(9)

leg2=R.TLegend(0.8,0.6,0.88,0.89)
leg2.SetBorderSize(0)
leg2.SetFillColorAlpha(0,0)
leg2.SetTextSize(0.03)
leg2.Clear()

for ip,prod in enumerate([ 'prod'+str(i) for i in range(1,10) ]):
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].Fit("expo","+")
    objs['lyNormRelRescaled_AVG_ExpFitSlope_ByProd'].SetPoint(ip,ip+1, objs['lyNormRel_AVG_RescaledVsDose_'+prod].GetFunction("expo").GetParameter(1))
    objs['lyNormRelRescaled_AVG_ExpFitSlope_ByProd'].SetPointError(ip,0, objs['lyNormRel_AVG_RescaledVsDose_'+prod].GetFunction("expo").GetParError(1))

    for i in range(0, objs['lyNormRel_AVG_RescaledVsDose_'+prod].GetN()):
        x,y=R.Double(0.),R.Double(0.)
        objs['lyNormRel_AVG_RescaledVsDose_'+prod].GetPoint(i,x,y)
        objs['lyNormRel_AVG_RescaledVsDose_'+prod].SetPoint(i,x*(1+0.07*ip),y)

    objs['lyNormRel_AVG_RescaledVsDose_'+prod].GetFunction("expo").SetLineColor(R.kBlack+ip)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].GetFunction("expo").SetLineStyle((R.kBlack+ip)%4)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].GetFunction("expo").SetLineWidth(2)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].SetMarkerStyle(20+ip)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].SetMarkerColor(R.kBlack+ip)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].SetMarkerSize(1.2)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].SetLineColor(R.kBlack+ip)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].SetLineStyle((R.kBlack+ip)%4)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].SetLineWidth(2)
    objs['lyNormRel_AVG_RescaledVsDose_'+prod].Draw("PSAME")
    leg2.AddEntry(objs['lyNormRel_AVG_RescaledVsDose_'+prod],prod,"PL")

leg2.Draw()

for ext in ['.pdf','.png']:
    c.SaveAs("LYIrradAnalysisMerged/lyNormRelRescaled_AVG_VsDose"+ext)
c.SetLogx(0)        

for ig,g in enumerate(['lyNormRelRescaled_AVG']):
    a1[g]=R.TH2F("a1_"+g,"a1_"+g,10,0,10,10,a1_Y_Range[g][0],a1_Y_Range[g][1])
    a1[g].GetXaxis().SetTitle("Prod #")
    a1[g].GetYaxis().SetTitle(a1_Y_Title[g])
    a1[g].Draw()
    leg.Clear()
    for id,dose in enumerate(['_IRR9K']):
        objs[g+dose+'_ByProd'].SetMarkerStyle(21)
        objs[g+dose+'_ByProd'].SetMarkerColor(R.kBlack+id)
        objs[g+dose+'_ByProd'].SetLineColor(R.kBlack+id)
        objs[g+dose+'_ByProd'].SetMarkerSize(1.2)
        objs[g+dose+'_ByProd'].Draw("PSAME")
        if (g == 'lyNormRelRescaled_AVG' ):
            objs[g+dose+'_ByProd'].Fit("pol0")
        leg.AddEntry(objs[g+dose+'_ByProd'],labels[dose],"PL")
#    leg.Draw()

    for ext in ['.pdf','.png']:
        c.SaveAs("LYIrradAnalysisMerged/"+g+"ByProd"+ext)

R.gStyle.SetOptFit(111111)
for ig,g in enumerate(['lyNormRelRescaled_AVG_ExpFitSlope']):
    a1[g]=R.TH2F("a1_"+g,"a1_"+g,10,0,10,10,a1_Y_Range[g][0],a1_Y_Range[g][1])
    a1[g].GetXaxis().SetTitle("Prod #")
    a1[g].GetYaxis().SetTitle(a1_Y_Title[g])
    a1[g].Draw()
    leg.Clear()

    objs[g+'_ByProd'].SetMarkerStyle(21)
    objs[g+'_ByProd'].SetMarkerColor(R.kBlack+id)
    objs[g+'_ByProd'].SetLineColor(R.kBlack+id)
    objs[g+'_ByProd'].SetMarkerSize(1.2)
    objs[g+'_ByProd'].Draw("PSAME")
    if (g == 'lyNormRelRescaled_AVG_ExpFitSlope' ):
        objs[g+'_ByProd'].Fit("pol0")
#    leg.AddEntry(objs[g+dose+'_ByProd'],labels[dose],"PL")
#    leg.Draw()
    
for ext in ['.pdf','.png']:
    c.SaveAs("LYIrradAnalysisMerged/"+g+"ByProd"+ext)


leg.Clear()
objs['lyNormAbs_Ratio_ByDose'].GetXaxis().SetTitle("Log_{10}(Dose) [Gy]")
objs['lyNormAbs_Ratio_ByDose'].GetYaxis().SetTitle("LY(PMT)/LY(TOFPET)")
objs['lyNormAbs_Ratio_ByDose'].GetYaxis().SetRangeUser(0.9,1.1)
objs['lyNormAbs_Ratio_ByDose'].Fit("pol0")
objs['lyNormAbs_Ratio_ByDose'].SetMarkerColor(R.kBlack)
objs['lyNormAbs_Ratio_ByDose'].SetLineColor(R.kBlack)
objs['lyNormAbs_Ratio_ByDose'].SetMarkerStyle(21)
objs['lyNormAbs_Ratio_ByDose'].SetMarkerSize(1.2)
objs['lyNormAbs_Ratio_ByDose'].Draw("P")
for ext in ['.pdf','.png']:
    c.SaveAs("LYIrradAnalysisMerged/lyNormAbsRatio_ByDose"+ext)

leg.Clear()
for ib,bench in enumerate(['PMT','TOFPET']):
    objs['lyNormAbs_'+bench+'_ByDose'].GetXaxis().SetTitle("Log_{10}(Dose) [Gy]")
    objs['lyNormAbs_'+bench+'_ByDose'].GetYaxis().SetTitle("LY/LY_{ref}")
    objs['lyNormAbs_'+bench+'_ByDose'].GetYaxis().SetRangeUser(0.8,1.1)
    objs['lyNormAbs_'+bench+'_ByDose'].SetMarkerColor(R.kBlack+ib)
    objs['lyNormAbs_'+bench+'_ByDose'].SetLineColor(R.kBlack+ib)
    objs['lyNormAbs_'+bench+'_ByDose'].SetMarkerStyle(21)
    objs['lyNormAbs_'+bench+'_ByDose'].SetMarkerSize(1.2)
    if (ib==0):
        objs['lyNormAbs_'+bench+'_ByDose'].Draw("P")
    else:
        objs['lyNormAbs_'+bench+'_ByDose'].Draw("PSAME")
    leg.AddEntry(objs['lyNormAbs_'+bench+'_ByDose'],bench,'PL')

leg.Draw()

for ext in ['.pdf','.png']:
    c.SaveAs("LYIrradAnalysisMerged/lyNormAbs_ByDose"+ext)




