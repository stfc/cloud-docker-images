#!/usr/bin/python
import json
import sys
import os
import requests
from datetime import datetime
from subprocess import Popen, PIPE
import time

def main():
    while True: 

        env = os.environ.copy()

        def cl(c):
            p = Popen(c, shell=True, stdout=PIPE, env=env)
            print(c)
            return p.communicate()[0]

        domains = json.loads(cl("openstack domain list -f json"))

        for domain in domains:
            if "openid" in domain["Description"]:
                iamdomainid=domain["ID"]

        print(iamdomainid)

        iamuserslist = json.loads(cl("openstack user list --domain " + iamdomainid + " -f json"))

        print(iamuserslist)

        rolecommands = []

        for iamuser in iamuserslist:
            print(iamuser["ID"])
            userinstances = json.loads(cl("openstack server list --all-projects -f json --user " + iamuser["ID"]))
            print(userinstances)
            for instance in userinstances:
                instancedetails = json.loads(cl("openstack server show -f json " + instance["ID"]))
                projectid = instancedetails["project_id"]
                rolecmd = "openstack role add --user " + iamuser["ID"] + " --project " + projectid + " user"
                if rolecmd not in rolecommands:
                    rolecommands.append(rolecmd)

        for rolecommand in rolecommands:
            print(rolecommand)
            cl(rolecommand)

        time.sleep(3600)

if __name__ == "__main__":
    main()