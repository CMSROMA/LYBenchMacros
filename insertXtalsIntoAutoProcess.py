import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--db',dest='db')
args = parser.parse_args()

import json
crystalsDB=json.load(open(args.db))

import os
from airtable import Airtable
base_key = 'appQ2YoOIQFBKKIpG'
tables = ['Crystals']

airtables={}
for t in tables:
    airtables[t] = Airtable(base_key, t, api_key=os.environ['AIRTABLE_KEY'])

records=airtables['Crystals'].get_all()
xtals=[ t['fields']['ID'] for t in records ]

for crystal,crystalInfo in crystalsDB.items():
    if crystal in xtals:
        print("Crystal "+crystal+" already inserted. Skipping")
        continue
    print("Adding "+crystal)
    airtables['Crystals'].insert({'ID': crystal, 'Status':'ok','Location':'Lab2','VendorID':int(crystalInfo['producer'].split('prod')[1]),'Type':crystalInfo['geometry'].upper()})

