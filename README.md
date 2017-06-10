New Prompt Admin API built in python

Python Dependencies:
1. Flask
2. Django
3.cx_Oracle
4.ldap (should already be installed)
5. make sure a config.py file is created containing the username and password for the oracle db.
your config.py file should look as follows:
    username = **********
    password =  *********
(be sure to replace stars with actual username and password)

all python dependencies should be installed using pip. If unavailable get a system admin to install it on the desired server. Additionally, the servers this will be implemented on
will most likely run python 2.6. because of this make sure you use pip to install the correct version. a quick google search will explain how to use pip and select
specific version numbers in detail

Additional dependencies (you should only check these if the initial deployment fails. they should already be installed on the target server)
1. Oracle Instant Client (necessary to connect to any oracle DB)


Documentation:
(coming soon)
