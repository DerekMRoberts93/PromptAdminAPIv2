# New Prompt Admin API built in python

## Dependencies

### Python Dependencies:
1. Flask
2. Django
3.cx_Oracle
4.ldap3 (should already be installed)
5. make sure a config.py file is created containing the username and password for the oracle db.
your config.py file should look as follows:
    username = **********
    password =  *********
(be sure to replace stars with actual username and password)

all python dependencies should be installed using pip. If unavailable get a system admin to install it on the desired server. Additionally, the servers this will be implemented on
will most likely run python 2.6. because of this make sure you use pip to install the correct version. a quick google search will explain how to use pip and select
specific version numbers in detail

### Additional dependencies
(you should only check these if the initial deployment fails. they should already be installed on the target server)

1. Oracle Instant Client (necessary to connect to any oracle DB)


## Notes on cx_Oracle module:
due to the fact that the oracle database moves periodically, its location is tracked through LDAP. I created a function called establishDBConnection that queries the appropriate LDAP server and
returns the connection string need for cx_Oracle to establish a connection with the data base.

The cursor object in the cx_Oracle module is what allows you to run queries against the data base. A few things tonote about the cursor object:
1. it essentially returns a list of strings that you will need to loop through and clean up. For this reason I created my cleaning functions to remove 
all the extra characters returned from the query. Additionally, you can't access the query results directly from the cursor object using indices. you have to split it up
into your own list using a for loop. See code for more details

2. passing parameters directly to the query in the cursor object is not a good idea. The cursor object tends to make everything uppercase and causes problems with
anything that isn't a number. For this reason, you should pass all parameters to a dictionary and then access them through the dictionary in your queries in order
to preserve formattig and avoid unintended errors. this can be done in the following manner:
```
@app.route(/getPrompt/<string:appId>)
def getPrompt(appId):
    #basic connection setup
    con = cx_Oracle.connect(EstablishDBConnection())
    cur = con.cursor()
    #pass parameter to dictionary
    named_params = {'app':appId}
    #create query referencing the dictionary. this is done by putting a colon followed by the name given in the distionary
    query = 'SELECT * FROM FCFO_STATUS WHERE APP_ID =:app'
    #finally we must pass in the query and dictionary to the cursor.execute() function for it to behave properly
    cur.execute(query,named_params)
```

## Documentation(basic):
[get] getPrompts
route: /getPrompts/appID (example: /getPrompts/22222)
takes: five digit appId
returns: appId, pin, and associated prompts for the given appId in XML format

[get] returnEverything
route: /returnEverything (example: /returnEverything)
takes: nothing
returns: all apps, prompts, pins, fcfo statuses in XML format (essentially returns all DB info)


[put] changePin
route: /changePin/appId/newPin (example: /changePin/22222/456789)
takes: 5-digit appId and 6-digit pin
returns: success or failure in XML format

[put] changeGroupName
route: /changeGroupName (example: /changeGroupName/22222/myNewGroup)
takes:  5-digit appId and a new groupName
returns: success or failure in XML format

[put] setFc
route: /setFc/appId/bool (example: /setFc/22222/true)
takes: 5-digit app id and the string 'true' or 'false'
returns: success or failure in XML format

[put] setFo
route: /setFo/appId/bool (example: /setFo/22222/true)
takes: 5-digit appId and the string 'true' or 'false'
returns: success or failure in XML format


[post] addApp
route: /addApp/appId/groupName/promptId/promptName/pin
takes: 5-digit appId, groupname, 5-digit promptId, promptName, and 6-digit pin (promptId and appId must be unique from all other entries)
returns: success or failure in XML format

[post] addPrompt
route: /addPrompt/appId/newPromptId/promptName (example: /addPrompt/22222/96369/newPrompt)
takes: 5-digit appId (from an existing app) and a 5-digit promptId as well as a new prompt name
returns: success or failure in xml


[delete] deleteApp
route: /deleteApp/appId (example: /deleteApp/22222)
takes: 5-digit appId
returns: success or failure in XML format

[delete] deletePrompt
route: /deletePrompt/promptId (example: /deletePrompt/96369)
takes: 5-digit promptId
returns: success or failure in XML format
