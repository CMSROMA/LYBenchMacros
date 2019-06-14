import ROOT as R
from root_pandas import read_root

R.gROOT.SetBatch(1)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input',dest='inputData')
parser.add_argument('--inputEnvData',dest='inputEnvData')
parser.add_argument('--output',dest='output')
parser.add_argument('--longRun',dest='longRun',action='store_true')
parser.add_argument('--runType',dest='runType')

parser.set_defaults(longRun=False)

args = parser.parse_args()

#helper class to access environmental data
class TempData:
    #load data from ROOT file and transform in pandas DF
    def __init__(self, inputFiles):
        self.df=read_root(inputFiles.split(","))
        self.df.set_index('timestamp', inplace=True)

    #return the closest environmental data values to a timestamp index
    def closestValues(self, timeStamp):
        return self.df.iloc[self.df.index.get_loc(timeStamp,method='nearest')]

    #return the closest bench temperature to a timestamp index
    def tBench(self, timeStamp):
        return self.df.iloc[self.df.index.get_loc(timeStamp,method='nearest')]['tbench']

    #return the closest lab temperature to a timestamp index
    def tLab(self, timeStamp):
        return self.df.iloc[self.df.index.get_loc(timeStamp,method='nearest')]['tlab']


tData=TempData(args.inputEnvData)

data=R.TFile(args.inputData)
h4=data.Get("h4")

histos={}

histos={}
histos['spill']=R.TH1F("spill","spill",200,-0.5,199.5);

h4.Project("spill","spill")

if (not args.longRun):
    if (args.runType != "led" and args.runType !="ped" ):
        histos['charge_spill0']=R.TH1F("charge_spill0","charge_spill0",1000,1000,101000)
    else:
        histos['charge_spill0']=R.TH1F("charge_spill0","charge_spill0",1000,-50,450)
    histos['tBench_spill0']=R.TH1F("tBench_spill0","tBench_spill0",1000,15.,25.)
    histos['tLab_spill0']=R.TH1F("tLab_spill0","tLab_spill0",1000,15.,25.)

for ievent,event in enumerate(h4):
    key="_spill0"
    if (args.longRun):
        key="_spill"+str(event.spill)
        if "charge"+key not in histos.keys():
            if (args.runType != "led" and args.runType !="ped" ):
                histos['charge'+key]=R.TH1F("charge"+key,"charge"+key,1000,0,100000)
            else:
                histos['charge'+key]=R.TH1F("charge"+key,"charge"+key,1000,-50,450)
            histos['tBench'+key]=R.TH1F("tBench"+key,"tBench"+key,1000,10.,30.)
            histos['tLab'+key]=R.TH1F("tLab"+key,"tLab"+key,1000,10.,30.)
        
    if (ievent%100==0):
        print "Analysing event %d"%ievent
    #fill environmental data histograms only every 100 events
    #get closest value of environmental data 
        t=tData.closestValues(event.time_stamps[1])
        histos['tBench'+key].Fill(float(t['tbench']))
        histos['tLab'+key].Fill(float(t['tlab']))

    histos['charge'+key].Fill(event.charge_tot[event.C0])

if (not args.longRun):
    print "Average temperature during run: %4.2f"%(histos['tBench_spill0'].GetMean())

print "Saving histograms to "+args.output
fOut=R.TFile(args.output,"RECREATE")
for hn, histo in histos.iteritems():
    if isinstance(histo,R.TH1F):
        histo.SetMinimum(0.)
    if isinstance(histo,R.TGraphAsymmErrors):
        histo.SetMinimum(0.)
        histo.SetMaximum(1.1)
    histo.Write()
fOut.Close()
