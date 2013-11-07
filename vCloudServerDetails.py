import mysql.connector
from vCloudDeployVm import vCloud_Deploy
from vCloudLogger import vCloud_Logger

class vCloud_Instance(object):


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
		self.x		= vCloud_Logger()

	def get_servername(self):

		self.x.log(lvl='i',msg=("servername created and ready to use ...OK"))

		query = ("select max(id) from vcloud.vm_instances")
		self.cursor.execute(query)
		res = self.cursor.fetchall()

		for v in res:
  			for k in v:
				if k == None: k = 0
				vCloud_Instance.server_id   = k+1
				vCloud_Deploy.vm_name = "server-"+str(vCloud_Instance.server_id)
				vCloud_Instance.server_name = "server-"+str(vCloud_Instance.server_id)
    				return "server-"+str(vCloud_Instance.server_id)

	def update_server(self, vm_name, vm_href, vm_ip):

		self.x.log(lvl='i',msg=("server details updated in database ...OK"))

		query = ("INSERT INTO `vcloud`.`vm_instances` "
			"(`vm_name`, `vm_href`, `vm_ipaddress`) "
			"VALUES (%s, %s, %s)")
		value =	(vm_name, vm_href, vm_ip)

		self.cursor.execute(query, value)
		self.connection.commit()
		self.cursor.close()
		self.connection.close()
