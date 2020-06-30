import mysql.connector
import datetime
import re

class MaterMtd:
    _username = ''
    _password = ''
    _host     = ''
    _user     = -1
    _cnx      = None
    _cursor   = None

    def __init__(self, user = 'mater', password = 'materpassword',
                 host = 'localhost'):
        self.setup(user, password, host)

    def __del__(self):
        self.disconnect()
        
    def setup(self, user, password, host):
        self._username = user
        self._password = password
        self._host = host
        self.connect()

    def disconnect(self):
        self._cnx.close()

    def connect(self):
        try:
            self._cnx = mysql.connector.connect(user=self._username, password=self._password,
                                                host=self._host, database='mtd', use_pure = True,
                                                charset='utf8', autocommit=True)
        except mysql.connector.Error as err:
            print(err.msg)

    def connected(self):
        if self._cnx == None:
            return False
        else:
            return True

    def startTransaction(self):
        print('---- Starting a transaction')
        self._cnx.start_transaction()
        self._cursor = self._cnx.cursor(buffered=True)

    def cursor(self):
        # get a new cursor
        return self._cnx.cursor(buffered=True)

    def rollback(self):
        print('---- Aborting transaction')
        if self._cursor != None:
            self._cursor.close()
        self._cnx.rollback()
        
    def commit(self):
        print('---- Closing transaction')
        self._cursor.close()
        self._cnx.commit()
        
    def operator(self, id):
        cursor = self.cursor()
        sql = "SELECT ID FROM MATERUSERS.USER WHERE USERNAME = %s"
        cursor.execute(sql, (id,))
        record = cursor.fetchall()
        if len(record) == 1:
            self._user = record[0][0]
        cursor.close()

    def activityDone(self, idPart, actDef, start, notes = None, idoperator = None):
        ret = False
        sql = "SELECT ID FROM ACTIVITY WHERE IDPART = %s AND IDACTIVITY = %s AND START = %s "
        ptuple = (idPart, actDef, start)
        t = list(ptuple)
        if notes != None:
            sql += "AND NOTES = %s "
            t.append(notes)
        if idoperator != None:
            sql += "AND IDOPERATOR = %s"
            t.append(idoperator)
        ptuple = tuple(t)
        cursor = self.cursor()
        cursor.execute(sql, ptuple)
        record = cursor.fetchall()
        if len(record) == 1:
            ret = True
        cursor.close()
        return ret

    def charExists(self, idActivity, charDef):
        value = None
        sql = "SELECT ID, TABLE_NAME FROM CHARACTERISTIC_DEFINITION WHERE SHORTNAME = %s"
        cursor = self.cursor()
        cursor.execute(sql, (charDef,))
        record = cursor.fetchall()
        if len(record) == 1:
            if record[0][0] > 0:
                idChar = record[0][0]
                tblName = record[0][1]
                sql = "SELECT * FROM " + tblName + " WHERE IDACTIVITY = %s AND IDDEFINITION = %s"
                cursor.execute(sql, (idActivity, idChar,))
                rchar = cursor.fetchall()
                if len(rchar) > 0:
                    value = rchar[0][2]
        cursor.close()
        return value

    def chars(self, part, charName = None):
        ret = []
        cursor = self.cursor()
        sql = "SELECT DISTINCT TABLE_NAME FROM CHARACTERISTIC_DEFINITION WHERE IDPARTDEFINITION = "
        sql += "(SELECT IDDEFINITION FROM PART WHERE ID = %s)"
        ptuple = (part,)
        if charName != None:
            sql += " AND SHORTNAME = %s"
            l = list(ptuple)
            l.append(charName)
            ptuple = tuple(l)
        cursor.execute(sql, ptuple)
        record = cursor.fetchall()
        for r in record:
            tblName = r[0]
            sql = "SELECT CD.SHORTNAME, AD.SHORTDESCRIPTION, A.START, U.USERNAME, O.OUTCOME, "
            sql += "A.NOTES, T.*, CD.UNIT FROM " + tblName + " T JOIN ACTIVITY A ON "
            sql += "A.ID = T.IDACTIVITY JOIN ACTIVITY_DEFINITION AD ON AD.ID = A.IDACTIVITY JOIN "
            sql += "CHARACTERISTIC_DEFINITION CD ON CD.ID = T.IDDEFINITION JOIN "
            sql += "MATERUSERS.USER U ON U.ID = A.IDOPERATOR JOIN POSSIBLE_OUTCOMES O ON "
            sql += "O.ID = A.IDOUTCOME "
            ptuple = ()
            if charName != None:
                sql += "WHERE CD.SHORTNAME = %s "
                ptuple = (charName,)
            sql += "ORDER BY START DESC"
            cursor.execute(sql, ptuple)
            rValue = cursor.fetchall()
            ret.append(rValue)
        cursor.close()
        return ret
    
    def newLY(self, part, start = None, stop = None, notes = None, lyRaw = None,
              lyAbs = None, lyNorm = None, decayTime = None):
        self.startTransaction()

        actDef = self.__activityDefinition('LY evaluation', part = part)
        success = False
        if self.activityDone(part, actDef, start, notes = None):
            success = True
        else:
            success = self.__newActivity(part, 'LY evaluation', start, stop, notes)
        s1 = s2 = s3 = s4 = False
        if success:
            if lyRaw != None:
                s1 = self.__insertChar(part, 'lyRaw', lyRaw)
            if lyAbs != None:
                s2 = self.__insertChar(part, 'lyAbs', lyAbs)
            if lyNorm != None:
                s3 = self.__insertChar(part, 'lyNorm', lyNorm)
            if decayTime != None:
                s4 = self.__insertChar(part, 'decayTime', decayTime)
        if success and s1 and s2 and s3 and s4:
            self.commit()
        else:
            print('LY insertion failed for part {}'.format(part))
            print('   activity LY evaluation started on {} with notes {}'.format(start, notes))
            print('   lyRaw    : {}'.format(s1))
            print('   lyAbs    : {}'.format(s2))
            print('   lyNorm   : {}'.format(s3))
            print('   decayTime: {}'.format(s4))
            self.rollback()

    def newCrystalRegistration(self, partid, producer, reflector, wrapping, x, y, z):
        idReflector = {'None':1, 'ESR':2, 'BaSO_4':3}
        idWrapping = {'None':1, 'Al':2, 'Tyvek':3}
        if reflector in idReflector and wrapping in idWrapping:
            self.startTransaction()
            success = self.__insertPart(partid, 'Crystal', producer)
            if success:
                s1 = self.__newActivity(partid, 'Crystal registration')
                if s1:
                    s2 = self.__insertChar(partid, 'Array multiplicity', 1)
                    s3 = self.__insertChar(partid, 'Crystal type', 1) #LYSO
                    s4 = self.__insertChar(partid, 'Reflector', idReflector[reflector])
                    s5 = self.__insertChar(partid, 'Wrapping', idWrapping[wrapping])
                    s6 = self.__insertChar(partid, 'X', x)
                    s7 = self.__insertChar(partid, 'Y', y)
                    s8 = self.__insertChar(partid, 'Z', z)
            if success and s1 and s2 and s3 and s4 and s5 and s6 and s7 and s8:
                self.commit()
            else:
                self.rollback()
        else:
            if not reflector in idReflector:
                print('Cannot find {} among reflectors'.format(reflector))
            if not wrapping in idWrapping:
                print('Cannot find {} among wrapping'.format(wrapping))

    def __activityDefinition(self, name, partType = None, workflow = None, workflowVersion = None,
                             part = None):
        actDef = -1
        p = (name,)
        sql = "SELECT ID FROM ACTIVITY_DEFINITION WHERE SHORTDESCRIPTION = %s "
        if partType != None:
            sql += "AND IDPART_DEFINITION = (SELECT ID FROM PART_DEFINITION WHERE "
            sql += "SHORTDESCRIPTION = %s) "
            p = p + (partType,)
        elif part != None:
            sql += "AND IDPART_DEFINITION = (SELECT IDDEFINITION FROM PART WHERE ID = %s) "
            p = p + (part,)
        if workflow == None:
            sql += "AND IDWORKFLOW = (SELECT MAX(ID) FROM WORKFLOW)"
        else:
            sql += "AND IDWORKFLOW = (SELECT ID FROM WORKFLOW WHERE NAME = %s "
            p = p + (workflow,)
            if workflowVersion == None:
                sql += "ORDER BY VERSION DESC LIMIT 1)"
            else:
                sql += "AND VERSION = %s)"
                p = p + (workflowVersion,)
        self._cursor.execute(sql, p)
        record = self._cursor.fetchall()
        if len(record) == 1:
            actDef = record[0][0]
        return actDef
        
    def __newActivity(self, part, activity, start = None, stop = None, notes = None):
        ret = False
        # private method: there is a public method per concrete activity
        if self._user < 0:
            print('User not defined...please declare it first...')
            return ret
        actDef = self.__activityDefinition(activity, part = part)
        pattern = re.compile("^[0-9]+$")
        if start == None:
            start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif pattern.match(str(start)):
            start = datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S')
        if stop == None:
            stop = start
        elif pattern.match(str(stop)):
            stop = datetime.datetime.fromtimestamp(stop).strftime('%Y-%m-%d %H:%M:%S')
        if notes == None:
            notes = ''
        idoperator = self._user
        if self.activityDone(part, actDef, start, notes, idoperator) == False:
            sql = 'INSERT INTO ACTIVITY (IDPART, IDACTIVITY, START, STOP, IDOUTCOME, '
            sql += 'NOTES, IDOPERATOR) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            try:
                self._cursor.execute(sql, (part, actDef, start, stop, 1, notes, idoperator,))
                ret = True
            except mysql.connector.Error as error:
                print("Failed to insert record into ACTIVITY {}".format(error))
                print(sql)
                ret = False
        else:
            print('Activity {} for part {} already in DB'.format(activity, part))
        return ret

    def __charvalueExists(self, tablename, idAct, idDef, value):
        ret = False
        sql = 'SELECT * FROM {} WHERE IDACTIVITY = %s AND IDDEFINITION = %s AND VALUE = %s'.format(tablename)
        self._cursor.execute(sql, (idAct, idDef, value,))
        record = self._cursor.fetchall()
        if len(record) > 0:
            ret = True
        return ret

    def __insertChar(self, part, charName, charValue):
        # private method called by newActivity
        ret = False
        sql = 'SELECT ID, IDACTIVITYDEFINITION, TABLE_NAME FROM CHARACTERISTIC_DEFINITION '
        sql += 'WHERE SHORTNAME = %s'
        try:
            self._cursor.execute(sql, (charName,))
            record = self._cursor.fetchall()
            if len(record) == 1:
                idChar = record[0][0]
                actDef = record[0][1]
                table  = record[0][2]
                sql = "SELECT ID FROM ACTIVITY WHERE IDPART = %s AND IDACTIVITY = %s AND "
                sql += "IDOUTCOME = (SELECT ID FROM POSSIBLE_OUTCOMES WHERE OUTCOME = 'Success') " 
                sql += "ORDER BY START DESC LIMIT 1"
                self._cursor.execute(sql, (part,actDef,))
                record = self._cursor.fetchall()
                if len(record) == 1:                    
                    idAct = record[0][0]
                    sql = 'INSERT INTO {} VALUES (%s, %s, %s)'.format(table)
                    if not self.__charvalueExists(table, idAct, idChar, charValue):
                        self._cursor.execute(sql, (idAct,idChar,charValue,))
                    ret = True
        except mysql.connector.Error as error:
            print("Failed to insert characteristic {} for part {}: {}".format(charName, part, error))
            print(sql)
            ret = False
        return ret
            
    def __insertPart(self, id, type, model, location = 'Segre', service = 'None'):
        # private method: there is a public method per concrete part
        ret = False
        sql = 'INSERT INTO PART VALUES (%s, NULL, '
        sql += '(SELECT ID FROM PART_DEFINITION WHERE SHORTDESCRIPTION '
        sql += '= %s), (SELECT ID FROM LOCATION WHERE LOCATION = %s), (SELECT ID FROM SERVICE '
        sql += 'WHERE SERVICE = %s), (SELECT ID FROM MODEL WHERE NAME = %s), NULL, NULL, '
        sql += '(SELECT MAX(ID) FROM WORKFLOW))'
        try:
            cursor = self._cnx.cursor()
            cursor.execute(sql, (id, type, location, service, model,))
            ret = True
        except mysql.connector.Error as error:
            print("Failed to insert part {}: {}".format(id, error))
            print(sql)
            ret = False
        return ret

