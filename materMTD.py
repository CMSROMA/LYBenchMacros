import mysql.connector
import datetime
import re

class MaterMtd:
    _username = ''
    _password = ''
    _host     = ''
    _user     = -1
    _cnx      = None

    def __init__(self, user = 'mater', password = 'materpassword',
                 host = 'localhost'):
        self.setup(user, password, host)

    def setup(self, user, password, host):
        self._username = user
        self._password = password
        self._host = host
        self.connect()

    def connect(self):
        try:
            self._cnx = mysql.connector.connect(user=self._username, password=self._password,
                                                host=self._host, database='mtd', use_pure = True,
                                                charset='utf8')
        except mysql.connector.Error as err:
            print(err.msg)

    def connected(self):
        if self._cnx == None:
            return False
        else:
            return True

    def operator(self, id):
        sql = "SELECT ID FROM MATERUSERS.USER WHERE USERNAME = %s"
        cursor = self._cnx.cursor(buffered=True)
        cursor.execute(sql, (id,))
        record = cursor.fetchall()
        if len(record) == 1:
            self._user = record[0][0]
        
    def newActivity(self, part, activity, start = None, stop = None, notes = None):
        if self._user < 0:
            print('User not defined...please declare it first...')
            return -1
        actDef = -1
        sql = "SELECT ID FROM ACTIVITY_DEFINITION WHERE SHORTDESCRIPTION = %s"
        cursor = self._cnx.cursor(buffered=True)
        cursor.execute(sql, (activity,))
        record = cursor.fetchall()
        if len(record) == 1:
            actDef = record[0][0]
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
        sql = 'INSERT INTO ACTIVITY (IDPART, IDACTIVITY, START, STOP, IDOUTCOME, '
        sql += 'NOTES, IDOPERATOR) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        try:
            cursor = self._cnx.cursor()
            cursor.execute(sql, (part, actDef, start, stop, 1, notes, idoperator,))
            self._cnx.commit()
            cursor.close()
        except mysql.connector.Error as error:
            print("Failed to insert record into ACTIVITY {}".format(error))
            print(sql)

    def insertChar(self, part, charName, charValue):
        # only single valued chars support by now
        sql = 'SELECT ID, IDACTIVITYDEFINITION, TABLE_NAME FROM CHARACTERISTIC_DEFINITION '
        sql += 'WHERE SHORTNAME = %s'
        try:
            cursor = self._cnx.cursor()
            cursor.execute(sql, (charName,))
            record = cursor.fetchall()
            if len(record) == 1:
                idChar = record[0][0]
                actDef = record[0][1]
                table  = record[0][2]
                sql = "SELECT ID FROM ACTIVITY WHERE IDPART = %s AND IDACTIVITY = %s AND "
                sql += "IDOUTCOME = (SELECT ID FROM POSSIBLE_OUTCOMES WHERE OUTCOME = 'Success') " 
                sql += "ORDER BY START DESC LIMIT 1"
                cursor.execute(sql, (part,actDef,))
                record = cursor.fetchall()
                if len(record) == 1:                    
                    idAct = record[0][0]
                    sql = 'INSERT INTO {} VALUES (%s, %s, %s)'.format(table)
                    cursor.execute(sql, (idAct,idChar,charValue,))
                    self._cnx.commit()
                    cursor.close()
                else:
                    print("Failed to insert characteristic {} for part {}: IDPART not found".format(charName, part))
            else:
                print("Failed to insert characteristic {} for part {}: CHARACTERISTIC not found".format(charName, part))

        except mysql.connector.Error as error:
            print("Failed to insert characteristic {} for part {}: {}".format(charName, part, error))
            print(sql)
            
    def newLY(self, part, lyRaw = None, lyAbs = None, lyNorm = None, decayTime = None):
        if lyRaw != None:
            self.insertChar(part, 'lyRaw', lyRaw)
        if lyAbs != None:
            self.insertChar(part, 'lyAbs', lyAbs)
        if lyNorm != None:
            self.insertChar(part, 'lyNorm', lyNorm)
        if decayTime != None:
            self.insertChar(part, 'decayTime', decayTime)
