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


R.gROOT.SetBatch(1)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input',dest='input')
#parser.add_argument('--output',dest='output')
args = parser.parse_args()

import glob
files=glob.glob("SourceAnalysis/SourceAnalysis_"+args.input+"*.root")

from array import array

ly, ly_err, lyres, lyres_err = array('d'), array('d'), array('d'), array('d')

for file in files:
    f=R.TFile(file)
    his=Map(f)
    for h in his:
        if 'charge_' in h:
            fTot=his[h].GetFunction("fTot")
#            if (fTot.GetParameter(10)>20000):
#                continue
            ly.append(fTot.GetParameter(10))
            ly_err.append(fTot.GetParError(10))
            lyres.append(fTot.GetParameter(11)/fTot.GetParameter(10))
            lyres_err.append(fTot.GetParError(11)/fTot.GetParameter(10))
            
lyArray=np.array(ly)
lyResArray=np.array(lyres)

histos={}
c=R.TCanvas("c","c",900,700)

histos['ly']=R.TH1F('ly_'+args.input,'ly_'+args.input,10,1-5*lyArray.std()/lyArray.mean(),1+5*lyArray.std()/lyArray.mean())
for val in lyArray:
    histos['ly'].Fill(val/lyArray.mean())
histos['ly'].Draw()
for ext in ['png','pdf']:
    c.SaveAs("SourceAnalysis/lyStability_"+ args.input +"."+ext)

histos['lyRes']=R.TH1F('lyRes_'+args.input,'lyRes_'+args.input,60,1-5*lyResArray.std()/lyResArray.mean(),1+5*lyResArray.std()/lyResArray.mean())
for val in lyResArray:
    histos['lyRes'].Fill(val/lyResArray.mean())
histos['lyRes'].Draw()
for ext in ['png','pdf']:
    c.SaveAs("SourceAnalysis/lyResStability_"+ args.input +"."+ext)
