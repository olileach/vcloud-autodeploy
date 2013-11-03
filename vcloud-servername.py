import mysql.connector

class Servername():

	def __init__(self):

		self.config 	={
  				'user': '',
  				'password': '',
  				'host': '127.0.0.1',
  				'database': 'vcloud',
  				'raise_on_warnings': True,
				}


		self.connection = mysql.connector.connect(**self.config)
		self.cursor 	= self.connection.cursor()

	def getid(self):

		query = ("select max(id) from vcloud.vm_instances")
		self.cursor.execute(query)
		res = self.cursor.fetchall()
		self.connection.close()

		for v in res:
  			for k in v:
    				return "server-"+str(k)

x = Servername()
print x.getid()
