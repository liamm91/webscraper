# code
it is a python based application which on startup, goes to youtube.com and searches for all the links within the current webpage and for every link parsed, the application spawns a new object which does the exact same process. It's a recursive program which relies on an API known as BeautifulSoup for formatting the tags.
for every link it obtains, it stores it in a database with the parent link attached. it also logs its process in a file for every website encountered, all logs and the database is stored in an auto-generated folder.
