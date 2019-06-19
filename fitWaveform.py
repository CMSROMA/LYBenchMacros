import numpy as np
from scipy.signal import cheby1, butter, lfilter, freqz
import matplotlib.pyplot as plt
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--input',dest='input')
parser.add_argument('--output',dest='output')
args = parser.parse_args()


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
#    b, a = cheby1(order, 5, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

import ROOT as R
R.gROOT.SetBatch(1)

runID=os.path.splitext(os.path.basename(args.input))[0]

if 'h4Reco_' in runID:
    runID=runID.split('h4Reco_')[1]
if 'histos_' in runID:
    runID=runID.split('histos_')[1]

#Read original waveform from ROOT file
f=R.TFile(args.input)
h4=f.Get("h4")
hh1=R.TProfile("hh1","hh1",1000,-20,480)
h4.Project("hh1","WF_val*100/charge_tot[C0]:WF_time-time[C0]","amp_max[C0]>100 && amp_max[C0]<450 && time_max[C0]>40 && time_max[C0]<65","PROF");

xG = np.empty(hh1.GetNbinsX()-1, dtype="float64")
xG_err = np.empty(hh1.GetNbinsX()-1, dtype="float64")
yG = np.empty(hh1.GetNbinsX()-1, dtype="float64")
yG_err = np.empty(hh1.GetNbinsX()-1, dtype="float64")
for ibin in range(1,hh1.GetNbinsX()):
    xG[ibin-1]=hh1.GetBinCenter(ibin)
    xG_err[ibin-1]=0.
    yG[ibin-1]=hh1.GetBinContent(ibin)
    yG_err[ibin-1]=hh1.GetBinError(ibin)*1.5

# Filter requirements.
order = 2
fs = 2000       # sample rate (MHz)
cutoff = 20  # desired cutoff frequency of the filter, MHz

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.semilogx(0.5*fs*w/np.pi, 20 * np.log10(abs(h)), 'b')
#plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
#plt.axvline(cutoff, color='k')
plt.xlim(1, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [MHz]')
plt.ylabel('gain (dB)')
plt.grid()

# Filter the data, and plot both the original and filtered signals.
yF = butter_lowpass_filter(yG, cutoff, fs, order)
plt.subplot(2, 1, 2)
plt.plot(xG, yG, 'b-', label='data')
plt.plot(xG, yF, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [ns]')
plt.grid()
plt.legend()

plt.subplots_adjust(hspace=0.35)
for ext in ['.png','.pdf']:
    plt.savefig(args.output+'/filteredWaveform_'+runID+ext)

wf=R.TGraphErrors(hh1.GetNbinsX()-1,xG,yF,xG_err,yG_err)
c=R.TCanvas("c","c",900,600)

#now fit the shape
f2=R.TF1("f2","[0]*(TMath::Exp((-2*[1]*(x-[3])+[2]*[2])/2/[1]/[1])*(1-TMath::Erf((-[1]*(x-[3])+[2]*[2])/(TMath::Sqrt(2)*[1]*[2]))))",10,500)
f2.SetParameter(3,10)
f2.SetParLimits(3,5,30)
f2.SetParameter(2,10)
f2.SetParLimits(2,8,12)
f2.SetParameter(1,45)
f2.SetParLimits(1,35,55)
f2.SetParameter(0,0.7)
f2.SetParLimits(0,0,1)

R.gStyle.SetOptTitle(0)
R.gStyle.SetOptFit(0)
f2.SetNpx(10000)
wf.Draw("APE")
wf.GetXaxis().SetRangeUser(-10,200)
wf.Fit(f2,"RB+","",15,200)
xG_shift = np.empty(hh1.GetNbinsX()-1, dtype="float64")
for ibin in range(1,hh1.GetNbinsX()):
    xG_shift[ibin-1]=hh1.GetBinCenter(ibin)+f2.GetParameter(3)
wfOri=R.TGraph(hh1.GetNbinsX()-1,xG_shift,yG)
wfOri.SetMarkerColor(R.kMagenta)
wfOri.SetLineColor(R.kMagenta)
wfOri.Draw("PLSAME")
wf.SetMaximum(1)
#f2.SetLineColor(R.kMagenta)
#f2.SetLineWidth(4)
#f2.Draw("SAME")

text=R.TLatex()
text.DrawLatexNDC(0.6,0.8,"#tau_{fit}=%4.2f#pm%3.2f ns" % (f2.GetParameter(1),f2.GetParError(1)))
#text.DrawLatexNDC(0.6,0.74,"#sigma_{fit}=%3.1f#pm%2.1f ns" % (f2.GetParameter(2),f2.GetParError(2)))
text.SetTextSize(0.03)
text.DrawLatexNDC(0.12,0.91,"Run ID: %s"%(runID))
   
wf.GetYaxis().SetTitle("Amplitude")
wf.GetXaxis().SetTitle("Time (ns)")

for ext in ['.png','.pdf']:
    c.SaveAs(args.output+"/fitWaveform_"+runID+ext)

fOut=R.TFile(args.output+"/SourceAnalysis_"+runID+".root","UPDATE")
fOut.cd()
wf.Write("filteredWaveform_spill0")
fOut.Close()
