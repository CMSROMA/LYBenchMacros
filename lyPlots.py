import ROOT as R

crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("LYAnalysis/crystalsData.csv","id/C:prod/C:geo/C:pe/F:dt/F:ref/F:ly/F");

producers = [ 'prod'+str(i) for i in range(1,7) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

histos = {}
for prod in producers: 
    histos['ly_'+prod]=R.TH1F('ly_'+prod,'ly_'+prod,400,0.,2000.)
    histos['dt_'+prod]=R.TH1F('dt_'+prod,'dt_'+prod,100,20.,50.)
    histos['lyNorm_'+prod]=R.TH1F('lyNorm_'+prod,'lyNorm_'+prod,400,0.5,1.5)
    for geo in geoms:
        histos['ly_'+prod+'_'+geo]=R.TH1F('ly_'+prod+'_'+geo,'ly_'+prod+'_'+geo,400,0.,2000.)
        histos['dt_'+prod+'_'+geo]=R.TH1F('dt_'+prod+'_'+geo,'dt_'+prod+'_'+geo,100,20.,50.)
        histos['lyNorm_'+prod+'_'+geo]=R.TH1F('lyNorm_'+prod+'_'+geo,'lyNorm_'+prod+'_'+geo,400,0.5,1.5)

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    histos['ly_'+prod].Fill(crys.ly/16.)
    histos['ly_'+prod+'_'+geo].Fill(crys.ly/16.)
    histos['lyNorm_'+prod].Fill(crys.ly/crys.ref)
    histos['lyNorm_'+prod+'_'+geo].Fill(crys.ly/crys.ref)
    histos['dt_'+prod].Fill(crys.dt)
    histos['dt_'+prod+'_'+geo].Fill(crys.dt)

out=R.TFile("LYAnalysis/LYplots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
out.Write()
out.Close()
