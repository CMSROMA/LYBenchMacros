#!/bin/sh

PARSED_OPTIONS=$(getopt -n "$0"  -o i:p:l --long "input:led:long,fromHistos"  -- "$@")
#Bad arguments, something has gone wrong with the getopt command.
if [ $? -ne 0 ];
then
    echo "Usage: $0 -i input"
  exit 1
fi

eval set -- "$PARSED_OPTIONS"

inputFile=""
ledFile=""
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

    -p|--led)
      if [ -n "$2" ];
      then
          ledFile=$2
          echo "Ledrun ${ledFile}"
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

if [ "$ledFile" == "" ];
then
    echo "Usage: $0 -p ledFile. Please check your inputs"
  exit 1
fi


source ~/H4AnalysisEnv.sh

mkdir -p SourceAnalysis

if [ $long -eq 1 ]; then
    if [ $fromHistos -eq 0 ]; then
	python fitSource.py --input=/data/cmsdaq/source/ntuples/h4Reco_$inputFile.root --output=SourceAnalysis --led=SinglePEAnalysis/${ledFile}_simul_out.root --longRun
    else
	if [ ! -f "/data/cmsdaq/source/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/source/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/source/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=source --longRun
	fi
	python fitSource.py --input=/data/cmsdaq/source/histos/histos_$inputFile.root --output=SourceAnalysis --led=SinglePEAnalysis/${ledFile}_simul_out.root --fromHistos --longRun
    fi
else
    if [ $fromHistos -eq 0 ]; then
	python fitSource.py --input=/data/cmsdaq/source/ntuples/h4Reco_$inputFile.root --output=SourceAnalysis --led=SinglePEAnalysis/${ledFile}_simul_out.root
    else
	if [ ! -f "/data/cmsdaq/source/histos/histos_${inputFile}.root" ]; then
	    python makeHisto.py --input=/data/cmsdaq/source/ntuples/h4Reco_${inputFile}.root --output=/data/cmsdaq/source/histos/histos_${inputFile}.root --inputEnvData=/data/cmsdaq/slowControl/temperatures  --runType=source
	fi
	python fitSource.py --input=/data/cmsdaq/source/histos/histos_$inputFile.root --output=SourceAnalysis --led=SinglePEAnalysis/${ledFile}_simul_out.root --fromHistos
    fi
fi

python fitWaveform.py --input=/data/cmsdaq/source/ntuples/h4Reco_${inputFile}.root --output=SourceAnalysis
