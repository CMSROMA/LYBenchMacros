import materMTD
import pandas as pd
import os
import sys

import logging
logging.basicConfig(format='%(asctime)s  %(filename)s  %(levelname)s: %(message)s',
                    level=logging.INFO)

db = materMTD.MaterMtd('mtd', os.environ['MATER_PWD'], 'cmsrm-web.roma1.infn.it')
db.operator(os.environ['MATER_USER'])

# read the CSV file containing Barcode, Type, Comments and Producer
data = pd.read_csv(sys.argv[1])

# loop on rows
for index, row in data.iterrows():
    # define barcode from CSV file content
    barcode = 33300060000000 + int(row['Barcode'])
    xtaltype = str(row['Type'])
    # build producer string
    prod = 'Producer_' + str(row['Producer'])
    notes = str(row['Comments'])
    # register single crystals only
    if xtaltype.find('array') < 0 :
        dx = float(xtaltype.replace(',', '.'))
        # create an instance of a Crystal
        c = materMTD.Crystal(db, barcode = barcode, producer = str(row['Producer']))
        # preregister it
        c.addToDb()
        # perform registration
        c.register(notes, dx)
        print('skip')
    else:
        # these are crystal arrays
        xtaltype = xtaltype.replace('array - ', '')
        dx = float(xtaltype.replace(',', '.'))
        c = materMTD.Crystal(db, barcode = barcode, producer = str(row['Producer']), parttype = 'CrystalArray')
        c.addToDb()
        c.register(notes, dx)
        sp = barcode
        for i in range(1, 17, 1):
            barcode = 33300060000000 + i*100000 + int(row['Barcode'])
            c = materMTD.Crystal(db, barcode = barcode, producer = str(row['Producer']))
            c.addToDb(superpart = sp)
            c.register(notes, dx)

        

    
    


