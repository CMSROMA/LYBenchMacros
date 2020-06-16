import pandas as pd
import datetime
import json
import os

class LYDB():
    def __init__(self, dbFile=None):
        if (dbFile is None):
            print('Should provide a csv file to start')
            return
        self.dbFile=dbFile
        print('Opening '+dbFile)
        if (os.path.isfile(dbFile)):
            self.db=pd.read_csv(dbFile,header=None,names=['measId','prod','geo','ref','measTime','measTag','pe','dt','xtalType','myId','ly'])
            self.db['measTime']=pd.to_datetime(self.db.measTime,unit='s')
            print('Loaded MeasDB from '+dbFile)
        else:
            print('Cannot open '+dbFile)
            return

    def getDB(self):
        return self.db
