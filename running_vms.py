"""
I need a script or automation of some sorts which runs on a daily basis which gets me a list of
running instances (VMs) on a cloud provider. 

It should show me a report of the instances that are running for a certain period of time. 
(That time can be configurable eventually )

"""

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import os
import schedule
import time
from datetime import datetime
import pytz
import json 


LOCATION = 'us-east-1'

# Resource Group
GROUP_NAME = 'py-assignment-1'

def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ClientSecretCredential(
        client_secret=os.environ['AZURE_CLIENT_SECRET'],
        client_id=os.environ['AZURE_CLIENT_ID'],
        tenant_id=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id


def run_example():
    
    # Create all clients with an Application (service principal) token provider
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    day = datetime.today().strftime('%Y-%m-%d')
    dt = datetime.strptime(day, "%Y-%m-%d")
    timezone = pytz.UTC
    dt_with_timezone = timezone.localize(dt)

    try:
        # List VMs in subscription
        print('\nList VMs in subscription -')
        for vm in compute_client.virtual_machines.list_all():
            print("VM name -", vm.name)
        # List VM in resource group
        print('\nList VMs in resource group -')
        for vm in compute_client.virtual_machines.list(GROUP_NAME):
            if abs((vm.time_created - dt_with_timezone).days) >= 1:
                print("VM name which is running from last 7 or more than 7 days -", vm.name) 
                with open("report.json","a") as textfile:
                    id = vm.id
                    splitIDbyslash = id.split('/')

                    vm_info = {
                        "VM Name": vm.name,
                        "VM ID": vm.id,
                        "VM Resource Group": splitIDbyslash[4],
                        "VM Subscription ID": splitIDbyslash[2],
                        "Region": vm.location,
                        "VM type": vm.type,
                      }
                    textfile.write(json.dumps(vm_info))

                    print("added to the file")
                    textfile.close()
    except Exception as e:
        print(f"\nError: {e}")
     

if __name__ == "__main__":
    schedule.every().day.at("18:00").do(run_example)
    while True:
        schedule.run_pending()
        time.sleep(1)


    




