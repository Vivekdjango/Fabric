#!/usr/bin/python


import logging, os
from fabric.api import local, sudo, env, settings

from getpass import *

env.hosts =['127.0.0.1']
logging.basicConfig(filename='idrac_conf.log', filemode='w', level=logging.ERROR)

hosts = [line.rstrip('\n') for line in open('hosts.txt')]

online_hosts = filter(lambda host : os.system("ping -c 1 "+host) == 0 , hosts)

DEFAULT_COLO = "<value>"

PASSWORD=getpass("Enter Password:")

colo_dns = {
    "uh1" :["<IP1>", "<IP1>"],
    "hkg1":["<IP1>", "<IP1>"],
    "lhr1":["<IP1>", "<IP1>"],
    "dfw1":["<IP1>"],
    "pek1":["<IP2>"],
}


def network_settings():
    """
    Sets network setting for iDRAC
    """
    for host in online_hosts:
        with settings(warn_only=True):

            result1 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgLanNetworking -o cfgDNSDomainName <Domain Name>")
            if result1.failed:
                logging.error("Host: [ "+host+" ] : " + "Configuration for DNSDomainName failed ")

            result2 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgLanNetworking -o cfgDNSServer1 "+colo_dns[DEFAULT_COLO ][0])
            if result2.failed:
                logging.error("Host: [ "+host+" ] : " + "Configuration for DNSServer1 failed  ")

            result3 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgLanNetworking -o cfgDNSServer2 "+colo_dns[DEFAULT_COLO ][1])
            if result3.failed:
                logging.error("Host: [ "+host+" ] : " + "Configuration for DNSServer2 failed  ")


def enable_ad():
    """
    Enables AD and then sets standard schema.
    """
    for host in online_hosts:
        with settings(warn_only=True):

            result1 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgActiveDirectory -o cfgADEnable 1")
            if result1.failed:
                logging.error("Host: [ "+host+" ] : " + "Enabling Active Directory failed  ")

            result2 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgActiveDirectory -o cfgADType 2")
            if result2.failed:
                    logging.error("Host: [ "+host+" ] : " + "Setting of standard schema for AD failed  ")



def create_user_domain():
    """
    Creates user domain name, domain controller, catalog server
    """
    for host in online_hosts:
        with settings(warn_only=True):

            result1 = sudo("racadm -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgUserDomain -o cfgUserDomainName <Domain Name> -i 1")
            if result1.failed:
                logging.error("Host: [ "+host+" ] : " + "Configuration for UserDomainName failed  ")

            result2 = sudo("racadm -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgActiveDirectory -o cfgADDomainController1 <Domain Name>")
            if result2.failed:
                logging.error("Host: [ "+host+" ] : " + "Configuration for DomainController1 failed  ")

            result3 = sudo("racadm -r "+host+"  -u root -p "+PASSWORD+" config -g  cfgActiveDirectory -o cfgADGlobalCatalog1 <Domain Name>")
            if result3.failed:
                logging.error("Host: [ "+host+" ] : " + "Configuration for GlobalCatalog1 failed  ")


def create_groups():
    """
    Creates groups and permissions
    """
    groups = ["iDRAC-Administrators", "iDRAC-Operators", "iDRAC-Readonly"]
    group_priviledges = ["0x000001ff", "0x000000f9", "0x00000001"]
    for host in online_hosts:
        for index in [1,2,3]:
            print index," ", groups[index-1]
            with settings(warn_only=True):

                result1 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g cfgStandardSchema -i "+str(index) +" -o cfgSSADRoleGroupName "+groups[index-1])
                if result1.failed:
                    logging.error("Host: [ "+host+" ] : " + "Configuration for RoleGroupName failed  ")

                result2 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g cfgStandardSchema -i "+str(index) +" -o cfgSSADRoleGroupDomain corp.inmobi.com")
                if result2.failed:
                    logging.error("Host: [ "+host+" ] : " + "Configuration for RoleGroupDomain failed  ")

                result3 = sudo("racadm5 -r "+host+"  -u root -p "+PASSWORD+" config -g cfgStandardSchema -i "+str(index) +" -o cfgSSADRoleGroupPrivilege "+ group_priviledges[index-1])
                if result3.failed:
                    logging.error("Host: [ "+host+" ] : " + "Configuration for RoleGroupPriviledge failed  ")


def main_configure_ad():
    """
    Main function to start configuration.
    """

    print "------------- AD Configuration Started --------------"
    network_settings()
    enable_ad()
    create_user_domain()
    create_groups()
    print "------------- Setup Finished...Please Check idrac_conf.log for any failures --------------"


