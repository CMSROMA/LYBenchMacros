import materMTD
import lyDB
import os        

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--csv',dest='csv')
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
        print(xtalID,measTime,tag,lyNorm,lyAbs,lyRaw,dt)
#        try:   
#            db.newActivity(xtalID, 'LY evaluation',start=measTime,notes=tag)
#            db.newLY(xtalID,lyRaw,lyAbs,lyNorm,dt)
#        except Exception as e:
#            print('Exception while writing to DB:'+str(e))

