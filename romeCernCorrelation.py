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

R.gROOT.SetBatch(1)

f1=R.TFile("LYIrradAnalysisMerged/LYMergedPlots.root")
f2=R.TFile("compareRome.root")

objsRome=Map(f1)
objsCERN=Map(f2)

nprod=8
objs={}
objsCompare={}

objs['dt']=R.TGraphErrors(nprod)
objs['dt'].SetName('dt')

objsCompare['dt_ByProd_CERN']=objsCERN['gDT_TCSPC_vendors'].Clone('dt_ByProd_CERN')
objsCompare['dt_ByProd_ROME']=objsRome['dt_ByProd'].Clone('dt_ByProd_ROME')

for ip in range(0,nprod):
    xC,yC,xR,yR=R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gDT_TCSPC_vendors'].GetPoint(ip,xC,yC)
    objsCompare['dt_ByProd_CERN'].SetPointError(ip,0,0.3)
    objsRome['dt_ByProd'].GetPoint(ip,xR,yR)

#    if (xC != xR):
#        print 'Hey DT!!'+' '+str(yC)+' '+str(xR)
    objs['dt'].SetPoint(ip,yC+2.5,yR)
    objs['dt'].SetPointError(ip,0.3,objsRome['dt_ByProd'].GetErrorY(ip))

objs['lyPMT']=R.TGraphErrors(nprod)
objs['lyPMT'].SetName('lyPMT')

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gLY_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLY_vendors'].GetPoint(0,xCRef,yCRef)
    objsRome['lyNormAbs_PMT_ByProd'].GetPoint(ip,xR,yR)
    if (xC != xR):
        print 'Hey!!'
    objs['lyPMT'].SetPoint(ip,yC/yCRef,yR)
    objs['lyPMT'].SetPointError(ip,0.03,objsRome['lyNormAbs_PMT_ByProd'].GetErrorY(ip))

objs['lyS']=R.TGraphErrors(nprod)
objs['lyS'].SetName('lyS')

objsCompare['lyS_ByProd_CERN']=objsCERN['gLOS_vendors'].Clone('lyS_ByProd_CERN')
objsCompare['lyS_ByProd_ROME']=objsRome['lyNormAbs_TOFPET_ByProd'].Clone('lyS_ByProd_ROME')

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gLOS_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLOS_vendors'].GetPoint(0,xCRef,yCRef)
    objsRome['lyNormAbs_TOFPET_ByProd'].GetPoint(ip,xR,yR)
    if (xC != xR):
        print 'Hey!!'

    objs['lyS'].SetPoint(ip,yC/yCRef,yR)
    objs['lyS'].SetPointError(ip,0.03,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip))

    objsCompare['lyS_ByProd_CERN'].SetPoint(ip,xC,yC/yCRef)
    objsCompare['lyS_ByProd_CERN'].SetPointError(ip,0,0.03)

objs['lyCERNSVsP']=R.TGraphErrors(nprod)
objs['lyCERNSVsP'].SetName('lyCERNSVsP')

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xP,yP,xPRef,yPRef=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gLOS_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLOS_vendors'].GetPoint(0,xCRef,yCRef)
    objsCERN['gLY_vendors'].GetPoint(ip,xP,yP)
    objsCERN['gLY_vendors'].GetPoint(0,xPRef,yPRef)
    if (xC != xP):
        print 'Hey!!'
    objs['lyCERNSVsP'].SetPoint(ip,yC/yCRef,yP/yPRef)
    objs['lyCERNSVsP'].SetPointError(ip,0.03,0.03)

objs['lyRomeSVsP']=R.TGraphErrors(nprod+1)
objs['lyRomeSVsP'].SetName('lyRomeSVsP')


for ip in range(0,nprod+1):
    xC,yC,xP,yP=R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsRome['lyNormAbs_TOFPET_ByProd'].GetPoint(ip,xC,yC)
    objsRome['lyNormAbs_PMT_ByProd'].GetPoint(ip,xP,yP)
    if (xC != xP):
        print 'Hey!!'
    objs['lyRomeSVsP'].SetPoint(ip,yC,yP)
    objs['lyRomeSVsP'].SetPointError(ip,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip),objsRome['lyNormAbs_PMT_ByProd'].GetErrorY(ip))

objs['lySOverDt']=R.TGraphErrors(nprod)
objs['lySOverDt'].SetName('lySOverDt')
objs['lySOverDt'].SetTitle('lySOverDt')

objsCompare['lySOverDt_ByProd_CERN']=objsCERN['gTR_ave_vendors'].Clone('lySOverDt_ByProd_CERN')
objsCompare['lySOverDt_ByProd_ROME']=objsRome['ctr_ByProd'].Clone('lySOverDt_ByProd_ROME')

for ip in range(0,nprod+1): #we need also to fill producer 9 for Rome
    xCRef,yCRef,xC,yC,xR,yR,xD,yD,xDR,yDR,xR_D,yR_D,xR_DR,yR_DR=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)

    objsRome['lyNormAbs_TOFPET_ByProd'].GetPoint(ip,xR,yR)
    objsRome['dt_ByProd'].GetPoint(ip,xR_D,yR_D)
    objsRome['dt_ByProd'].GetPoint(0,xR_DR,yR_DR)

    objsCompare['lySOverDt_ByProd_ROME'].SetPoint(ip,xR,yR/(yR_D/yR_DR))
    objsCompare['lySOverDt_ByProd_ROME'].SetPointError(ip,0,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip))

    if (ip>=nprod): #only 8 producers for CERN for the moment
        continue

    objsCERN['gLOS_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLOS_vendors'].GetPoint(0,xCRef,yCRef)
    objsCERN['gDT_TCSPC_vendors'].GetPoint(ip,xD,yD)
    objsCERN['gDT_TCSPC_vendors'].GetPoint(0,xDR,yDR)

    if (xC != xR or xC != xR_D ):
        print 'Hey!!'
#    if (xCRef != xDR or xCRef !=xR_DR):
#        print 'Hey!!'

    objsCompare['lySOverDt_ByProd_CERN'].SetPoint(ip,xC,(yC/yCRef)/((yD+2.5)/(yDR+2.5)))
    objsCompare['lySOverDt_ByProd_CERN'].SetPointError(ip,0,0.03)

    objs['lySOverDt'].SetPoint(ip,(yC/yCRef)/(yD/yDR),yR/(yR_D/yR_DR))
    objs['lySOverDt'].SetPointError(ip,0.03,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip))


objs['ctrVSlySOverDtRome']=R.TGraphErrors(nprod+1)
objs['ctrVSlySOverDtRome'].SetName('ctrVSlySOverDtRome')
objs['ctrVSlySOverDtRome'].SetTitle('ctrVSlySOverDtRome')

for ip in range(0,nprod+1): #we need also to fill producer 9 for Rome
    xR,yR,xR_D,yR_D,xR_DR,yR_DR,xRT,yRT=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)

    objsRome['lyNormAbs_TOFPET_ByProd'].GetPoint(ip,xR,yR)
    objsRome['dt_ByProd'].GetPoint(ip,xR_D,yR_D)
    objsRome['dt_ByProd'].GetPoint(0,xR_DR,yR_DR)
    objsRome['ctr_ByProd'].GetPoint(ip,xRT,yRT)

    objs['ctrVSlySOverDtRome'].SetPoint(ip,yR/(yR_D/yR_DR),yRT)
    objs['ctrVSlySOverDtRome'].SetPointError(ip,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip),objsRome['ctr_ByProd'].GetErrorY(ip))

objs['ctrVSlySOverDtCERN']=R.TGraphErrors(nprod)
objs['ctrVSlySOverDtCERN'].SetName('ctrVSlySOverDtCERN')
objs['ctrVSlySOverDtCERN'].SetTitle('ctrVSlySOverDtCERN')

for ip in range(0,nprod): #we need also to fill producer 9 for CERN
    xCRef,yCRef,xC,yC,xD,yD,xDR,yDR,xCT,yCT=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)

    objsCERN['gLOS_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLOS_vendors'].GetPoint(0,xCRef,yCRef)
    objsCERN['gDT_TCSPC_vendors'].GetPoint(ip,xD,yD)
    objsCERN['gDT_TCSPC_vendors'].GetPoint(0,xDR,yDR)
    objsCERN['gTR_ave_vendors'].GetPoint(ip,xCT,yCT)

#    if (xC !=xD or xC != xCT):
#        print 'Hey!!'
#        continue

    objs['ctrVSlySOverDtCERN'].SetPoint(ip,(yC/yCRef)/((yD+2.5)/(yDR+2.5)),yCT*1000)
    objs['ctrVSlySOverDtCERN'].SetPointError(ip,0.03,3)

objs['lyPOverDt']=R.TGraphErrors(nprod)
objs['lyPOverDt'].SetName('lyPOverDt')
objs['lyPOverDt'].SetTitle('lyPOverDt')

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR,xD,yD,xDR,yDR,xR_D,yR_D,xR_DR,yR_DR=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)

    objsCERN['gLY_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLY_vendors'].GetPoint(0,xCRef,yCRef)
    objsCERN['gDT_TCSPC_vendors'].GetPoint(ip,xD,yD)
    objsCERN['gDT_TCSPC_vendors'].GetPoint(0,xDR,yDR)

    objsRome['lyNormAbs_PMT_ByProd'].GetPoint(ip,xR,yR)
    objsRome['dt_ByProd'].GetPoint(ip,xR_D,yR_D)
    objsRome['dt_ByProd'].GetPoint(0,xR_DR,yR_DR)
#    if (xC != xR or xC !=xD or xC != xR_D ):
#        print 'Hey!!'
#    if (xCRef != xDR or xCRef !=xR_DR):
#        print 'Hey!!'

    objs['lyPOverDt'].SetPoint(ip,(yC/yCRef)/(yD+2.5)/(yDR+2.5),yR/(yR_D/yR_DR))
    objs['lyPOverDt'].SetPointError(ip,0.03,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip))


objs['ctr']=R.TGraphErrors(nprod)
objs['ctr'].SetName('ctr')

objsCompare['ctr_ByProd_CERN']=objsCERN['gTR_ave_vendors'].Clone('ctr_ByProd_CERN')
objsCompare['ctr_ByProd_ROME']=objsRome['ctr_ByProd'].Clone('ctr_ByProd_ROME')

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR,xRRef,yRRef=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gTR_ave_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gTR_ave_vendors'].GetPoint(0,xCRef,yCRef)
    objsCompare['ctr_ByProd_CERN'].SetPoint(ip,xC,yC*1000)
    objsCompare['ctr_ByProd_CERN'].SetPointError(ip,0,3)

    objsRome['ctr_ByProd'].GetPoint(ip,xR,yR)
    objsRome['ctr_ByProd'].GetPoint(0,xRRef,yRRef)
    if (xC != xR):
        print 'Hey!!'
    objs['ctr'].SetPoint(ip,yC/yCRef,yR/yRRef)
    objs['ctr'].SetPointError(ip,3/(yCRef*1000),objsRome['ctr_ByProd'].GetErrorY(ip)/yRRef)

out=R.TFile("romeCernCorrelation.root","RECREATE")
for h,histo in objs.items():
    histo.Write()
for h,histo in objsCompare.items():
    histo.Write()
out.Write()
out.Close()

R.gStyle.SetOptTitle(0)
c1=R.TCanvas("c1","c1",900,600)

labels = {
    'dt': { 'X':'#tau_{CERN} [ns]', 'Y':'#tau_{ROME} [ns]' },
    'lyPMT': { 'X':'LY_{PMT} ^{CERN}', 'Y':'LY_{PMT} ^{ROME}' },
    'lyS': { 'X':'LY_{SiPM} ^{CERN}', 'Y':'LY_{SiPM} ^{ROME}' },
    'lyCERNSVsP': { 'X':'LY_{SiPM} ^{CERN}', 'Y':'LY_{PMT} ^{CERN}' },
    'lyRomeSVsP': { 'X':'LY_{SiPM} ^{ROME}', 'Y':'LY_{PMT} ^{ROME}' },
    'lySOverDt': { 'X':'LY_{SiPM}/#tau ^{CERN}', 'Y':'LY_{SiPM}/#tau ^{ROME}' },
    'lyPOverDt': { 'X':'LY_{PMT}/#tau ^{CERN}', 'Y':'LY_{PMT}/#tau ^{ROME}' },
    'ctr': { 'X':'#sigma_{t}^{CERN}', 'Y':'#sigma_{t} ^{ROME}' },
    'ctr_ByProd': { 'X':'Vendor ID', 'Y':'#sigma_{t} [ps]' },
    'ctrVSlySOverDtRome': { 'X':'LY_{SiPM}/#tau ^{ROME}', 'Y':'#sigma_{t}^{ROME} [ps]' },
    'ctrVSlySOverDtCERN': { 'X':'LY_{SiPM}/#tau ^{CERN}', 'Y':'#sigma_{t}^{CERN} [ps]' },
    'dt_ByProd': { 'X':'Vendor ID', 'Y':'#tau [ns]' },
    'lySOverDt_ByProd': { 'X':'Vendor ID', 'Y':'LY_{SiPM}/#tau' },
    'lyS_ByProd': { 'X':'Vendor ID', 'Y':'LY_{SiPM}' },
}

ranges = {
    'dt': { 'X' : [35,50] , 'Y' : [35,50] },
    'lyPMT': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyS': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyCERNSVsP': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyRomeSVsP': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lySOverDt': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyPOverDt': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'ctr': { 'X' : [0.85,1.3] , 'Y' : [0.8,2.0] },
    'ctr_ByProd': { 'X' : [0,10] , 'Y' : [60,200] },
    'ctrVSlySOverDtRome':{ 'X' : [0.7,1.3] , 'Y' : [70,200] },
    'ctrVSlySOverDtCERN':{ 'X' : [0.7,1.3] , 'Y' : [70,120] },
    'dt_ByProd': { 'X': [0,10], 'Y': [35,50] },
    'lySOverDt_ByProd': { 'X': [0.,10], 'Y': [0.7,1.3] },
    'lyS_ByProd': { 'X': [0.,10.], 'Y': [0.7,1.3] },
}


fX = R.TF1("fX","x",0,1000)

text=R.TLatex()
text.SetTextSize(0.04)

for k,g in objs.items():

    g.Print()
    g.SetMarkerColor(R.kBlue)
    g.SetMarkerStyle(21)
    g.SetMarkerSize(0.8)

    g.GetXaxis().SetTitle(labels[k]['X'])
    g.GetXaxis().SetLimits(ranges[k]['X'][0],ranges[k]['X'][1])
    g.GetXaxis().SetRangeUser(ranges[k]['X'][0],ranges[k]['X'][1])

    g.GetYaxis().SetTitle(labels[k]['Y'])
    g.GetYaxis().SetLimits(ranges[k]['Y'][0],ranges[k]['Y'][1])
    g.GetYaxis().SetRangeUser(ranges[k]['Y'][0],ranges[k]['Y'][1])

    g.Draw("AP")
    if (not 'ctr' in k):
        fX.Draw('SAME')
    elif (not 'VSly'):
        g.Fit("pol1")

    for ext in ['.png','.pdf']:
        c1.SaveAs("RomeVsCERN/"+k+ext)

leg=R.TLegend(0.77,0.73,0.89,0.89)
leg.SetBorderSize(0)
leg.SetFillColorAlpha(0,0)
leg.SetTextSize(0.04)

for k in ['dt_ByProd', 'ctr_ByProd', 'lyS_ByProd', 'lySOverDt_ByProd' ]:
    leg.Clear()
    for ib,b in enumerate(['CERN','ROME']):
        objsCompare[k+'_'+b].SetMarkerColor(R.kBlack+ib)
        objsCompare[k+'_'+b].SetMarkerStyle(21)
        objsCompare[k+'_'+b].SetMarkerSize(0.8)
        
        objsCompare[k+'_'+b].GetXaxis().SetTitle(labels[k]['X'])
        objsCompare[k+'_'+b].GetXaxis().SetLimits(ranges[k]['X'][0],ranges[k]['X'][1])
        objsCompare[k+'_'+b].GetXaxis().SetRangeUser(ranges[k]['X'][0],ranges[k]['X'][1])
        
        objsCompare[k+'_'+b].GetYaxis().SetTitle(labels[k]['Y'])
        objsCompare[k+'_'+b].GetYaxis().SetLimits(ranges[k]['Y'][0],ranges[k]['Y'][1])
        objsCompare[k+'_'+b].GetYaxis().SetRangeUser(ranges[k]['Y'][0],ranges[k]['Y'][1])

        leg.AddEntry(objsCompare[k+'_'+b],b,"PL")

        if (ib==0):
            objsCompare[k+'_'+b].Draw("AP")
        else:
            objsCompare[k+'_'+b].Draw("PSAME")

    leg.Draw()
    for ext in ['.png','.pdf']:
        c1.SaveAs("RomeVsCERN/"+k+ext)
