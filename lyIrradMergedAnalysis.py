import pandas as pd
import ROOT as R
R.gROOT.SetBatch(1)

#,nmeas,dose,lyNormAbs,lyAbs,lyRel,dt,prod,type,lyNormRel
lyBenchData = pd.read_csv("LYIrradAnalysis/resultsByTag.csv",header=0,index_col=0,usecols=[0,2,3,4,5,6,7,8,9]) 

#nmeas,ctrRel,ctrNormAbs,ctrAbs,ctrNormRel,dose,lyNormAbs,lyAbs,lyRel,prod,type,lyNormRel
tofpetData = pd.read_csv("LYIrradAnalysisTOFPET/resultsByTag.csv",header=0,index_col=0,usecols=[0,2,3,4,5,7,8,9,12]) 

resultByTag = pd.concat([lyBenchData,tofpetData], axis=1, join='inner')
resultByTag.to_csv("LYIrradAnalysisMerged/lyAnalysisMerged.csv",header=False)

print(resultByTag.head())

crystalsData=R.TTree("crystalsData","crystalsData")
crystalsData.ReadFile("LYIrradAnalysisMerged/lyAnalysisMerged.csv","id/C:dose/F:lyNormAbsPMT/F:lyAbsPMT/F:lyRelPMT/F:dtAbsPMT/F:prod/C:type/C:lyNormRelPMT/F:ctrRelTOFPET/F:ctrNormAbsTOFPET/F:ctrAbsTOFPET/F:ctrNormRelTOFPET/F:lyNormAbsTOFPET/F:lyAbsTOFPET/F:lyRelTOFPET/F:lyNormRelTOFPET/F")

producers = [ 'prod'+str(i) for i in range(1,10) ]
histos = {}
data = {}
index={}

histos['lyNormAbs_Ratio']=R.TH1F('lyNormAbs_Ratio','lyNormAbs_Ratio',100,0.5,1.5)
histos['lyNormAbs_Ratio_ByDose']=R.TProfile('lyNormAbs_Ratio_ByDose','lyNormAbs_Ratio_ByDose',6,-1,5)
histos['lyNormRel_Ratio']=R.TH1F('lyNormRel_Ratio','lyNormRel_Ratio',100,0.5,1.5)
histos['lyNormRelRescaled_Ratio']=R.TH1F('lyNormRelRescaled_Ratio','lyNormRelRescaled_Ratio',100,0.5,1.5)
for bench in ['PMT','TOFPET','AVG']:
    histos['lyNormRel_'+bench]=R.TH1F('lyNormRel_'+bench,'lyNormRel_'+bench,100,0.5,1.5)
    histos['lyNormAbs_'+bench+'_ByDose']=R.TProfile('lyNormAbs_'+bench+'_ByDose','lyNormAbs_'+bench+'_ByDose',6,-1,5)

for g in ['lyNormAbs_TOFPETvsPMT','lyNormRel_TOFPETvsPMT','lyNormRelRescaled_TOFPETvsPMT','ctrAbsVsLYAbsOverDt']:
    histos[g]=R.TGraphErrors(crystalsData.GetEntries())
    histos[g].SetName(g)
    index[g]=0

histos['ctrAbsVsLYAbsOverDtProfile']=R.TProfile('ctrAbsVsLYAbsOverDtProfile','ctrAbsVsLYAbsOverDtProfile',40,0.02,0.03)

for prod in producers: 
    for bench in ['PMT','TOFPET','AVG']:
        histos['lyNormAbs_'+bench+'_'+prod]=R.TH1F('lyNormAbs_'+bench+'_'+prod,'lyNormAbs_'+bench+'_'+prod,100,0.5,1.5)
        histos['lyNormAbs_'+bench+'_IRR9K_'+prod]=R.TH1F('lyNormAbs_'+bench+'_IRR9K_'+prod,'lyNormAbs_'+bench+'_'+prod,100,0.5,1.5)
        histos['lyNormRelRescaled_'+bench+'_IRR9K_'+prod]=R.TH1F('lyNormRelRescaled_'+bench+'_IRR9K_'+prod,'lyNormRelRescaled_'+bench+'_IRR9K_'+prod,100,0.5,1.5)

    histos['lyNormAbs_Ratio_'+prod]=R.TH1F('lyNormAbs_Ratio_'+prod,'lyNormAbs_Ratio_xs'+prod,100,0.5,1.5)
    histos['lyNormAbs_Ratio_IRR9K_'+prod]=R.TH1F('lyNormAbs_Ratio_IRR9K_'+prod,'lyNormAbs_Ratio_IRR9K_'+prod,100,0.5,1.5)
    histos['dt_'+prod]=R.TH1F('dt_'+prod,'dt_'+prod,100,20.,50.)
    histos['dt_IRR9K_'+prod]=R.TH1F('dt_IRR9K_'+prod,'dt_IRR9K_'+prod,100,20.,50.)
    histos['ctr_'+prod]=R.TH1F('ctr_'+prod,'ctr_'+prod,100,50.,250.)
    histos['ctr_IRR9K_'+prod]=R.TH1F('ctr_IRR9K_'+prod,'ctr_IRR9K_'+prod,100,50.,250.)
    histos['lyNormAbsOverDt_'+prod]=R.TH1F('lyNormAbsOverDt_'+prod,'lyNormAbsOverDt_'+prod,100,0.02,0.03)
    histos['lyNormAbsOverDt_IRR9K_'+prod]=R.TH1F('lyNormAbsOverDt_IRR9K_'+prod,'lyNormAbsOverDt_IRR9K_'+prod,100,0.02,0.03)

    for bench in ['PMT','TOFPET','AVG']:
        histos['lyNormRel_'+bench+'_VsDose_'+prod]=R.TGraphErrors(10)#max size 10
        histos['lyNormRel_'+bench+'_VsDose_'+prod].SetName('lyNormRel_'+bench+'_VsDose_'+prod)
        index['lyNormRel_'+bench+'_VsDose_'+prod]=0
        histos['lyNormRelRescaled_'+bench+'_IRR9K_'+prod]=R.TH1F('lyNormRelRescaled_'+bench+'_IRR9K_'+prod,'lyNormRelRescaled_'+bench+'_IRR9K_'+prod,100,0.5,1.5)

    for g in ['ctrAbsVsLYAbsOverDt']:
        histos[g+'_'+prod]=R.TGraphErrors(crystalsData.GetEntries())
        histos[g+'_'+prod].SetName(g+'_'+prod)
        index[g+'_'+prod]=0

    data[prod] = []
        

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')

    #prod1 crystals are small
    lyNormAbsCorrTOFPET=crys.lyNormAbsTOFPET
    if (prod=='prod1'):
        lyNormAbsCorrTOFPET=crys.lyNormAbsTOFPET/1.06

    lyNormRel={'PMT':crys.lyNormRelPMT,'TOFPET':crys.lyNormRelTOFPET,'AVG':(crys.lyNormRelPMT+crys.lyNormRelTOFPET)/2.}
    lyNormAbs={'PMT':crys.lyNormAbsPMT/0.96,'TOFPET':lyNormAbsCorrTOFPET,'AVG':(crys.lyNormAbsPMT/0.96+lyNormAbsCorrTOFPET)/2.}

    #IRR0
    if (crys.dose==0):
        histos['lyNormAbs_Ratio_'+prod].Fill(lyNormAbs['PMT']/lyNormAbs['TOFPET'])
        histos['dt_'+prod].Fill(crys.dtAbsPMT)
        histos['ctr_'+prod].Fill(crys.ctrAbsTOFPET)
        for bench in ['PMT','TOFPET','AVG']: 
            histos['lyNormAbs_'+bench+'_'+prod].Fill(lyNormAbs[bench])
        histos['lyNormAbsOverDt_'+prod].Fill(lyNormAbs['AVG']/crys.dtAbsPMT)

    #high dose
    if (crys.dose>9E3):
        histos['lyNormAbs_Ratio_IRR9K_'+prod].Fill(lyNormAbs['PMT']/lyNormAbs['TOFPET'])
        histos['dt_IRR9K_'+prod].Fill(crys.dtAbsPMT)
        histos['ctr_IRR9K_'+prod].Fill(crys.ctrAbsTOFPET)
        for bench in ['PMT','TOFPET','AVG']: 
            histos['lyNormAbs_'+bench+'_IRR9K_'+prod].Fill(lyNormAbs[bench])
        histos['lyNormAbsOverDt_IRR9K_'+prod].Fill(lyNormAbs['AVG']/crys.dtAbsPMT)

    #Relative measurements
    if (not 'IRR0' in crys.id):#skip point 0 for Rel measurements
        histos['lyNormRel_Ratio'].Fill(crys.lyNormRelPMT/crys.lyNormRelTOFPET)

        histos['lyNormRel_TOFPETvsPMT'].SetPoint(index['lyNormRel_TOFPETvsPMT'],crys.lyNormRelPMT,crys.lyNormRelTOFPET)
        histos['lyNormRel_TOFPETvsPMT'].SetPointError(index['lyNormRel_TOFPETvsPMT'],0.05,0.05)
        index['lyNormRel_TOFPETvsPMT']=index['lyNormRel_TOFPETvsPMT']+1

        for bench in ['PMT','TOFPET','AVG']: #beware not doing the average here if >1 crystal at same dose
            histos['lyNormRel_'+bench].Fill(lyNormRel[bench])
            histos['lyNormRel_'+bench+'_VsDose_'+prod].SetPoint(index['lyNormRel_'+bench+'_VsDose_'+prod],crys.dose,lyNormRel[bench])
            histos['lyNormRel_'+bench+'_VsDose_'+prod].SetPointError(index['lyNormRel_'+bench+'_VsDose_'+prod],0.,0.05)
            index['lyNormRel_'+bench+'_VsDose_'+prod]=index['lyNormRel_'+bench+'_VsDose_'+prod]+1

    #fill for all measurements
    histos['ctrAbsVsLYAbsOverDt'].SetPoint(index['ctrAbsVsLYAbsOverDt'],crys.lyNormAbsTOFPET/crys.dtAbsPMT,crys.ctrAbsTOFPET)
    histos['ctrAbsVsLYAbsOverDt'].SetPointError(index['ctrAbsVsLYAbsOverDt'],(crys.lyNormAbsTOFPET/crys.dtAbsPMT)*0.05,5)
    index['ctrAbsVsLYAbsOverDt']=index['ctrAbsVsLYAbsOverDt']+1
    histos['ctrAbsVsLYAbsOverDtProfile'].Fill(crys.lyNormAbsTOFPET/crys.dtAbsPMT,crys.ctrAbsTOFPET)

    histos['ctrAbsVsLYAbsOverDt_'+prod].SetPoint(index['ctrAbsVsLYAbsOverDt_'+prod],crys.lyNormAbsTOFPET/crys.dtAbsPMT,crys.ctrAbsTOFPET) #non corrected for correlation
    histos['ctrAbsVsLYAbsOverDt_'+prod].SetPointError(index['ctrAbsVsLYAbsOverDt_'+prod],(crys.lyNormAbsTOFPET/crys.dtAbsPMT)*0.05,5)
    index['ctrAbsVsLYAbsOverDt_'+prod]=index['ctrAbsVsLYAbsOverDt_'+prod]+1

    histos['lyNormAbs_TOFPETvsPMT'].SetPoint(index['lyNormAbs_TOFPETvsPMT'],lyNormAbs['PMT'],lyNormAbs['TOFPET'])
    histos['lyNormAbs_TOFPETvsPMT'].SetPointError(index['lyNormAbs_TOFPETvsPMT'],0.05,0.05)
    index['lyNormAbs_TOFPETvsPMT']=index['lyNormAbs_TOFPETvsPMT']+1

    histos['lyNormAbs_Ratio'].Fill(lyNormAbs['PMT']/lyNormAbs['TOFPET'])
    histos['lyNormAbs_Ratio_ByDose'].Fill(R.TMath.Log10(crys.dose+0.1),lyNormAbs['PMT']/lyNormAbs['TOFPET'])
    for bench in ['PMT','TOFPET','AVG']: 
        histos['lyNormAbs_'+bench+'_ByDose'].Fill(R.TMath.Log10(crys.dose+0.1),lyNormAbs[bench])

#resize histograms to their actual size
for n,h in histos.items():
    if ('TGraph' in str(type(h))):
        h.Set(index[n])

for g in ['dt','dt_IRR9K','ctr','ctr_IRR9K','lyNormAbs_TOFPET','lyNormAbs_TOFPET_IRR9K','lyNormAbs_PMT','lyNormAbs_PMT_IRR9K','lyNormAbs_AVG','lyNormAbs_AVG_IRR9K','lyNormAbsOverDt','lyNormAbsOverDt_IRR9K','lyNormRelRescaled_PMT_IRR9K','lyNormRelRescaled_TOFPET_IRR9K','lyNormRelRescaled_AVG_IRR9K','lyNormAbs_Ratio','lyNormAbs_Ratio_IRR9K']:        
    histos[g+'_ByProd']=R.TGraphErrors(len(producers))
    histos[g+'_ByProd'].SetName(g+'_ByProd')

for iprod,prod in enumerate(producers):

    for bench in ['PMT','TOFPET','AVG']:
        histos['lyNormRel_'+bench+'_VsDose_'+prod].Fit("expo")
        histos['lyNormRel_'+bench+'_RescaledVsDose_'+prod]=R.TGraphErrors(histos['lyNormRel_'+bench+'_VsDose_'+prod].GetN())
        histos['lyNormRel_'+bench+'_RescaledVsDose_'+prod].SetName('lyNormRel_'+bench+'_RescaledVsDose_'+prod)
        for ip in range(0,histos['lyNormRel_'+bench+'_VsDose_'+prod].GetN()):
            x,y=R.Double(0.),R.Double(0.)
            histos['lyNormRel_'+bench+'_VsDose_'+prod].GetPoint(ip,x,y)
            histos['lyNormRel_'+bench+'_RescaledVsDose_'+prod].SetPoint(ip,x,y/histos['lyNormRel_'+bench+'_VsDose_'+prod].GetFunction("expo").Eval(0))
            histos['lyNormRel_'+bench+'_RescaledVsDose_'+prod].SetPointError(ip,0,0.05)

    for ip in range(0,histos['lyNormRel_PMT_RescaledVsDose_'+prod].GetN()):
        xPMT,yPMT,xTOFPET,yTOFPET,xAVG,yAVG=R.Double(0.),R.Double(0.),R.Double(0.),R.Double(0.),R.Double(0.),R.Double(0.)
        histos['lyNormRel_PMT_RescaledVsDose_'+prod].GetPoint(ip,xPMT,yPMT)
        histos['lyNormRel_TOFPET_RescaledVsDose_'+prod].GetPoint(ip,xTOFPET,yTOFPET)
        histos['lyNormRel_AVG_RescaledVsDose_'+prod].GetPoint(ip,xAVG,yAVG)

        if (xPMT != xTOFPET or xPMT != xAVG):
            print("Hey???")
            continue

        histos['lyNormRelRescaled_TOFPETvsPMT'].SetPoint(index['lyNormRelRescaled_TOFPETvsPMT'],yPMT,yTOFPET)
        histos['lyNormRelRescaled_TOFPETvsPMT'].SetPointError(index['lyNormRelRescaled_TOFPETvsPMT'],0.04,0.04)
        index['lyNormRelRescaled_TOFPETvsPMT']=index['lyNormRelRescaled_TOFPETvsPMT']+1
        histos['lyNormRelRescaled_Ratio'].Fill(yPMT/yTOFPET)

        if (xPMT>9000):
            histos['lyNormRelRescaled_PMT_IRR9K_'+prod].Fill(yPMT)
            histos['lyNormRelRescaled_TOFPET_IRR9K_'+prod].Fill(yTOFPET)
            histos['lyNormRelRescaled_AVG_IRR9K_'+prod].Fill(yAVG)

    for g in ['dt','dt_IRR9K','ctr','ctr_IRR9K','lyNormAbs_TOFPET','lyNormAbs_TOFPET_IRR9K','lyNormAbs_PMT','lyNormAbs_PMT_IRR9K','lyNormAbs_AVG','lyNormAbs_AVG_IRR9K','lyNormAbsOverDt','lyNormAbsOverDt_IRR9K','lyNormRelRescaled_TOFPET_IRR9K','lyNormRelRescaled_PMT_IRR9K','lyNormRelRescaled_AVG_IRR9K','lyNormAbs_Ratio','lyNormAbs_Ratio_IRR9K']:        
        histos[g+'_ByProd'].SetPoint(iprod,iprod+1,histos[g+'_'+prod].GetMean())
        if ('IRR9K' in g):
            if ('dt' in g):
                histos[g+'_ByProd'].SetPointError(iprod,0,0.3)
            elif ('ctr' in g):
                histos[g+'_ByProd'].SetPointError(iprod,0,5)
            elif ('lyNormAbsOverDt' in g):
                histos[g+'_ByProd'].SetPointError(iprod,0,0.001)
            elif ('ly' in g):
                histos[g+'_ByProd'].SetPointError(iprod,0,0.05)
                if ('AVG' in g):
                    histos[g+'_ByProd'].SetPointError(iprod,0,0.035)
        else:
            histos[g+'_ByProd'].SetPointError(iprod,0,histos[g+'_'+prod].GetRMS())

histos['lyNormRelRescaled_TOFPETvsPMT'].Set(index['lyNormRelRescaled_TOFPETvsPMT'])

out=R.TFile("LYIrradAnalysisMerged/LYMergedPlots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
print("Data wrote to LYIrradAnalysisMerged/LYMergedPlots.root")
out.Write()
out.Close()

