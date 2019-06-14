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
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"$inputFile\",1,0\)
    else
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"$inputFile\",1,1\)
    fi
else
    if [ $fromHistos -eq 0 ]; then
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"$inputFile\",0,0\)
    else
	root -l -b -q SinglePEAnalysis_longRun.C+\(\"$inputFile\",0,1\)
    fi
fi
