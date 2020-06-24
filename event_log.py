from datetime import datetime, timezone
import subprocess
import meraki


# Application input
parent_directory = 'YOUR_PATH_TO_STORE_EVENT_LOG'
organisation_id = 'YOUR_ORGANISATION_ID'
network_id = 'YOUR_NETWORK_ID'
starting_date = '2020-01-01T00:00:00.000000Z'
api_key_file = 'PATH_TO_API.TXT_FILE'
current_date = datetime.now(timezone.utc)

with open(api_key_file, 'r') as reader: # Reads the API key form the api_key.txt saved in the same directory
    apikey = reader.readline()[:-1:]
dashboard = meraki.DashboardAPI(api_key=apikey, output_log=False, suppress_logging=True)


def get_product_types(organisation_id, network_id):
    """
    This function determines what device types this network contains.
    :param organisation_id: Cisco Meraki Organisation ID
    :param net_id: Cisco Meraki Network ID
    :return: Returns the list of the products which your network contains
    """
    networks = dashboard.networks.getOrganizationNetworks(organisation_id)
    product_types = []
    for i in networks:
        if i['id'] == network_id:
            product_types = i['productTypes']
    return product_types


def create_folders(parent_directory):
    """
    This function create a folder structure to store the logs.
    :param parent_directory: Directory to export and store the logs
    :return: True
    """
    lsdir = subprocess.Popen([f'ls {parent_directory}'], stdout=subprocess.PIPE, shell=True)
    output_lsdir = lsdir.communicate()[0].decode().split('\n')
    if network_id not in output_lsdir:
        mkdir = subprocess.Popen(['mkdir', rf'{parent_directory}/{network_id}'], stdout=subprocess.PIPE)
        for i in product_types:
            mkdir = subprocess.Popen(['mkdir', rf'{parent_directory}/{network_id}/{i}'], stdout=subprocess.PIPE)
            output_mkdir = mkdir.communicate()[0].decode().split('\n')
    return True


def event_log_exporter(parent_directory, network_id, product_types):
    """

    :param parent_directory: Directory to export and store the logs
    :param network_id: Cisco Meraki Network ID
    :param product_types: List of product types which the network contains
    :return: True
    """
    # Checking the current logs in order to determine the latest exported log.
    latest_export_dates = {}
    for i in product_types:
        lsdir = subprocess.Popen([f'ls -t {parent_directory}/{network_id}/{i} | head -n1'], stdout=subprocess.PIPE,
                                 shell=True)
        output_lsdir = lsdir.communicate()[0].decode()
        if output_lsdir == '':
            latest_export_dates[i] = starting_date
            continue
        latest_timestamp = output_lsdir[28:55]
        latest_export_dates[i] = latest_timestamp

    # Log exporter
    for i in product_types:
        print(f"Checking event log for {i}:")
        starting_after = latest_export_dates[i]
        starting_after_date = datetime.strptime(starting_after, '%Y-%m-%dT%H:%M:%S.%f%z')
        while current_date > starting_after_date:
            result = dashboard.events.getNetworkEvents(network_id, productType=i, perPage=1000,
                                                       startingAfter=starting_after)
            start = starting_after
            end = result['pageEndAt']
            print(f'Exporting logs from {start} to {end}')

            with open(f'{parent_directory}/{network_id}/{i}/{start}_{end}_collection.txt', 'w') as file:
                for e in result['events']:
                    file.write(str(f'{e}\n'))

            starting_after = result['pageEndAt']
            starting_after_date = datetime.strptime(starting_after, '%Y-%m-%dT%H:%M:%S.%f%z')
    return True


# Get product types for the organisation
product_types = get_product_types(organisation_id, network_id)
print(f'The logs are going to be exported for these product types: {product_types}')

# Create folder structure to store the files.
create_folders(parent_directory)

# Export the logs
event_log_exporter(parent_directory, network_id, product_types)
