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

def integral(g,xmin,xmax):
    v=0
    x=g.GetX()
    y=g.GetY()
    for i in range(0,g.GetN()):
        if x[i]<xmin:
            continue
        if x[i]>xmax:
            break
        v=v+y[i]
    return v

def LYAnalysis(crystal,crystalInfo):
    files={}

    ly , dt, i0, i1, i2, i3 = array('d'), array('d'), array('d'), array('d'), array('d'), array('d')
    for r in crystalInfo['runs']:
#        print("Opening SourceAnalysis/SourceAnalysis_"+r+".root")
        files[r]=R.TFile.Open("SourceAnalysis/SourceAnalysis_"+r+".root")
        objs=Map(files[r])

        if not 'charge_spill0' in objs.keys():
            print "Bad Run (no charge histogram): "+r
            continue
        if not 'filteredWaveform_spill0' in objs.keys():
            print "Bad Run (no waveform): "+r
            continue
#        if not 'waveform_spill0' in objs.keys():
#            print "Bad Run (no waveform): "+r
#            continue

        if (objs['charge_spill0'].GetFunction('fTot').GetParameter(10)<1000) or (objs['charge_spill0'].GetFunction('fTot').GetParameter(10)>100000):
            print "Bad Run (strange fit): "+r
            continue

        ly.append(objs['charge_spill0'].GetFunction('fTot').GetParameter(10))
        dt.append(objs['filteredWaveform_spill0'].GetFunction("f2").GetParameter(1))
        i0.append(integral(objs['filteredWaveform_spill0'],0,30))
        i1.append(integral(objs['filteredWaveform_spill0'],0,50))
        i2.append(integral(objs['filteredWaveform_spill0'],0,300))
        i3.append(integral(objs['filteredWaveform_spill0'],0,450))

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

    if len(i0)==0:
        print "No good waveform for "+crystal
        i0Avg=-9999
    else:
        i0Avg=sum(i0)/len(i0)

    if len(i1)==0:
        print "No good waveform for "+crystal
        i1Avg=-9999
    else:
        i1Avg=sum(i1)/len(i1)

    if len(i2)==0:
        print "No good waveform for "+crystal
        i2Avg=-9999
    else:
        i2Avg=sum(i2)/len(i2)

    if len(i3)==0:
        print "No good waveform for "+crystal
        i3Avg=-9999
    else:
        i3Avg=sum(i3)/len(i3)


    ref=array('d')
    for r in crystalInfo['refRuns']:
        files[r]=R.TFile.Open("SourceAnalysis/SourceAnalysis_"+r+".root")
        objs=Map(files[r])
        if not 'charge_spill0' in objs.keys():
            print "Bad Run (no charge histogram): "+r
            continue
        if (objs['charge_spill0'].GetFunction('fTot').GetParameter(10)<1000) or (objs['charge_spill0'].GetFunction('fTot').GetParameter(10)>100000):
            print "Bad Run (strange fit): "+r
            continue
        ref.append(objs['charge_spill0'].GetFunction('fTot').GetParameter(10))
    if len(ref)==0:
        print "No good ref data for this crystal!"
        refAvg=-9999
    else:
        refAvg=sum(ref)/len(ref)

    ledAvg=LEDAnalysis(crystal,crystalInfo['ledRuns'])
    return { 'ly':lyAvg, 'dt':dtAvg, 'ref':refAvg, 'pe':ledAvg, 'i0':i0Avg, 'i1':i1Avg, 'i2':i2Avg, 'i3':i3Avg }

def LEDAnalysis(crystal,ledRuns):
    files={}
    pe=array('d')
    for r in ledRuns:
        files[r]=R.TFile.Open("SinglePEAnalysis/"+r+"_simul_out.root")
        objs=Map(files[r])
        if not 'PMT_0' in objs.keys():
            print "Bad LED Run (no fit function): "+r
            continue
        if ( abs(objs['PMT_0'].GetParameter(4)-35)<0.01 ):
            print "Bad LED Run (fit not converging): "+r
            continue
#        if ( objs['PMT_4'].GetParameter(1) < 1. ):
#            print "Bad LED Run (small LED amplitude): "+r
#            continue
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
args = parser.parse_args()

from crystalsDB import crystalsDB

crystalsDB_withData = {}

for crystal,crystalInfo in crystalsDB.items():
    print "Analysing crystal "+crystal
    lyData=LYAnalysis(crystal,crystalInfo)
    crystalInfo.update(lyData)
    crystalsDB_withData[crystal]=crystalInfo

#Save CSV using Pandas DataFrame
import pandas as pd
df=pd.DataFrame.from_dict(crystalsDB_withData,orient='index')
df=df.drop(columns=['runs','ledRuns','refRuns'])
df.to_csv(args.output,header=False)
