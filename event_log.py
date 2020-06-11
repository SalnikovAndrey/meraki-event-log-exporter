from datetime import datetime, timezone
import subprocess
import meraki
from pprint import pprint

# Reads the API key form the api_key.txt saved in the same directory

f = open("api_key.txt", "r")
apikey = f.readline()[:-1:]
f.close()

# TODO: Check alternative secure API handling
# Application input
parent_directory = '/Users/andrey.salnikov/git/database_python'
dashboard = meraki.DashboardAPI(api_key=apikey,output_log=False)
org_id = '869141'
network_id = 'L_683984193406897943'
current_date = datetime.now(timezone.utc)
starting_date = '2020-01-01T01:02:03.000000Z'

# Get product types for the organisation

networks = dashboard.networks.getOrganizationNetworks(org_id)
product_types = []
for i in networks:
    if i['id'] == network_id:
        product_types = i['productTypes']


# Create folder structure to store the files.

lsdir = subprocess.Popen([f'ls {parent_directory}'], stdout=subprocess.PIPE, shell=True)
output_lsdir = lsdir.communicate()[0].decode().split('\n')

if network_id not in output_lsdir:
    mkdir = subprocess.Popen(['mkdir', rf'{parent_directory}/{network_id}'], stdout=subprocess.PIPE)
    for i in product_types:
        mkdir = subprocess.Popen(['mkdir', rf'{parent_directory}/{network_id}/{i}'], stdout=subprocess.PIPE)
        output_mkdir = mkdir.communicate()[0].decode().split('\n')
        # print(f"{i}/ is created")


# Read the current logs in order to determine the latest exported log.
latest_export_dates = {}
for i in product_types:
    lsdir = subprocess.Popen([f'ls -t {parent_directory}/{network_id}/{i} | head -n1'], stdout=subprocess.PIPE, shell=True)
    output_lsdir = lsdir.communicate()[0].decode()
    if output_lsdir == '':
        latest_export_dates[i] = starting_date
        continue
    latest_timestamp = output_lsdir[28:55]
    latest_export_dates[i] = latest_timestamp

print(latest_export_dates)


# Log exporter

for i in product_types:
    # print(i)
    starting_after = latest_export_dates[i]
    # print(current_date)
    # print(starting_after)
    starting_after_date = datetime.strptime(starting_after, '%Y-%m-%dT%H:%M:%S.%f%z')
    while current_date > starting_after_date:
        result = dashboard.events.getNetworkEvents(network_id, productType=i, perPage=1000,
                                                   startingAfter=starting_after)
        print(result['message'])
        print(result['pageStartAt'])
        print(result['pageEndAt'])
        start = starting_after
        end = result['pageEndAt']

        with open(f'{parent_directory}/{network_id}/{i}/{start}_{end}_collection.txt', 'w') as file:
            for e in result['events']:
                file.write(str(f'{e}\n'))

        starting_after = result['pageEndAt']
        starting_after_date = datetime.strptime(starting_after, '%Y-%m-%dT%H:%M:%S.%f%z')


# Get the list of the list of organisations

# organisations = dashboard.organizations.getOrganizations()
# print(organisations)

# org_ids = []
#
# for i in organisations:
#     org_ids.append(i['id'])
#     print(i)
# print(org_ids)
#
# orgs_id = organisations[0]['id']
# print(orgs_id)

# Get the list of networks

# networks = dashboard.networks.getOrganizationNetworks(org_id)
# print(networks)
# network_ids = []
# for i in networks:
#     network_ids.append(i['id'])
#     print(i)
# print(network_ids)
#
# network_id = network_ids[0]

# subprocess.Popen(['find . -name "meraki_api__log__*" -maxdepth 1 -exec mv {} api_log/ \\;'], stdout=subprocess.PIPE, shell=True)
