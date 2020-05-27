#!/bin/sh

echo 'REMOVING OLD DB! RECREATING A NEW ONE!'
read -p "Are you sure (y/n)?" answer

if [ "${answer}" != "y" ]; then
    exit
fi

rm -rf crystalsDB_LYBench.json
python mergeDB.py --db1=crystalsDB_LYBench --db2=crystalsDB --output=crystalsDB_LYBench.json
./addOldRuns.sh
