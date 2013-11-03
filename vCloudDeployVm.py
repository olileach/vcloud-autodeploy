import base64
import requests
import xml.etree.ElementTree as ET
import time

class vCloud_Lookup(object):


	vm_name = None
	vm_ip	= None
	vm_href	= None

        def __init__(self):

                self.login = None
                self.headers = None
                self.endpoint = None
                self.org = None
                self.root = None
                self.vapp_template = None
                self.vapp = None
                #self.vm_href = None
                #self.vm_name = "server01"

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

        def org_url(self):

                g = requests.get(self.endpoint + 'org', data=None, headers = self.headers)
                root = ET.fromstring(g.content)

                for child in root:

                        self.org = child.get("href")

                g = requests.get(self.org, data=None, headers = self.headers)
                self.root = ET.fromstring(g.content)

                return self.org

        def vapp_templates(self, template_name):


                r = requests.get(self.endpoint + '/vAppTemplates/query',headers = self.headers)
                root = ET.fromstring(r.content)

                for child in root:
                        if child.tag == ('''{http://www.vmware.com/vcloud/v1.5}VAppTemplateRecord'''):
                                for k,v in child.attrib.iteritems():
                                        if v == template_name : self.vapp_template = child.attrib['href']

                
        def vapps(self, vapp_name):

                r = requests.get(self.endpoint + '/vApps/query',headers = self.headers)
                root = ET.fromstring(r.content)

                for child in root:

                        if child.tag == ('''{http://www.vmware.com/vcloud/v1.5}VAppRecord'''):
                                for k,v in child.attrib.iteritems():
                                        if v == vapp_name : self.vapp = child.attrib['href']
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
                print "\nDeploying virtual machine. Please wait..... \n"
                print "Installing \n"
                print "1 % completed"
                while x == 0:

                        time.sleep(5)
                        g = requests.get(task_id_href, headers = self.headers)
                        root = ET.fromstring(g.content)

                        for child in root.iter():

                                tag = child.tag
                                tag = tag.replace("{http://www.vmware.com/vcloud/v1.5}","")
                                if tag == 'Progress' :

                                        if child.text != '1' : print child.text,'% completed'
                                        if child.text == '100' : x = 1

                print "\nThe deployment of the virtual machine has been successful. Moving on...\n"
                time.sleep(15)
                self.query_vms()


        def query_vms(self):

                r = requests.get(self.endpoint + 'vms/query', headers = self.headers)
                root = ET.fromstring(r.content)

                for child in root:

                        if child.tag == ('''{http://www.vmware.com/vcloud/v1.5}VMRecord'''):
                                for k,v in child.attrib.iteritems():
                                        if v =="v28388581plc6":
                                                for k,v in child.attrib.iteritems():
                                                        if k == "href" and 'vAppTemplate' not in v :
								vCloud_Lookup.vm_href = v
                                                                self.update_name()

        def update_name(self):

                #minorErrorCode="BUSY_ENTITY" message="The entity  is busy completing an operation." when vapp was busy # try execpt needed.

                xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                        <vcloud:Vm
                            xmlns:vcloud="http://www.vmware.com/vcloud/v1.5"
                            name="%s">
                        </vcloud:Vm>""" % (vCloud_Lookup.vm_name)

                post_headers = self.headers
                post_headers['Content-Type']='application/vnd.vmware.vcloud.vm+xml'
                post = requests.put(vCloud_Lookup.vm_href, data=xml, headers=post_headers)
                result = ET.fromstring(post.text)

		print "\nUpdating the virtual machine name in vCloud...\n"

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
                post = requests.put(vCloud_Lookup.vm_href + '/networkConnectionSection', data=xml, headers=post_headers)
                result = ET.fromstring(post.text)
                
		print "\nUpdating the virtual machine network configuration... \n"

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
                </GuestCustomizationSection>""" % (vCloud_Lookup.vm_name)

                post_headers = self.headers
                post_headers['Content-Type']='application/vnd.vmware.vcloud.guestcustomizationsection+xml'
                post = requests.put(vCloud_Lookup.vm_href + '/guestCustomizationSection', data=xml, headers=post_headers)
                result = ET.fromstring(post.text)
                
		print "\nUpdating the virtual machine hostname... /n"

		time.sleep (5)
                self.ip()

        def ip(self):

                g = requests.get(vCloud_Lookup.vm_href, headers = self.headers)
                root = ET.fromstring(g.content)
                for child in root.iter():

                        if child.tag == '{http://www.vmware.com/vcloud/v1.5}IpAddress':
				print 'IP Address of machine just deployed is:', child.text
				vCloud_Lookup.vm_ip = child.text

                time.sleep (15)
                self.power_on_vm()

        def power_on_vm(self):


                g = requests.post(vCloud_Lookup.vm_href + '/power/action/powerOn', headers=self.headers)
                root = ET.fromstring(g.content)

		print "\nPowering on virtual machine... \n"

