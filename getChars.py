import materMTD
import pandas as pd

import logging
logging.basicConfig(format='%(asctime)s  %(filename)s  %(levelname)s: %(message)s',
                    level=logging.INFO)

db = materMTD.MaterMtd('mtd', 'xxxxxxx', 'cmsrm-web.roma1.infn.it')
db.operator('organtin')

# get all parts of type Crystal
lst = db.parts('Crystal')

for x in lst:
    # for each barcode instantiates a part
    p = materMTD.Part(db, x)
    # dump info on screen
    p.dump()
    # get a specific characteristic
    chars = p.getChars('lyAbs')
    # the characteristic is a list of lists
    print(chars)
    


