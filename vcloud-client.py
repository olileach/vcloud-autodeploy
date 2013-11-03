from vCloudServerDetails import vCloud_instance
from vCloudDeployVm import vCloud_Lookup 

x = vCloud_Lookup()
y = vCloud_instance()

# set api credentials and endpoint

username 	= ''
org      	= ''
password 	= ''
key      	= ''
secret   	= ''
endpoint 	= ''

# set servername for virtual machine

servername = y.get_servername()
vCloud_Lookup.vm_name = servername

# login to vCloud 

x.sessions(username, org, password, key, secret, endpoint)
x.org_url()

# template values are puppet-win-2008r2 or puppet-centos-6x

x.vapp_templates(template_name = 'puppet-centos-6x')
x.vapps(vapp_name = 'ol-vapp-04')
x.recompose_vapp()

# insert the virtual machine details in to the vCloud vm_instance database 

y.update_server(vm_name=vCloud_Lookup.vm_name, vm_href=vCloud_Lookup.vm_href, vm_ip=vCloud_Lookup.vm_ip)
