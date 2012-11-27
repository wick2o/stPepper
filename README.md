stPepper
========

stPepper: Distributed Tasks

    My attempt at a framework for completing large amount of tasks with help from
	multiple people. This program is released as is.

    Depenancies:
		Client: poster
		Server: bottle, sqlite3
		
Example Client Usage:
=====================

> Complete Single task

    ./client.py -s [SERVER IP] -u [USERNAME] -t [NUMBER OF THREADS]  

> Complete Multiple tasks

    ./client.py -s [SERVER IP] -u [USERNAME] -t [NUMBER OF THREADS] -m [NUMBER OF TASKS]

Example Server Usage:
=====================

> Server Startup

	./webby.py -i 0.0.0.0 -p 80

