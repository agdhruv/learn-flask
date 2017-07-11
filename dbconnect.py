import MySQLdb

# start your mySQL server, else connection will fail
# $ mysql.server start
# $ mysql -u root -p
# then enter password, and your server is running!

def connection():
	conn = MySQLdb.connect(host="localhost", user="root", passwd="something", db="learn_flask")

	c = conn.cursor()

	return c, conn