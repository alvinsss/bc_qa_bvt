#coding:utf-8
import pymysql
import config

datains = config.basedata()
MYSQL_HOST=datains.MYSQL_HOST
MYSQL_USER=datains.MYSQL_USER
MYSQL_PWD=datains.MYSQL_PWD
MYSQL_DB=datains.MYSQL_DB
MYSQL_PORT=datains.MYSQL_PORT

def createConn():
    try:
        coon = pymysql.connect(user=MYSQL_USER,
                               passwd=MYSQL_PWD,
                               db=MYSQL_DB,
                               port=MYSQL_PORT,
                               host=MYSQL_HOST,
                               charset='utf8'
                               )
        return coon
    except Exception as e:
        print (e)
        raise Exception(e)
    pass

class Sql():
    def __init__(self,conn=None,close=True):
        self.close=close
        if not conn:
            self._db_conn=createConn()
        else:
            self._db_conn=conn
            
    def closedb(self):
        if self._db_conn:
            try:
                self._db_conn.close()
            except:pass
            
    def update(self,sql,param=None):
        cursor = None
        data = None
        try:
            cursor = self._db_conn.cursor()
            cursor.execute(sql, param)
            self._db_conn.commit()
        except Exception as e:
            print (e)
            raise Exception(e)
        finally:
            if cursor:
                cursor.close()
            if self.close and self._db_conn:
                try:
                    self._db_conn.close()
                except:pass
            return True
        
    def query(self,sql, param=None):
        cursor = None
        data = None
        try:
            cursor = self._db_conn.cursor()
            cursor.execute(sql, param)
            data=cursor.fetchall()
        except Exception as e:
            raise Exception(e)
        finally:
            if cursor:
                cursor.close()
            if self.close and self._db_conn:
                try:
                    self._db_conn.close()
                except:pass
            return data

if __name__ == "__main__":
    print("done!")