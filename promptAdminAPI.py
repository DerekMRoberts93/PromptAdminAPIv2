import cx_Oracle
import ldap
import json
import config
import xml.etree.ElementTree as ET
from flask import Flask
from flask import jsonify

app = Flask(__name__)


def generateSingleXML(myStr,tag):
    return "<"+tag+">"+myStr+"</"+tag+">"

def generateListXML(myList,tag1,tag2):
    xmlString = ""
    xmlString = "<"+tag1+">"
    for item in myList:
        xmlString = xmlString + "\n" + "<"+tag2+">"+item+"</"+tag2+">"

    xmlString = xmlString + "\n" + "</"+tag1+">"
    return xmlString

def stringCleaner(myString):
    myString = myString.replace("(","")
    myString = myString.replace(")","")
    myString = myString.replace("\'","")
    myString = myString.replace(",","")
    return myString

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
    #start connection to Oracle database
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()
    #return PIN from database that matches the entered app id
    cur.execute('select AUTH_PIN from APPID_APPNAME where APP_ID ='+appId)

    #grabs pin form sql query result
    pin = ""
    for item in cur:
        pin = str(item)
    pin = stringCleaner(pin)

    #query to grab all prompt ids associated with the app id
    cur.execute('select PROMPT_ID from APPID_PROMPTID where APP_ID ='+appId)
    prompts = []
    for member in cur:
        prompts.append(str(member))
    #close oracle connections
    cur.close()
    con.close()
    prompts = listCleaner(prompts)

    #generate xml file
    promptsXml = generateListXML(prompts,"prompts","prompt")
    appIdXml = generateSingleXML(appId,"appID")
    pinXml = generateSingleXML(pin,"pin")
    responseXml = "<getPrompts>\n" + appIdXml + "\n" + pinXml + "\n" + promptsXml + "\n</getprompts>"
    return responseXml

@app.route("/changePin/<string:appId>/<string:newPin>")
def changePin(appId,newPin):
    #start oracle connection
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()

    #query to set pin
    query = 'UPDATE APPID_APPNAME SET AUTH_PIN = '+newPin+' WHERE APP_ID ='+appId
    cur.execute(query)
    con.commit()

    #close oracle connections
    cur.close()
    con.close()

    return generateSingleXML("success","response")



@app.route("/addPrompt/<string:appId>/<string:promptId>/<string:promptName>")
def addPrompt(appId,promptId,promptName):
    #start oracle connection
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()

    #query to add new prompt
    named_params = {'app':appId, 'prompt':promptId, 'name':promptName}
    query = 'INSERT INTO APPID_PROMPTID (APP_ID,PROMPT_ID,DESCRIPTION) VALUES (:app, :prompt, :name)'
    cur.execute(query, named_params)
    con.commit()

    #close connections
    cur.close()
    con.close()

    return generateSingleXML("success","response")


@app.route("/changeGroupName/<string:appId>/<string:groupName>")
def changeGroupName(appId,groupName):
    #start oracle connection
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()

    #query to change group name
    named_params = {'newName':groupName}
    query = 'UPDATE APPID_APPNAME SET APP_NAME =:newName WHERE APP_ID ='+appId
    cur.execute(query,named_params)
    con.commit()

    #close oracle connections
    cur.close()
    con.close()

    return generateSingleXML("success","response")

@app.route("/setFc/<string:appId>/<string:boolean>")
def setFc(appId,boolean):
    #start oracle connection
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()

    #query to update fc
    named_params = {'boolVal':boolean}
    query = 'UPDATE FCFO_STATUS SET FORCE_CLOSE =:boolVal WHERE APP_ID = '+appId
    cur.execute(query,named_params)
    con.commit()

    #close oracle connections
    cur.close()
    con.close()

    return generateSingleXML("success","response")

@app.route("/setFo/<string:appId>/<string:boolean>")
def setFo(appId,boolean):
    #start oracle connection
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()

    #query to update fc
    named_params = {'boolVal':boolean}
    query = 'UPDATE FCFO_STATUS SET FORCE_OPEN =:boolVal WHERE APP_ID = '+appId
    cur.execute(query,named_params)
    con.commit()

    #close oracle connections
    cur.close()
    con.close()

    return generateSingleXML("success","response")



@app.route("/addApp/<string:appId>/<string:groupName>/<string:promptId>/<string:promptName>/<string:pin>")
def addApp(appId,groupName,promptId,promptName,pin):
    #start oracle connection
    con = cx_Oracle.connect(establishDBConnection())
    cur = con.cursor()

    #query to create new user
    named_params = {'app':appId, 'group':groupName, 'promptIdent':promptId, 'prompt':promptName, 'pinNumber':pin, 'boolVal':'false'}
    query = 'INSERT INTO APPID_APPNAME (APP_ID, APP_NAME,AUTH_PIN) VALUES (:app,:group,:pinNumber)'
    cur.execute(query,named_params)
    con.commit()
    query = 'INSERT INTO APPID_PROMPTID (APP_ID, PROMPT_ID, DESCRIPTION) VALUES (:app,:promptIdent,:prompt)'
    cur.execute(query,named_params)
    con.commit()
    query = 'INSERT INTO FCFO_STATUS (APP_ID, FORCE_CLOSE, FORCE_OPEN) VALUES (:app,:boolVal,:boolVal)'
    con.execute(query,named_params)
    con.commit()

    #close connections
    cur.close()
    con.close()

    return generateSingleXML("success","response")



if  __name__ == "__main__":
    app.run(host='0.0.0.0')

