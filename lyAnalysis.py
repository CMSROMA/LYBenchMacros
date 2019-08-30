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

def LYAnalysis(crystalInfo):
    files={}
    ly=array('d')
    for r in crystalInfo['runs']:
        files[r]=R.TFile.Open("SourceAnalysis/SourceAnalysis_"+r+".root")
        objs=Map(files[r])
        if not 'charge_spill0' in objs.keys():
            print "Bad Run (no charge histogram): "+r
            continue
        if (objs['charge_spill0'].GetFunction('fTot').GetParameter(10)<1000) or (objs['charge_spill0'].GetFunction('fTot').GetParameter(10)>100000):
            print "Bad Run (strange fit): "+r
            continue
        ly.append(objs['charge_spill0'].GetFunction('fTot').GetParameter(10))
    if len(ly)==0:
        print "No good data for this crystal!"
        lyAvg=-9999
    else:
        lyAvg=sum(ly)/len(ly)
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

    ledAvg=LEDAnalysis(crystalInfo['ledRuns'])
    return { 'ly':lyAvg, 'ref':refAvg, 'pe':ledAvg }

def LEDAnalysis(ledRuns):
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
        if ( objs['PMT_4'].GetParameter(1) < 1. ):
            print "Bad LED Run (small LED amplitude): "+r
            continue
        pe.append(objs['PMT_0'].GetParameter(2))

    if len(pe)==0:
        print "No good LED data for this crystal!"
        peAvg=-9999
    else:
        peAvg=sum(pe)/len(pe)

    return peAvg

from crystalsDB import crystalsDB

for crystal,crystalInfo in crystalsDB.items():
    print "Analysing crystal "+crystal
    lyData=LYAnalysis(crystalInfo)
    print lyData
