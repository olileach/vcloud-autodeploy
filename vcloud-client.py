import sys
from vCloudServerDetails import vCloud_Instance
from vCloudDeployVm import vCloud_Deploy 
from vCloudLogger import vCloud_Logger

x = vCloud_Deploy()
y = vCloud_Instance()
z = vCloud_Logger()

vCloud_Logger.filename = sys.argv[1]

# set api credentials and endpoint

username 	= ''
org      	= ''
password 	= ''
key      	= ''
secret   	= ''
endpoint 	= ''

# set servername for virtual machine

z.log(lvl='i',msg=("need to set servername for vCloud virtual machine"))
y.get_servername()

# login to vCloud

z.log(lvl='i',msg=("need to log in to vcloud to get session headers"))
x.sessions(username, org, password, key, secret, endpoint)

# Deploy VM and with template values - puppet-win-2008r2 or puppet-centos-6x

z.log(lvl='i',msg=("need to deploy virtual machines from vapp template"))
x.vapp_templates(template_name = 'puppet-centos-6')
x.vapps(vapp_name = 'ol-vapp-04')

# insert the virtual machine details in to the vCloud vm_instance database

z.log(lvl='i',msg=("need to update virtual machine name"))
y.update_server(vm_name=vCloud_Deploy.vm_name, vm_href=vCloud_Deploy.vm_href, vm_ip=vCloud_Deploy.vm_ip)

# return exit value 

sys.stdout.write(vCloud_Deploy.vm_ip)
sys.stdout.flush()
sys.exit(0)
