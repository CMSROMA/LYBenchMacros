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

source ~/H4AnalysisEnv.sh

mkdir -p SourceAnalysis

if [ $long -eq 1 ]; then
    if [ $fromHistos -eq 0 ]; then
	python fitSource.py --input=/data/cmsdaq/source/ntuples/h4Reco_$inputFile.root --output=SourceAnalysis --longRun
    else
	if [ ! -f "/data/cmsdaq/source/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/source/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/source/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=source --longRun
	fi
	python fitSource.py --input=/data/cmsdaq/source/histos/histos_$inputFile.root --output=SourceAnalysis --fromHistos --longRun
    fi
else
    if [ $fromHistos -eq 0 ]; then
	python fitSource.py --input=/data/cmsdaq/source/ntuples/h4Reco_$inputFile.root --output=SourceAnalysis
    else
	if [ ! -f "/data/cmsdaq/source/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/source/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/source/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=source
	fi
	python fitSource.py --input=/data/cmsdaq/source/histos/histos_$inputFile.root --output=SourceAnalysis --fromHistos
    fi
fi

python fitWaveform.py --input=/data/cmsdaq/source/ntuples/h4Reco_${inputFile}.root --output=SourceAnalysis
