import mysql.connector

class vCloud_instance(object):


	server_name 	= None
	server_id 	= None

	def __init__(self):

		self.config 	={
  				'user': 'python_dba',
  				'password': 'F00f1ght3r$',
  				'host': '127.0.0.1',
  				'database': 'vcloud',
  				'raise_on_warnings': True,
				}


		self.connection = mysql.connector.connect(**self.config)
		self.cursor 	= self.connection.cursor()
		self.server_id	= None

	def get_servername(self):

		query = ("select max(id) from vcloud.vm_instances")
		self.cursor.execute(query)
		res = self.cursor.fetchall()
		self.connection.close()

		for v in res:
  			for k in v:
				if k == None: k = 0
				self.server_id   = k+1
				self.server_name = "server-"+str(self.server_id)
    				return "server-"+str(self.server_id)

	def update_server(self, vm_name, vm_href, vm_ip):

		#cnx = mysql.connector.connect(user='python_dba', database='vcloud', host='127.0.0.1', password='F00f1ght3r$')
		#cursor = cnx.cursor()

		query = ("INSERT INTO `vcloud`.`vm_instances` "
			"(`vm_name`, `vm_href`, `vm_ipaddress`) "
			"VALUES (%s, %s, %s)")
		value =	(vm_name, vm_href, vm_ip)

		self.cursor.execute(query, value)
		self.connection.commit()
		self.cursor.close()
		self.connection.close()

