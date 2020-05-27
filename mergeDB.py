import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output',dest='output')
parser.add_argument('--db1',dest='db1')
parser.add_argument('--db2',dest='db2')
args = parser.parse_args()

exec "from %s import crystalsDB as db1" % args.db1
exec "from %s import crystalsDB as db2" % args.db2

#crystalsDB_withData = {}

for crystal,crystalInfo in db1.items():
#    print "Analysing crystal "+crystal
    for runInfo in crystalInfo['runs']:
        tag=runInfo['tag']

for crystal,crystalInfo in db2.items():
    if (len(crystalInfo['runs'])>1):
        print(crystal,crystalInfo['runs'])
        continue
    if crystal in db1.keys():
        irr0_runs=[ 'IRR0' in run['tag'] for run in db1[crystal]['runs']]
        db1[crystal]['runs'].append({'tag':'PREIRR_0','runs':crystalInfo['runs'], 'refRuns':crystalInfo['refRuns'],'ledRuns':crystalInfo['ledRuns']})
    else:
        db1[crystal]={ 'type':'xtal','producer':crystalInfo['producer'],'geometry':crystalInfo['geometry'],'id':int(crystal.split('BAR000')[1]),'runs':[ {'tag':'PREIRR_0','runs':crystalInfo['runs'], 'refRuns':crystalInfo['refRuns'],'ledRuns':crystalInfo['ledRuns'] } ] } 

print('Number of crystals in DB %d'%len(db1.keys()))

import json
with open(args.output, 'w') as file:
     file.write(json.dumps(db1)) # use `json.loads` to do the reverse    
