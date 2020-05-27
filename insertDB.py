import io
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--crys',dest='crys')
parser.add_argument('--runs',dest='runs')
parser.add_argument('--tag',dest='tag')
parser.add_argument('--id',dest='xtalid')
parser.add_argument('--ledruns',dest='ledRuns')
parser.add_argument('--refruns',dest='refRuns')
parser.add_argument('--prod',dest='producer')
parser.add_argument('--geom',dest='geometry')
parser.add_argument('--db',dest='db')

args = parser.parse_args()

crys=str(args.crys)
tag=str(args.tag)
xtalid=int(args.xtalid)
runs=str(args.runs).split(',')
refRuns=str(args.refRuns).split(',')
ledRuns=str(args.ledRuns).split(',')
prod=str(args.producer)
geo=str(args.geometry)

if (int(crys.split('BAR0')[1]) != xtalid):
     print('ERROR. Check that ID %s matches crystal number %d'%(crys,xtalid))
     exit(-1)

import json
db=json.load(open(args.db))

print('=========> Crystal %s '%crys)
if crys in db.keys():
     if (tag in [  r['tag'] for r in db[crys]['runs'] ]):
          print('ERROR. Tag %s already present'%tag)
     else:
          db[crys]['runs'].append({'tag':tag,'runs':runs, 'refRuns':refRuns,'ledRuns':ledRuns})
          print('Tag %s for crystal %s inserted correctly. Total runs for this xtal %d'%(tag,crys,len(db[crys]['runs'])))
else:
     db[crys]={ 'type':'xtal','producer':prod,'geometry':geo,'id':xtalid,'runs':[ {'tag':tag,'runs':runs, 'refRuns':refRuns,'ledRuns':ledRuns} ] } 
     print('Crystal %s inserted correctly'%crys)

print('Runs for this xtal %s'%str([ '%s:%s,'%(str(r['tag']),str(r['runs'])) for r in db[crys]['runs']]))
print('------ Number of crystals in DB %d ------'%len(db.keys()))

with open(args.db, 'w') as file:
     file.write(json.dumps(db))


