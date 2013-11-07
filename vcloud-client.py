import sys
from vCloudServerDetails import vCloud_Instance
from vCloudDeployVm import vCloud_Lookup 
from vCloudLogger import vCloud_Logger

x = vCloud_Lookup()
y = vCloud_Instance()
z = vCloud_Logger()


vCloud_Logger.filename = sys.argv[1]


# set api credentials and endpoint

username 	= 'oliver.api'
org      	= 'SymphonyVPDCDemo2'
password 	= 'A12345'
key      	= 'l7xxd3a1965751154a0fae7373bd79628ffb'
secret   	= '5a8eeb6ef18947bea5451130d5a35012'
endpoint 	= 'https://api.savvis.net/clouddatacenter/vcloud/de-central-1/'

# set servername for virtual machine

z.log(lvl='c',msg=("setting servername for vCloud virtual machine"))
y.get_servername()

# login to vCloud 

x.sessions(username, org, password, key, secret, endpoint)

# Deploy VM and with template values - puppet-win-2008r2 or puppet-centos-6x

x.vapp_templates(template_name = 'puppet-centos-6x')
x.vapps(vapp_name = 'ol-vapp-04')

# insert the virtual machine details in to the vCloud vm_instance database 

y.update_server(vm_name=vCloud_Lookup.vm_name, vm_href=vCloud_Lookup.vm_href, vm_ip=vCloud_Lookup.vm_ip)

# return exit value 

sys.stdout.write(vCloud_Lookup.vm_ip)
sys.stdout.flush()
sys.exit(0)
