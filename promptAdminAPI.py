import cx_Oracle
import ldap
import json
import config
import xml.etree.ElementTree as ET
from flask import Flask
from flask import jsonify

app = Flask(__name__)




def generateNestedListXML(myList):
    xmlResponse = []
    count = 1
    for item in myList:
        xmlString = ""
        xmlString = xmlString + "<appdata>\n"
        xmlString = xmlString + "\t<appid>"+item[0]+"</appid>\n\t<appname>"+item[1]+"</appname>\n\t<pin>"+item[2]+"</pin>\n\t<forceclose>"+item[3]+"</forceclose>\n\t<forceopen>"+item[4]+"</forceopen>\n"
        xmlString = xmlString + "</appdata>\n"
        xmlResponse.append(xmlString)


    return xmlResponse

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

    try:
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
    except:
        return generateSingleXML("failure","response")

@app.route("/changePin/<string:appId>/<string:newPin>")
def changePin(appId,newPin):
    try:
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
    except:
        return generateSingleXML("failure","response")


@app.route("/addPrompt/<string:appId>/<string:promptId>/<string:promptName>")
def addPrompt(appId,promptId,promptName):
    try:
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
    except:
        return generateSingleXML("failure", "response")

@app.route("/changeGroupName/<string:appId>/<string:groupName>")
def changeGroupName(appId,groupName):
    try:
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
    except:
        return generateSingleXML("failure","response")

@app.route("/setFc/<string:appId>/<string:boolean>")
def setFc(appId,boolean):
    try:
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
    except:
        return generateSingleXML("failure","response")

@app.route("/setFo/<string:appId>/<string:boolean>")
def setFo(appId,boolean):
    try:
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
    except:
        return generateSingleXML("success","response")



@app.route("/addApp/<string:appId>/<string:groupName>/<string:promptId>/<string:promptName>/<string:pin>")
def addApp(appId,groupName,promptId,promptName,pin):
    try:
        #start oracle connection
        con = cx_Oracle.connect(establishDBConnection())
        cur = con.cursor()

        #query to create new user
        named_params = {'app':appId, 'groupN':groupName, 'pinNumber':pin}
        query = 'INSERT INTO APPID_APPNAME (APP_ID, APP_NAME,AUTH_PIN) VALUES (:app, :groupN, :pinNumber)'
        cur.execute(query,named_params)

        named_params_two = {'appID':appId, 'promptIdent':promptId, 'prompt':promptName}
        query = 'INSERT INTO APPID_PROMPTID (APP_ID, PROMPT_ID, DESCRIPTION) VALUES (:appID, :promptIdent, :prompt)'
        cur.execute(query,named_params_two)

        named_params_three = {'application':appId, 'boolVal':'false'}
        query = 'INSERT INTO FCFO_STATUS (APP_ID, FORCE_CLOSE, FORCE_OPEN) VALUES (:application, :boolVal, :boolVal)'
        cur.execute(query,named_params_three)
        con.commit()

        #close connections
        cur.close()
        con.close()

        return generateSingleXML("success","response")
    except:
        return generateSingleXML("failure","response")


@app.route("/returnAll")
def returnAll():
    try:
        #start oracle connection
        con = cx_Oracle.connect(establishDBConnection())
        cur = con.cursor()

        #query to natural join FCFO_STATUS and APPID_APPNAME
        query = ('SELECT * FROM APPID_APPNAME NATURAL JOIN FCFO_STATUS')
        cur.execute(query)
        applications = []
        for app in cur:
            temp = str(app).split(",")
            temp =  listCleaner(temp)
            applications.append(temp)

        #query to retrieve prompts for each app
        appDataXml = generateNestedListXML(applications)
        promptDataXml = []
        for app in applications:
            promptQuery = 'SELECT PROMPT_ID, DESCRIPTION FROM APPID_PROMPTID WHERE APP_ID = '+app[0]
            cur.execute(promptQuery)
            promptXml = "<prompts>\n"
            for item in cur:
                temp = str(item).split(",")
                temp = listCleaner(temp)
                promptXml = promptXml + "\t<prompt>\n\t\t<promptid>"+temp[0]+"</promptid>\n\t\t<promptname>"+temp[1]+"</promptname>\n\t</prompt>\n"
            promptXml = promptXml + "</prompts>\n"
            promptDataXml.append(promptXml)

        #merge xml for app and prompt data
        combinedXml = "<data>\n"
        for app, prompt in zip(appDataXml,promptDataXml):
            combinedXml = combinedXml +"<appobject>\n"+ app + prompt +"</appobject>\n"
        combinedXml = combinedXml + "</data>\n"


        #close connections
        cur.close()
        con.close()

        return combinedXml
    except:
        return generateSingleXML("failure","response")



@app.route("/deletePrompt/<string:promptId>")
def promptId(promptId):
    try:
        #connect to oracle
        con = cx_Oracle.connect(establishDBConnection())
        cur = con.cursor()

        #query to delete prompt
        named_params = {'id':promptId}
        query = 'DELETE FROM APPID_PROMPTID WHERE PROMPT_ID =:id'
        cur.execute(query,named_params)
        con.commit()


        #end connections
        cur.close()
        con.close()
        return generateSingleXML("success","response")
    except:
        return generateSingleXML("failure","response")




@app.route("/deleteApp/<string:appId>")
def deleteApp(appId):
    try:
        #connect to oracle
        con = cx_Oracle.connect(establishDBConnection())
        cur = con.cursor()

        #queries to delete
        named_params = {'app':appId}
        query = 'DELETE FROM APPID_APPNAME WHERE APP_ID =:app'
        cur.execute(query, named_params)

        query = 'DELETE FROM FCFO_STATUS WHERE APP_ID =:app'
        cur.execute(query,named_params)

        query = 'DELETE FROM APPID_PROMPTID WHERE APP_ID =:app'
        cur.execute(query,named_params)
        con.commit()


        #end connections
        cur.close()
        con.close()

        return generateSingleXML("success","response")
    except:
        return generateSingleXML("failure","response")




if  __name__ == "__main__":
    app.run(host='0.0.0.0')


