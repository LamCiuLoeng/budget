import cx_Oracle, os, traceback
from tg import config
os.environ["NLS_LANG"] = "american_america.al32utf8"

#Create the Oracle connection 
def createConnection():
    connstr = config.oracle_connection_str
    return cx_Oracle.connect(connstr)

def executeSearchSQL(dbconnection, sql, params, all=True, wrap=False):
    cursor = dbconnection.cursor()
    cursor.prepare(str(sql))
    cursor.execute(None, params)
    if all:
        if wrap:
            return [dtoWrap(cursor, row) for row in cursor.fetchall()]
        else:
            return cursor.fetchall()
    else:
        if wrap:
            return dtoWrap(cursor, cursor.fetchone())
        else:
            return cursor.fetchone()

def searchOracle(sql, params, all=True, wrap=False):
    dbconn = createConnection()
    try:
        return executeSearchSQL(dbconn, sql, params, all, wrap)
    except:
        traceback.print_exc()
        return None
    finally:
        dbconn.close()

class oracleDTO(dict):
    """A dictionary that provides attribute-style access."""

    def __getitem__(self, key):
        return  dict.__getitem__(self, key)

    def __getattr__(self, name):
        return self[name]

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

def dtoWrap(cursor, row):
    dto = oracleDTO()
    for index, item in enumerate(cursor.description):
        dto[item[0]] = row[index]
    return dto      

if __name__ == "__main__":
    dto = oracleDTO()
    dto.aa = "aa1"
    print dto['aa']
    print dto.aa
