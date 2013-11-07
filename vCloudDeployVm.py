import base64
import requests
import xml.etree.ElementTree as ET
import time
from vCloudLogger import vCloud_Logger


class vCloud_Deploy(object):

	vm_name 	= None
	vm_ip		= None
	vm_href		= None
	vm_temp_name 	= None

        def __init__(self):

                self.login = None
                self.headers = None
                self.endpoint = None
                self.org = None
                self.root = None
                self.vapp_template = None
                self.vapp = None
		self.x = vCloud_Logger()

        def sessions(self, username, org, password, key, secret, endpoint):

		self.endpoint = endpoint

                self.login = {'Accept':'application/*+xml;version=5.1', \
                           'Authorization':'Basic  '+ base64.b64encode(username + "@" + org + ":" + password), \
                           'x-id-sec':base64.b64encode(key + ":" + secret)}

                p = requests.post(self.endpoint + 'sessions', headers = self.login)

                self.headers = {'Accept':'application/*+xml;version=5.1'}

                for k,v in p.headers.iteritems():
                        if k == 'x-json':
                                access_token_value = 'Bearer %s' % v[21:57]
                                self.headers["Authorization:"]=access_token_value
                        if k == "x-vcloud-authorization" : self.headers[k]=v

		self.org_url()
		self.x.log(lvl='i',msg=("session headers created ...OK"))

        def org_url(self):

                g = requests.get(self.endpoint + 'org', data=None, headers = self.headers)
                root = ET.fromstring(g.content)

                for child in root:

                        self.org = child.get("href")

                g = requests.get(self.org, data=None, headers = self.headers)
                self.root = ET.fromstring(g.content)

                return self.org

        def vapp_templates(self, template_name):

		vCloud_Deploy.vm_temp_name = template_name 
                r = requests.get(self.endpoint + '/vAppTemplates/query',headers = self.headers)
                root = ET.fromstring(r.content)

                for child in root:
                        if child.tag == ('''{http://www.vmware.com/vcloud/v1.5}VAppTemplateRecord'''):
                                for k,v in child.attrib.iteritems():
                                        if v == template_name : self.vapp_template = child.attrib['href']

                self.x.log(lvl='i',msg=("vapp template variables set ...OK"))

        def vapps(self, vapp_name):

                r = requests.get(self.endpoint + '/vApps/query',headers = self.headers)
                root = ET.fromstring(r.content)

                for child in root:

                        if child.tag == ('''{http://www.vmware.com/vcloud/v1.5}VAppRecord'''):
                                for k,v in child.attrib.iteritems():
                                        if v == vapp_name : self.vapp = child.attrib['href']

		self.recompose_vapp()

        def recompose_vapp(self):

                post_headers = self.headers
                post_headers['Content-Type']='application/vnd.vmware.vcloud.recomposeVAppParams+xml'

                xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                        <RecomposeVAppParams
                        xmlns="http://www.vmware.com/vcloud/v1.5"
                        xmlns:ns2="http://schemas.dmtf.org/ovf/envelope/1"
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1"
                        xmlns:environment_1="http://schemas.dmtf.org/ovf/environment/1">
                        <Description> "api deployed vm to ol-vapp-04" </Description>
                            <SourcedItem sourceDelete="false">
                                <Source href="%s"/>
                            </SourcedItem>
                        <AllEULAsAccepted>true</AllEULAsAccepted>
                        </RecomposeVAppParams>""" % (self.vapp_template)

                post = requests.post(self.vapp + '/action/recomposeVApp', data=xml, headers=post_headers)
                result = ET.fromstring(post.text)

		self.x.log(lvl='i',msg=("recomposed vapp ...OK"))

                self.task_progress(task_id=result.attrib['id'])

        def task_progress(self, task_id):

                task_id_href = None

                for child in self.root:

                        if child.get('type') == 'application/vnd.vmware.vcloud.tasksList+xml':

                                r = requests.get(child.get('href'),headers = self.headers)
                                root = ET.fromstring(r.content)

                                for child in root:
                                        for k,v in child.attrib.iteritems():

                                                if k == 'id' and v == task_id:
                                                        task_id_href = child.attrib['href']

                x = 0
                
		self.x.log(lvl='i',msg=("checking progress of deployed vm ...OK"))

		while x == 0:

                        time.sleep(5)
                        g = requests.get(task_id_href, headers = self.headers)
                        root = ET.fromstring(g.content)

                        for child in root.iter():

                                tag = child.tag
                                tag = tag.replace("{http://www.vmware.com/vcloud/v1.5}","")
                                if tag == 'Progress' :

                                        if child.text == '100' : x = 1

                time.sleep(15)
                self.query_vms()


        def query_vms(self):

                r = requests.get(self.endpoint + 'vms/query', headers = self.headers)
                root = ET.fromstring(r.content)

		self.x.log(lvl='i',msg=("checking for vm name ...OK"))

                for child in root:

                        if child.tag == ('''{http://www.vmware.com/vcloud/v1.5}VMRecord'''):
                                for k,v in child.attrib.iteritems():
                                        if v == vCloud_Deploy.vm_temp_name:
                                                for k,v in child.attrib.iteritems():
                                                        if k == "href" and 'vAppTemplate' not in v :
								vCloud_Deploy.vm_href = v
                                                                self.update_name()

        def update_name(self):

                #minorErrorCode="BUSY_ENTITY" message="The entity  is busy completing an operation." when vapp was busy # try execpt needed.

                xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                        <vcloud:Vm
                            xmlns:vcloud="http://www.vmware.com/vcloud/v1.5"
                            name="%s">
                        </vcloud:Vm>""" % (vCloud_Deploy.vm_name)

                post_headers = self.headers
                post_headers['Content-Type']='application/vnd.vmware.vcloud.vm+xml'
                post = requests.put(vCloud_Deploy.vm_href, data=xml, headers=post_headers)
                result = ET.fromstring(post.text)

		self.x.log(lvl='i',msg=("updated vm name ...OK"))

                time.sleep(15)
                self.update_network()

        def update_network(self):

                xml = """<?xml version="1.0" encoding="UTF-8"?>
                        <NetworkConnectionSection
                        xmlns="http://www.vmware.com/vcloud/v1.5"
                        xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1">
                        <ovf:Info>Specifies the available VM network connections</ovf:Info>
                            <PrimaryNetworkConnectionIndex>0</PrimaryNetworkConnectionIndex>
                            <NetworkConnection network="ol-lan-02" needsCustomization="true">
                                <NetworkConnectionIndex>0</NetworkConnectionIndex>
                                <IsConnected>true</IsConnected>
                                <IpAddressAllocationMode>POOL</IpAddressAllocationMode>
                            </NetworkConnection>
                        </NetworkConnectionSection>"""

                post_headers = self.headers
                post_headers['Content-Type']='application/vnd.vmware.vcloud.networkConnectionSection+xml'
                post = requests.put(vCloud_Deploy.vm_href + '/networkConnectionSection', data=xml, headers=post_headers)
                result = ET.fromstring(post.text)

		self.x.log(lvl='i',msg=("setting and connectng vm network  ...OK"))

		time.sleep(15)
                self.update_hostname()

        def update_hostname(self):

                xml = """<?xml version="1.0" encoding="UTF-8"?>
                <GuestCustomizationSection
                   xmlns="http://www.vmware.com/vcloud/v1.5"
                   xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1"
                   ovf:required="false">
                   <ovf:Info>Specifies Guest OS Customization Settings</ovf:Info>
                   <Enabled>true</Enabled>
                   <ComputerName>%s</ComputerName>
                </GuestCustomizationSection>""" % (vCloud_Deploy.vm_name)

                post_headers = self.headers
                post_headers['Content-Type']='application/vnd.vmware.vcloud.guestcustomizationsection+xml'
                post = requests.put(vCloud_Deploy.vm_href + '/guestCustomizationSection', data=xml, headers=post_headers)
                result = ET.fromstring(post.text)
                
		time.sleep (5)
                self.ip()

        def ip(self):

                g = requests.get(vCloud_Deploy.vm_href, headers = self.headers)
                root = ET.fromstring(g.content)
                for child in root.iter():

                        if child.tag == '{http://www.vmware.com/vcloud/v1.5}IpAddress':
				vCloud_Deploy.vm_ip = child.text

		self.x.log(lvl='i',msg=("capturing vm IP address ...OK"))

                time.sleep (15)
                self.power_on_vm()

        def power_on_vm(self):

                g = requests.post(vCloud_Deploy.vm_href + '/power/action/powerOn', headers=self.headers)
                root = ET.fromstring(g.content)
		self.x.log(lvl='i',msg=("virtual machine powered on ...OK"))
