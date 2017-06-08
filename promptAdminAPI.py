import cx_Oracle
import ldap
import json
import config
from flask import Flask

app = Flask(__name__)


def listCleaner(myList):
    cleanedList = []
    for item in myList:
        item = item.replace("(","")
        item = item.replace(")","")
        item = item.replace("\'","")
        item = item.replace(",","")
        cleanedList.append(item)
    return cleanedList

def establishDBConnection():

    #establishes connection to oid3
    from ldap3 import Server, Connection, ALL
    ldapconn = Connection('oid3.byu.edu',auto_bind=True)

    #searches ldap for the node that contains the connection string to the desired oracle DB
    ldapconn.search('dc=byu,dc=edu','(cn=CDRPRD)',attributes=['orclNetDescString'])

    #next few lines just strip away everything from the search results except for the desired connection string
    splitSearch = str(ldapconn.response[0]).split(",")
    desiredAttribute = splitSearch[4].split("\'")
    dbConnectionString = desiredAttribute[5]
    dbConnectionString = dbConnectionString.replace("\'","")
    dbConnectionString = dbConnectionString.replace("(FAILOVER_MODE=(TYPE=select)(METHOD=basic)(RETRIES=10)(DELAY=10))","")
    dbConnectionString = config.username+'/'+config.password+'@'+dbConnectionString
    #connects to oracle database
    #con = cx_Oracle.connect('ip_phone/iptelc00l@'+dbConnectionString)
    return dbConnectionString


@app.route("/getPrompts/<string:appId>")
def getPrompts(appId):
    establishDBConnection()
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()
    cur.execute('select AUTH_PIN from APPID_APPNAME where APP_ID ='+appId)
    results = []
    results.append(appId)
    for member in cur:
        results.append(str(member))

    cur.execute('select PROMPT_ID from APPID_PROMPTID where APP_ID ='+appId)
    for member in cur:
        results.append(str(member))
    cur.close()
    con.close()
    results = listCleaner(results)
    js = json.dumps(results)
    return js




if __name__ == "__main__":
    app.run()


