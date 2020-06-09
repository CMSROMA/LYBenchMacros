#!/bin/sh

PARSED_OPTIONS=$(getopt -n "$0"  -o i:lsvw --long "input:long,fromHistos,simul,view,web"  -- "$@")
#Bad arguments, something has gone wrong with the getopt command.
if [ $? -ne 0 ];
then
    echo "Usage: $0 -i input"
  exit 1
fi

eval set -- "$PARSED_OPTIONS"

inputFile=""
long=0
simul=0
fromHistos=0
view=0
web=0

while true;
do
  case "$1" in
    -i|--input)
      if [ -n "$2" ];
      then
	  inputFile=$2
	  echo "Running fit on ${inputFile}"
      fi
      shift 2;;

    -l|--long)
      long=1
      echo "LongRun analysis"
      shift;; 
    -s|--simul)
      simul=1
      echo "Scan simultaneous fit analysis"
      shift;; 
    -v|--view)
      view=1
      echo "View results at the end"
      shift;; 
    -w|--web)
      web=1
      echo "Transfer to web server"
      shift;; 
    --fromHistos)
      fromHistos=1
      echo "Running from histograms"
      shift;; 
    --)
      shift
      break;;
  esac
done

if [ "$inputFile" == "" ];
then
    echo "Usage: $0 -i inputFile. Please check your inputs"
  exit 1
fi

#source ~/H4AnalysisEnv.sh

mkdir -p SinglePEAnalysis

if [ $long -eq 1 ]; then
    if [ $fromHistos -eq 0 ]; then
	if [ $simul -eq 0 ]; then
	    root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/ntuples/h4Reco_$inputFile.root\",1,0\)
	else
	    root -l -b -q SinglePEAnalysis_LedScan_Simultaneous_LL.C+\(\"/data/cmsdaq/led/ntuples/\",\"$inputFile\",1\)
	fi
    else
	if [ ! -f "/data/cmsdaq/led/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/led/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/led/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=led --longRun
	fi
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/histos/histos_$inputFile.root\",1,1\)
    fi
else
    if [ $fromHistos -eq 0 ]; then
	if [ $simul -eq 0 ]; then
	    root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/ntuples/h4Reco_$inputFile.root\",0,0\)
	else
	    root -l -b -q SinglePEAnalysis_LedScan_Simultaneous_LL.C+\(\"/data/cmsdaq/led/ntuples/\",\"$inputFile\",0\)
	fi
    else
	if [ ! -f "/data/cmsdaq/led/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/led/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/led/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=led
	fi
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/ntuples/histos_$inputFile.root\",0,1\)
    fi
fi

if [ $view -eq 1 ]; then
    for file in SinglePEAnalysis/*${inputFile}*.png; do
	display $file > /dev/null 2>&1 & 
    done
fi

if [ $web -eq 1 ]; then
    mkdir -p /data/cmsdaq/www/process/${inputFile}
    cp -v /data/cmsdaq/www/process/index.php /data/cmsdaq/www/process/${inputFile}/index.php
    for file in SinglePEAnalysis/*${inputFile}*.png; do
	cp -v $file /data/cmsdaq/www/process/${inputFile}/
    done
    for file in SinglePEAnalysis/*${inputFile}*.pdf; do
	cp -v $file /data/cmsdaq/www/process/${inputFile}/
    done
fi
