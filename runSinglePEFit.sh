#!/bin/sh

PARSED_OPTIONS=$(getopt -n "$0"  -o i:l --long "input:long,fromHistos"  -- "$@")
#Bad arguments, something has gone wrong with the getopt command.
if [ $? -ne 0 ];
then
    echo "Usage: $0 -i input"
  exit 1
fi

eval set -- "$PARSED_OPTIONS"

inputFile=""
long=0
fromHistos=0

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

mkdir -p SinglePEAnalysis

if [ $long -eq 1 ]; then
    if [ $fromHistos -eq 0 ]; then
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/ntuples/h4Reco_$inputFile.root\",1,0\)
    else
	if [ ! -f "/data/cmsdaq/led/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/led/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/led/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=led --longRun
	fi
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/histos/histos_$inputFile.root\",1,1\)
    fi
else
    if [ $fromHistos -eq 0 ]; then
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/ntuples/h4Reco_$inputFile.root\",0,0\)
    else
	if [ ! -f "/data/cmsdaq/led/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/led/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/led/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=led
	fi
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"/data/cmsdaq/led/ntuples/histos_$inputFile.root\",0,1\)
    fi
fi
