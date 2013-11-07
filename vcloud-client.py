import sys
from vCloudServerDetails import vCloud_Instance
from vCloudDeployVm import vCloud_Lookup 
from vCloudLogger import vCloud_Logger

x = vCloud_Lookup()
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

z.log(lvl='i',msg=("setting servername for vCloud virtual machine"))
y.get_servername()

# login to vCloud 

z.log(lvl='i',msg=("logging in to vcloud to get session headers"))
x.sessions(username, org, password, key, secret, endpoint)

# Deploy VM and with template values - puppet-win-2008r2 or puppet-centos-6x

z.log(lvl='i',msg=("deploying virtual machines from vapp template"))
x.vapp_templates(template_name = 'puppet-centos-6x')
x.vapps(vapp_name = 'ol-vapp-04')

# insert the virtual machine details in to the vCloud vm_instance database 

z.log(lvl='i',msg=("updating virtual machine name"))
y.update_server(vm_name=vCloud_Lookup.vm_name, vm_href=vCloud_Lookup.vm_href, vm_ip=vCloud_Lookup.vm_ip)

# return exit value 

sys.stdout.write(vCloud_Lookup.vm_ip)
sys.stdout.flush()
sys.exit(0)
