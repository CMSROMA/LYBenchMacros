import materMTD
import pandas as pd

import logging
logging.basicConfig(format='%(asctime)s  %(filename)s  %(levelname)s: %(message)s',
                    level=logging.INFO)

db = materMTD.MaterMtd('mtd', 'xxxxxx', 'cmsrm-web.roma1.infn.it')
db.operator('organtin')

# read the CSV file containing Barcode, Type, Comments and Producer
data = pd.read_csv('toRegister.csv')

# loop on rows
for index, row in data.iterrows():
    # define barcode from CSV file content
    barcode = 33300060000000 + int(row['Barcode'])
    xtaltype = str(row['Type'])
    # register single crystals only
    if xtaltype.find('array') < 0 :
        # if numbers are wriiten using the comma as a decimal separator, convert it into a dot
        dx = float(xtaltype.replace(',', '.'))
        # build producer string
        prod = 'Producer_' + str(row['Producer'])
        notes = row['Comments']
        # create an instance of a Crystal
        c = materMTD.Crystal(db, barcode = barcode, producer = str(row['Producer']))
        # preregister it
        c.addToDb()
        # perform registration
        c.register(notes, dx)

    
    


