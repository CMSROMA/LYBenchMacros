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

objs['dt']=R.TGraphErrors(nprod)
objs['dt'].SetName('dt')
for ip in range(0,nprod):
    xC,yC,xR,yR=R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gDT_vendors'].GetPoint(ip,xC,yC)
    objsRome['dt_ByProd'].GetPoint(ip,xR,yR)
    if (xC != xR):
        print 'Hey!!'
    objs['dt'].SetPoint(ip,yC,yR)
    objs['dt'].SetPointError(ip,0.3,0.3)

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

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gLOS_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLOS_vendors'].GetPoint(0,xCRef,yCRef)
    objsRome['lyNormAbs_TOFPET_ByProd'].GetPoint(ip,xR,yR)
    if (xC != xR):
        print 'Hey!!'
    objs['lyS'].SetPoint(ip,yC/yCRef,yR)
    objs['lyS'].SetPointError(ip,0.03,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip))

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

objs['lyRomeSVsP']=R.TGraphErrors(nprod)
objs['lyRomeSVsP'].SetName('lyRomeSVsP')

for ip in range(0,nprod):
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

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR,xD,yD,xDR,yDR,xR_D,yR_D,xR_DR,yR_DR=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)

    objsCERN['gLOS_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLOS_vendors'].GetPoint(0,xCRef,yCRef)
    objsCERN['gDT_vendors'].GetPoint(ip,xD,yD)
    objsCERN['gDT_vendors'].GetPoint(0,xDR,yDR)

    objsRome['lyNormAbs_TOFPET_ByProd'].GetPoint(ip,xR,yR)
    objsRome['dt_ByProd'].GetPoint(ip,xR_D,yR_D)
    objsRome['dt_ByProd'].GetPoint(0,xR_DR,yR_DR)
    if (xC != xR or xC !=xD or xC != xR_D ):
        print 'Hey!!'
    if (xCRef != xDR or xCRef !=xR_DR):
        print 'Hey!!'

    objs['lySOverDt'].SetPoint(ip,(yC/yCRef)/(yD/yDR),yR/(yR_D/yR_DR))
    objs['lySOverDt'].SetPointError(ip,0.03,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip))

objs['lyPOverDt']=R.TGraphErrors(nprod)
objs['lyPOverDt'].SetName('lyPOverDt')
objs['lyPOverDt'].SetTitle('lyPOverDt')

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR,xD,yD,xDR,yDR,xR_D,yR_D,xR_DR,yR_DR=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)

    objsCERN['gLY_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gLY_vendors'].GetPoint(0,xCRef,yCRef)
    objsCERN['gDT_vendors'].GetPoint(ip,xD,yD)
    objsCERN['gDT_vendors'].GetPoint(0,xDR,yDR)

    objsRome['lyNormAbs_PMT_ByProd'].GetPoint(ip,xR,yR)
    objsRome['dt_ByProd'].GetPoint(ip,xR_D,yR_D)
    objsRome['dt_ByProd'].GetPoint(0,xR_DR,yR_DR)
    if (xC != xR or xC !=xD or xC != xR_D ):
        print 'Hey!!'
    if (xCRef != xDR or xCRef !=xR_DR):
        print 'Hey!!'

    objs['lyPOverDt'].SetPoint(ip,(yC/yCRef)/(yD/yDR),yR/(yR_D/yR_DR))
    objs['lyPOverDt'].SetPointError(ip,0.03,objsRome['lyNormAbs_TOFPET_ByProd'].GetErrorY(ip))


objs['ctr']=R.TGraphErrors(nprod)
objs['ctr'].SetName('ctr')

for ip in range(0,nprod):
    xCRef,yCRef,xC,yC,xR,yR,xRRef,yRRef=R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0),R.Double(0)
    objsCERN['gTR_ave_vendors'].GetPoint(ip,xC,yC)
    objsCERN['gTR_ave_vendors'].GetPoint(0,xCRef,yCRef)
    objsRome['ctr_ByProd'].GetPoint(ip,xR,yR)
    objsRome['ctr_ByProd'].GetPoint(0,xRRef,yRRef)
    if (xC != xR):
        print 'Hey!!'
    objs['ctr'].SetPoint(ip,yC*1000,yR)
    objs['ctr'].SetPointError(ip,3,objsRome['ctr_ByProd'].GetErrorY(ip))

out=R.TFile("romeCernCorrelation.root","RECREATE")
for h,histo in objs.items():
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
    'ctr': { 'X':'#sigma_{t} ^{CERN}', 'Y':'#sigma_{t} ^{ROME}' },
}

ranges = {
    'dt': { 'X' : [35,50] , 'Y' : [35,50] },
    'lyPMT': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyS': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyCERNSVsP': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyRomeSVsP': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lySOverDt': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'lyPOverDt': { 'X' : [0.7,1.3] , 'Y' : [0.7,1.3] },
    'ctr': { 'X' : [70,110] , 'Y' : [80,200] },
}


fX = R.TF1("fX","x",0,1000)

text=R.TLatex()
text.SetTextSize(0.04)

for k,g in objs.items():

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
    else:
        g.Fit("pol1")

    for ext in ['.png','.pdf']:
        c1.SaveAs("RomeVsCERN/"+k+ext)
