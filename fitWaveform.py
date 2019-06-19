import numpy as np
from scipy.signal import cheby1, butter, lfilter, freqz
import matplotlib.pyplot as plt


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

# Filter requirements.
order = 2
fs = 2000       # sample rate (MHz)
cutoff = 20  # desired cutoff frequency of the filter, MHz

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [MHz]')
plt.grid()


# Demonstrate the use of the filter.
# First make some data to be filtered.
#T = 5.0         # seconds
#n = int(T * fs) # total number of samples
#t = np.linspace(0, T, n, endpoint=False)
# "Noisy" data.  We want to recover the 1.2 Hz signal from this.
#data = np.sin(1.2*2*np.pi*t) + 1.5*np.cos(9*2*np.pi*t) + 0.5*np.sin(12.0*2*np.pi*t)

f=R.TFile("lysoShape.root")

hh1=f.Get("hh1")
xG = np.empty(hh1.GetNbinsX()-1, dtype="float64")
xG_err = np.empty(hh1.GetNbinsX()-1, dtype="float64")
yG = np.empty(hh1.GetNbinsX()-1, dtype="float64")
yG_err = np.empty(hh1.GetNbinsX()-1, dtype="float64")

for ibin in range(1,hh1.GetNbinsX()):
    xG[ibin-1]=hh1.GetBinCenter(ibin)
    xG_err[ibin-1]=0.
    yG[ibin-1]=hh1.GetBinContent(ibin)
    yG_err[ibin-1]=hh1.GetBinError(ibin)*1.5
#    yG_err[ibin-1]=0.001
#data = np.genfromtxt('lysoShape.csv', dtype="d,d",names=['time','amp'], delimiter=" ")

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
    plt.savefig('FilteredWaveform'+ext)
#plt.show()

#wf=R.TGraph(hh1.GetNbinsX(),xG,yF)

wf=R.TGraphErrors(hh1.GetNbinsX()-1,xG,yF,xG_err,yG_err)
c=R.TCanvas("c","c",900,600)

#now fit the shape
f2=R.TF1("f2","[0]*(TMath::Exp((-2*[1]*(x-[3])+[2]*[2])/2/[1]/[1])*(1-TMath::Erf((-[1]*(x-[3])+[2]*[2])/(TMath::Sqrt(2)*[1]*[2]))))",10,500)
f2.SetParameter(3,10)
f2.SetParLimits(3,5,50)
f2.SetParameter(2,8)
f2.SetParLimits(2,4,15)
f2.SetParameter(1,45)
f2.SetParLimits(1,30,60)
f2.SetParameter(0,180)
f2.SetParLimits(0,0,500)

#Double exp
#f2=R.TF1("f2","[0]*(TMath::Exp(-(x-[3])/[1])-TMath::Exp(-(x-[3])/[2]))",0,500)
#f2.SetParameter(3,10)
#f2.SetParLimits(3,5,50)
#f2.SetParameter(2,8)
#f2.SetParLimits(2,1,20)
#f2.SetParameter(1,45)
#f2.SetParLimits(1,30,60)
#f2.SetParameter(0,180)
#f2.SetParLimits(0,0,500)

R.gStyle.SetOptTitle(0)
R.gStyle.SetOptFit(0)
f2.SetNpx(10000)
wf.Draw("APE")
wf.GetXaxis().SetRangeUser(-10,200)
wf.Fit(f2,"RB","0",15,200)
#f2.SetLineColor(R.kMagenta)
#f2.SetLineWidth(4)
#f2.Draw("SAME")


text=R.TLatex()
text.DrawLatexNDC(0.6,0.8,"#tau_{fit}=%4.2f#pm%3.2f ns" % (f2.GetParameter(1),f2.GetParError(1)))
#text.DrawLatexNDC(0.6,0.74,"#sigma_{fit}=%3.1f#pm%2.1f ns" % (f2.GetParameter(2),f2.GetParError(2)))
  
wf.GetYaxis().SetTitle("Amplitude")
wf.GetXaxis().SetTitle("Time (ns)")

for ext in ['.png','.pdf']:
    c.SaveAs("fitWaveform"+ext)
