import os
import threading
import time
import sys
import datetime
from airtable import Airtable

import logging
logging.basicConfig(format='%(asctime)s  %(filename)s  %(levelname)s: %(message)s',
                    level=logging.INFO)

base_key = 'appQ2YoOIQFBKKIpG'
tables = ['RUNS','Crystals']

airtables={}
for t in tables:
    airtables[t] = Airtable(base_key, t, api_key=os.environ['AIRTABLE_KEY'])

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--db',dest='db')
parser.add_argument('--start',dest='start')
parser.add_argument('--end',dest='end')

args = parser.parse_args()

import measDB
f=measDB.MeasDB(args.db)

runs=airtables['RUNS'].get_all()
xtals=airtables['Crystals'].get_all()

if (args.start == None):
    start=datetime.datetime.now().replace(minute=0, hour=0, second=0)
else:
    start=datetime.datetime.strptime(args.start,'%Y-%m-%d')

if (args.end == None):
    end=start + datetime.timedelta(days=1)
else:
    end=datetime.datetime.strptime(args.end,'%Y-%m-%d')

print('Looking for runs from %s to %s'%(start.date(),end.date()))

from collections import defaultdict
ledRuns=defaultdict(list)
refRuns=defaultdict(list)

for r in runs:
    if r['fields']['Processing status'] != 'VALIDATED':
        continue
    tR=datetime.datetime.strptime(r['fields']['Created'],'%Y-%m-%dT%H:%M:%S.%fZ')
    if  (tR<start or tR>end):
        continue
    if(r['fields']['Type']=='LED' and r['fields']['TAG']=='LED_DAILY'):
        ledRuns[tR.date()].append(r['fields']['RunID'])
    if(r['fields']['Type']=='SOURCE' and r['fields']['TAG']=='REF_DAILY'):
        refRuns[tR.date()].append(r['fields']['RunID'])

measurements=defaultdict(dict)

for r in runs:
    if r['fields']['Processing status'] != 'VALIDATED':
        continue
    tR=datetime.datetime.strptime(r['fields']['Created'],'%Y-%m-%dT%H:%M:%S.%fZ')
    if  (tR<start or tR>end):
        continue

    if(r['fields']['Type']=='SOURCE' and not r['fields']['TAG']=='REF_DAILY'):
        xtalID=next((x['fields']['ID'] for x in xtals if x['id'] == (r['fields']['Crystal'])[0]), None)
        if (xtalID is None):
            print('ERROR: Xtal not found in Crystals table')
            continue

        if (xtalID == 'REF'):
            print('WARNING: Skip REF measurement %s not tagged as REF_DAILY'%r['fields']['RunID'])
            continue

        if (not tR.date() in measurements[xtalID].keys()):
            measurements[xtalID][tR.date()]=[{'id':r['fields']['RunID'],'tag':r['fields']['TAG']}]
        else:
            measurements[xtalID][tR.date()].append({'id':r['fields']['RunID'],'tag':r['fields']['TAG']})

for xt,runs in measurements.items():
    prod,geo=next(( ['prod%d'%x['fields']['VendorID'],x['fields']['Type'].lower()] for x in xtals if x['fields']['ID'] == xt), None)
    for day,rr in runs.items():
        runs=[ r['id'] for r in rr ]
        xtalID=int((xt.split('BAR'))[1])
        tag=rr[0]['tag']
        print(xt,tag,prod,geo,xtalID,runs,refRuns[day],ledRuns[day])
        f.insertMeas(xt,prod,geo,xtalID,runs,refRuns[day],ledRuns[day],tag)

f.save()
