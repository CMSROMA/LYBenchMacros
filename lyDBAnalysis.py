import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array


def Map(tf):
    """                                                                                                                  
    Maps objets as dict[obj_name][0] using a TFile (tf) and TObject to browse.                                           
    """
    m = {}
    for k in tf.GetListOfKeys():
        n = k.GetName()
        m[n] = tf.Get(n)
    return m

def LYAnalysis(crystal,run):
    files={}
    ly , dt, unixtime = array('d'), array('d'), array('d'), 
    for r in run['runs']:
        files[r]=R.TFile.Open(args.data+"/SourceAnalysis/SourceAnalysis_"+r+".root")
        objs=Map(files[r])
        unixtime.append(files[r].GetCreationDate().Convert(R.kTRUE))
        if not (('charge_spill0' in objs.keys()) or ('charge_spill1' in objs.keys())):
            print "Bad Run (no charge histogram): "+r
            continue
        if not (('filteredWaveform_spill0' in objs.keys()) or ('filteredWaveform_spill1' in objs.keys())):
            print "Bad Run (no waveform): "+r
            continue

        histoName='charge_spill0'
        if not histoName in objs.keys():
            histoName='charge_spill1'
        if 'charge_spill10 'in objs.keys():
            histoName='charge_spill10'

        if (objs[histoName].GetFunction('fTot').GetParameter(10)<1000) or (objs[histoName].GetFunction('fTot').GetParameter(10)>100000):
            print "Bad Run (strange fit): "+r
            continue

        ly.append(objs[histoName].GetFunction('fTot').GetParameter(10))
        dt.append(objs['filteredWaveform_spill0'].GetFunction("f2").GetParameter(1))

    if len(ly)==0:
        print "No good LY data for "+crystal
        lyAvg=-9999
    else:
        lyAvg=sum(ly)/len(ly)

    if len(dt)==0:
        print "No good waveform for "+crystal
        dtAvg=-9999
    else:
        dtAvg=sum(dt)/len(dt)

    if len(unixtime)==0:
        print "No good waveform for "+crystal
        unixtimeAvg=-9999
    else:
        unixtimeAvg=int(sum(unixtime)/len(unixtime))

    ref=array('d')
    for r in run['refRuns']:
        files[r]=R.TFile.Open(args.data+"/SourceAnalysis/SourceAnalysis_"+r+".root")
        objs=Map(files[r])
        if not (('charge_spill0' in objs.keys()) or ('charge_spill1' in objs.keys())):
            print "Bad Run (no charge histogram): "+r
            continue
        if not (('filteredWaveform_spill0' in objs.keys()) or ('filteredWaveform_spill1' in objs.keys())):
            print "Bad Run (no waveform): "+r
            continue

        histoName='charge_spill0'
        if not histoName in objs.keys():
            histoName='charge_spill1'

        if (objs[histoName].GetFunction('fTot').GetParameter(10)<1000) or (objs[histoName].GetFunction('fTot').GetParameter(10)>100000):
            print "Bad Run (strange fit): "+r
            continue

        ref.append(objs[histoName].GetFunction('fTot').GetParameter(10))
    if len(ref)==0:
        print "No good ref data for this crystal!"
        refAvg=-9999
    else:
        refAvg=sum(ref)/len(ref)

#    refAvg=11000.

    ledAvg=LEDAnalysis(crystal,run['ledRuns'])
    return { 'ly':lyAvg, 'dt':dtAvg, 'ref':refAvg, 'pe':ledAvg, 'time':unixtimeAvg }

def LEDAnalysis(crystal,ledRuns):
    files={}
    pe=array('d')
    for r in ledRuns:
        files[r]=R.TFile.Open(args.data+"/SinglePEAnalysis/"+r+"_simul_out.root")
        objs=Map(files[r])
        if not 'PMT_0' in objs.keys():
            print "Bad LED Run (no fit function): "+r
            continue
        if ( abs(objs['PMT_0'].GetParameter(4)-35)<0.01 ):
            print "Bad LED Run (fit not converging): "+r
            continue
        if ( objs['PMT_4'].GetParameter(1) < 1. ):
            print "Bad LED Run (small LED amplitude): "+r
            continue
        pe.append(objs['PMT_0'].GetParameter(2))

    if len(pe)==0:
        print "No good LED data for "+crystal
        peAvg=-9999
    else:
        peAvg=sum(pe)/len(pe)

    return peAvg

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output',dest='output')
parser.add_argument('--db',dest='db')
parser.add_argument('--data',dest='data')
args = parser.parse_args()

import json
crystalsDB=json.load(open(args.db))

#exec "from %s import crystalsDB" % args.db

crystalsDB_withData = {}

for crystal,crystalInfo in crystalsDB.items():
    print "Analysing crystal "+crystal
    for runInfo in crystalInfo['runs']:
        tag=runInfo['tag']
        lyData=LYAnalysis(crystal,runInfo)
        lyData.update({'tag':"%s"%tag})
        data={}
        data.update(crystalInfo)
        data.pop('runs',None)
        data.update(lyData)
        crystalsDB_withData['%s_%s'%(crystal,tag)]=data

#Save CSV using Pandas DataFrame
import pandas as pd
df=pd.DataFrame.from_dict(crystalsDB_withData,orient='index')
#df=df.drop(columns=['runs'])
print(df)

df.to_csv(args.output,header=False)
