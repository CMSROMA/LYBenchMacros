import materMTD
import lyDB
import os        

import logging
logging.basicConfig(format='%(asctime)s  %(filename)s  %(levelname)s: %(message)s',
                    level=logging.INFO)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--csv',dest='csv')
parser.add_argument('--dummy',dest='dummy')
args = parser.parse_args()

ly=lyDB.LYDB(args.csv)
db = materMTD.MaterMtd(os.environ['MATER_USER'], os.environ['MATER_PWD'], os.environ['MATER_HOST'])
if db.connected():
    db.operator(os.environ['MATER_OPERATOR'])
    for index, row in ly.getDB().iterrows():
        xtalID=row['measId'].split('_')[0].replace('BAR','33300060')
        tag='_'.join(row['measId'].split('_')[1:])
        measTime=row['measTime'].strftime('%Y-%m-%d %H:%M:%S')
        dt=row['dt'] # [ns]
        lyRaw=row['ly']/0.511 # [ADC/MeV]
        lyAbs=row['ly']/row['pe']/0.511 # [pe/MeV]
        lyNorm=row['ly']/row['ref'] # normalised to REF
        try:
            logging.info(str(xtalID)+' '+str(measTime)+' '+str(tag)+' '+str(lyNorm)+' '+str(lyAbs)+' '+str(lyRaw)+' '+str(dt))
            if (args.dummy==None):   
                db.newLY(xtalID,start=measTime,notes=tag,lyRaw=lyRaw,lyAbs=lyAbs,lyNorm=lyNorm,decayTime=dt)
        except Exception as e:
            logging.error('Exception while writing to DB:'+str(e))

