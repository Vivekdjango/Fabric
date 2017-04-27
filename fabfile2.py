#!/usr/bin/python

#Execute this file as a fabfile.py


from fabric.api import *
from getpass import getpass

f=open("hostname.txt","r")
g=open("new_hostname.txt","r")



hst=[]

#for k in g:
#        k=k.split()
#        hst.append(k)

for i in g:
	i=i.strip()
	env.hosts.append(i)

env.password=getpass("Please enter your password :")

'''
def test1():
	d=env.hosts.index(env.host)
	print hst[d][0]
	run("hostname")
'''
def update_hostname():
	try:
		d=env.hosts.index(env.host)
		a=sudo("hostname %s"%(hst[d][0]))
		print a.stdout.split("\r\n")
		b=sudo(">/etc/hostname")
		print b.stdout.split("\r\n")
		c=sudo("echo %s > /etc/hostname"%(hst[d][0]))
		print c.stdout.split("\r\n")
		d=sudo("init 6")
		print d.stdout.split("\r\n")
	except:
		print env.host,"Couldn't proceed"

def update_puppet():
	try:
		p1=sudo("rm -rf /var/lib/puppet/ssl")
		print p1.stdout.split("\r\n")
		p2=sudo("puppet agent -t --server <puppet URL>")
		print p2.stdout.split("\r\n")
	except:
		print env.host,"Failed"

