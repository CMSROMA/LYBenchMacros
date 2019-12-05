import pandas as pd
import ROOT as R
R.gROOT.SetBatch(1)

lyBenchData = pd.read_csv("LYIrradAnalysis/resultsByTag.csv",header=0,index_col=0,usecols=range(0,7)) 
tofpetData = pd.read_csv("LYIrradAnalysisTOFPET/resultsByTag.csv",header=0,index_col=0,usecols=[0,3,5,6,8]) 
resultByTag = pd.concat([lyBenchData,tofpetData], axis=1, join='inner')
resultByTag.to_csv("LYIrradAnalysisMerged/lyAnalysisMerged.csv",header=False)

crystalsData=R.TTree("crystalsData","crystalsData")
crystalsData.ReadFile("LYIrradAnalysisMerged/lyAnalysisMerged.csv","id/C:lyNormRelPMT/F:dose/F:lyRelPMT/F:dtAbsPMT/F:prod/C:type/C:ctrAbsTOFPET/F:lyAbsTOFPET/F:lyRelTOFPET/F:ctrRelTOFPET/F")

producers = [ 'prod'+str(i) for i in range(1,10) ]
histos = {}
data = {}
index={}

histos['lyRel_Ratio']=R.TH1F('lyRel_Ratio','lyRel_Ratio',100,0.5,1.5)
histos['lyRelRescaled_Ratio']=R.TH1F('lyRelRescaled_Ratio','lyRelRescaled_Ratio',100,0.5,1.5)
histos['lyRel_PMT']=R.TH1F('lyRel_PMT','lyRel_PMT',100,0.5,1.5)
histos['lyRel_TOFPET']=R.TH1F('lyRel_TOFPET','lyRel_TOFPET',100,0.5,1.5)

for g in ['lyRel_TOFPETvsPMT','lyRelRescaled_TOFPETvsPMT','ctrAbsVsLYAbsOverDt']:
    histos[g]=R.TGraphErrors(crystalsData.GetEntries())
    histos[g].SetName(g)
    index[g]=0

histos['ctrAbsVsLYAbsOverDtProfile']=R.TProfile('ctrAbsVsLYAbsOverDtProfile','ctrAbsVsLYAbsOverDtProfile',40,0.02,0.03)


for prod in producers: 
    histos['lyRel_PMT_IRR9K_'+prod]=R.TH1F('lyRel_PMT_IRR9K_'+prod,'lyRel_PMT_IRR9K_'+prod,100,0.5,1.5)
    histos['lyRel_TOFPET_IRR9K_'+prod]=R.TH1F('lyRel_TOFPET_IRR9K_'+prod,'lyRel_TOFPET_IRR9K_'+prod,100,0.5,1.5)
    histos['lyAbs_TOFPET_'+prod]=R.TH1F('lyAbs_TOFPET_'+prod,'lyAbs_TOFPET_'+prod,200,0.,100.)
    histos['lyAbs_TOFPET_IRR9K_'+prod]=R.TH1F('lyAbs_TOFPET_IRR9K_'+prod,'lyAbs_TOFPET_'+prod,200,0.,100.)
    histos['dt_'+prod]=R.TH1F('dt_'+prod,'dt_'+prod,100,20.,50.)
    histos['dt_IRR9K_'+prod]=R.TH1F('dt_IRR9K_'+prod,'dt_IRR9K_'+prod,100,20.,50.)
    histos['ctr_'+prod]=R.TH1F('ctr_'+prod,'ctr_'+prod,100,50.,250.)
    histos['ctr_IRR9K_'+prod]=R.TH1F('ctr_IRR9K_'+prod,'ctr_IRR9K_'+prod,100,50.,250.)
    histos['lyAbsOverDt_'+prod]=R.TH1F('lyAbsOverDt_'+prod,'lyAbsOverDt_'+prod,100,0.02,0.03)
    histos['lyAbsOverDt_IRR9K_'+prod]=R.TH1F('lyAbsOverDt_IRR9K_'+prod,'lyAbsOverDt_IRR9K_'+prod,100,0.02,0.03)
    histos['lyRel_PMT_VsDose_'+prod]=R.TGraphErrors(10)#max size 10
    histos['lyRel_PMT_VsDose_'+prod].SetName('lyRel_PMT_VsDose_'+prod)
    index['lyRel_PMT_VsDose_'+prod]=0
    histos['lyRel_TOFPET_VsDose_'+prod]=R.TGraphErrors(10)#max size 10
    histos['lyRel_TOFPET_VsDose_'+prod].SetName('lyRel_TOFPET_VsDose_'+prod)
    index['lyRel_TOFPET_VsDose_'+prod]=0
    data[prod] = []
        

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')

    #prod1 crystals are small
    lyAbsCorrTOFPET=crys.lyAbsTOFPET
    if (prod=='prod1'):
        lyAbsCorrTOFPET=crys.lyAbsTOFPET/1.06*1.03

    #IRR0
    if (crys.dose==0):
        histos['dt_'+prod].Fill(crys.dtAbsPMT)
        histos['ctr_'+prod].Fill(crys.ctrAbsTOFPET)
        histos['lyAbs_TOFPET_'+prod].Fill(lyAbsCorrTOFPET)
        histos['lyAbsOverDt_'+prod].Fill(crys.lyAbsTOFPET/crys.dtAbsPMT)

    #high dose
    if (crys.dose>9000):
        histos['dt_IRR9K_'+prod].Fill(crys.dtAbsPMT)
        histos['ctr_IRR9K_'+prod].Fill(crys.ctrAbsTOFPET)
        histos['lyAbs_TOFPET_IRR9K_'+prod].Fill(lyAbsCorrTOFPET)
        histos['lyAbsOverDt_IRR9K_'+prod].Fill(crys.lyAbsTOFPET/crys.dtAbsPMT)

    #Relative measurements
    if (not 'IRR0' in crys.id):#skip point 0 for Rel measurements
        histos['lyRel_Ratio'].Fill(crys.lyRelPMT/crys.lyRelTOFPET)

        histos['lyRel_TOFPETvsPMT'].SetPoint(index['lyRel_TOFPETvsPMT'],crys.lyRelPMT,crys.lyRelTOFPET)
        histos['lyRel_TOFPETvsPMT'].SetPointError(index['lyRel_TOFPETvsPMT'],0.05,0.05)
        index['lyRel_TOFPETvsPMT']=index['lyRel_TOFPETvsPMT']+1

        lyRel={'PMT':crys.lyRelPMT,'TOFPET':crys.lyRelTOFPET}
        for bench in ['PMT','TOFPET']:
            histos['lyRel_'+bench].Fill(lyRel[bench])
            histos['lyRel_'+bench+'_VsDose_'+prod].SetPoint(index['lyRel_'+bench+'_VsDose_'+prod],crys.dose,lyRel[bench])
            histos['lyRel_'+bench+'_VsDose_'+prod].SetPointError(index['lyRel_'+bench+'_VsDose_'+prod],0.,0.05)
            index['lyRel_'+bench+'_VsDose_'+prod]=index['lyRel_'+bench+'_VsDose_'+prod]+1

    #fill for all measurements
    histos['ctrAbsVsLYAbsOverDt'].SetPoint(index['ctrAbsVsLYAbsOverDt'],crys.lyAbsTOFPET/crys.dtAbsPMT,crys.ctrAbsTOFPET)
    histos['ctrAbsVsLYAbsOverDt'].SetPointError(index['ctrAbsVsLYAbsOverDt'],(crys.lyAbsTOFPET/crys.dtAbsPMT)*0.05,5)
    index['ctrAbsVsLYYAbsOverDt']=index['ctrAbsVsLYAbsOverDt']+1
    histos['ctrAbsVsLYAbsOverDtProfile'].Fill(crys.lyAbsTOFPET/crys.dtAbsPMT,crys.ctrAbsTOFPET)

#resize histograms to their actual size
for n,h in histos.items():
    if ('TGraph' in str(type(h))):
        h.Set(index[n])

for g in ['dt','dt_IRR9K','ctr','ctr_IRR9K','lyAbs_TOFPET','lyAbs_TOFPET_IRR9K','lyAbsOverDt','lyAbsOverDt_IRR9K']:        
    histos[g+'_ByProd']=R.TGraphErrors(len(producers))
    histos[g+'_ByProd'].SetName(g+'_ByProd')

for iprod,prod in enumerate(producers):
    for g in ['dt','dt_IRR9K','ctr','ctr_IRR9K','lyAbs_TOFPET','lyAbs_TOFPET_IRR9K','lyAbsOverDt','lyAbsOverDt_IRR9K']:        
        histos[g+'_ByProd'].SetPoint(iprod,iprod+1,histos[g+'_'+prod].GetMean())
        histos[g+'_ByProd'].SetPointError(iprod,0,histos[g+'_'+prod].GetRMS())
    for bench in ['PMT','TOFPET']:
        histos['lyRel_'+bench+'_VsDose_'+prod].Fit("expo")
        histos['lyRel_'+bench+'_RescaledVsDose_'+prod]=R.TGraphErrors(histos['lyRel_'+bench+'_VsDose_'+prod].GetN())
        histos['lyRel_'+bench+'_RescaledVsDose_'+prod].SetName('lyRel_'+bench+'_RescaledVsDose_'+prod)
        for ip in range(0,histos['lyRel_'+bench+'_VsDose_'+prod].GetN()):
            x,y=R.Double(0.),R.Double(0.)
            histos['lyRel_'+bench+'_VsDose_'+prod].GetPoint(ip,x,y)
            histos['lyRel_'+bench+'_RescaledVsDose_'+prod].SetPoint(ip,x,y/histos['lyRel_'+bench+'_VsDose_'+prod].GetFunction("expo").Eval(0))
            histos['lyRel_'+bench+'_RescaledVsDose_'+prod].SetPointError(ip,0,0.05)
    for ip in range(0,histos['lyRel_PMT_RescaledVsDose_'+prod].GetN()):
        xPMT,yPMT,xTOFPET,yTOFPET=R.Double(0.),R.Double(0.),R.Double(0.),R.Double(0.)
        histos['lyRel_PMT_RescaledVsDose_'+prod].GetPoint(ip,xPMT,yPMT)
        histos['lyRel_TOFPET_RescaledVsDose_'+prod].GetPoint(ip,xTOFPET,yTOFPET)
        if (xPMT != xTOFPET):
            print "Hey???"
            continue
        histos['lyRelRescaled_TOFPETvsPMT'].SetPoint(index['lyRelRescaled_TOFPETvsPMT'],yPMT,yTOFPET)
        histos['lyRelRescaled_TOFPETvsPMT'].SetPointError(index['lyRelRescaled_TOFPETvsPMT'],0.04,0.04)
        index['lyRelRescaled_TOFPETvsPMT']=index['lyRelRescaled_TOFPETvsPMT']+1
        histos['lyRelRescaled_Ratio'].Fill(yPMT/yTOFPET)

histos['lyRelRescaled_TOFPETvsPMT'].Set(index['lyRelRescaled_TOFPETvsPMT'])

out=R.TFile("LYIrradAnalysisMerged/LYMergedPlots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()

