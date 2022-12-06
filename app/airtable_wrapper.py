import json
from boto3_wrapper import EC2_Boto
from datetime import datetime

import pytz
import urllib3
from urllib.parse import quote, urlencode

# # Temporal catch, refactor on next iteration

# EC2 describe_instances AirTable field names' response keys
_instance_id = ('instance_id', 'InstanceId')
_security_groups = ('security_groups', 'SecurityGroups')
_instance_state = ('instance_state', 'State')
_instance_type = ('instance_type', 'InstanceType')
_instance_name = ('instance_name', 'Name')
_instance_tags = ('instance_tags', 'Tags')
_start_date = ('start_date', 'LaunchTime')
_public_ip = ('public_ip', 'PublicIpAddress')
_scanned_on_region = ('scanned_on_region', 'Region')
_last_scan_date = 'last_scan_date'


# Security Groups Airtable field names' response keys
_group_name = ('group_name', 'GroupName')
_group_id = ('group_id', 'GroupId')
_description = ('description', 'Description')
_empt_string = ''


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def ec2_instances_to_records(**kwargs):
    instances = kwargs.get('instances')
    scanned_on = kwargs.get('region')
    if instances is None:
        print('WARNING', 'Instances must not be None', scanned_on)
        return []
    elif len(instances) == 0:
        print('WARNING', 'Empty set of instances', scanned_on)
        return []
    records = [{'fields': {_instance_id[0]: str(instance.get(_instance_id[1])),
                           _instance_type[0]: instance.get(_instance_type[1]),
                           _instance_name[0]: EC2_Boto.ec2_tags_get_value(instance.get(_instance_tags[1]), _instance_name[1]),
                           _instance_tags[0]: EC2_Boto.stringify_ec2_tags(instance.get(_instance_tags[1])),
                           _public_ip[0]: instance.get(_public_ip[1]),
                           _security_groups[0]:  EC2_Boto.ec2_get_security_groups_ids(instance.get(_security_groups[1])),
                           _instance_state[0]: instance.get(_instance_state[1]).get('Name'),
                           _start_date[0]: str(instance.get(_start_date[1])),
                           _last_scan_date: str(datetime.now(pytz.utc)),
                           _scanned_on_region[0]: scanned_on,
                           _description[0]: EC2_Boto.ec2_tags_get_value(instance.get(_instance_tags[1]), _description[1])}}
               for instance in instances]
    return records


def security_groups_to_records(**kwargs):
    groups = kwargs.get('groups')
    _scanned_on = kwargs.get('region')
    if groups is None:
        print('WARNING:AIR_WRAPPER',
              'Security groups must not be None', _scanned_on)
        return []
    elif len(groups) == 0:
        print('WARNING:AIR_WRAPPER', 'Empty set of groups', _scanned_on)
        return []
    return [{'fields': {_group_name[0]: group.get(_group_name[1]),
                        _group_id[0]: group.get(_group_id[1]),
                        _description[0]: group.get(_description[1]),
                        _scanned_on_region[0]: _scanned_on}}
            for group in groups]


class Airtable_Api:
    def __init__(self, **kwargs):
        self.airtable_api_key = kwargs.get('_api_key')
        self.base_url = kwargs.get('_base_url')

    # Airtable API Call to get a list of records

    # # FilterByFormula not yet supported
    # # Sorting still work in progress
    # # Return a Dictionary containing the fetched records and an offset token
    def get_records(self, _max_records=None, _page_size=None, _offset=None, _sorts=None, **kwargs):
        table_tid = kwargs.get('_table_tid')
        fields = kwargs.get('_fields')
        view = kwargs.get('_view')
        # # Dictionary 'param_name', 'param values[]'
        params_to_encode = {}

        url = f'{self.base_url}{table_tid}'

        if fields is None or view is None:
            print('WARNING:AIR_WRAPPER', 'No fields or view specified')
            return {'records': [], 'offset': None}

        params_to_encode.update({'view': view})
        params_to_encode.update({'fields': fields})

        None if _max_records is None else params_to_encode.update(
            {'maxRecords': _max_records})
        None if _page_size is None else params_to_encode.update(
            {'pageSize': _page_size})
        None if _offset is None else params_to_encode.update(
            {'offset': quote(_offset)})
        None if _sorts is None else params_to_encode.update(
            {'sort%5B0%5D%5B': _sorts})

        # # Next iterations:
        # # 1. Check for string length of the url, Airtable allows until 16k characters,
        # # if it exceeds this limit, the POST method could be used
        encoded_params = urlencode(params_to_encode, doseq=True)
        url += f'?{encoded_params}'

        http = urllib3.PoolManager()
        r = http.request(
            'GET',
            url,
            headers={'Content-Type': 'application/json',
                     'Authorization': f'Bearer {self.airtable_api_key}'}
        )
        decoded_response = json.loads(r.data.decode('utf-8'))
        records = decoded_response.get('records')
        offset = decoded_response.get('offset')
        return {'records': records, 'offset': offset}

    # Airtable API Call to upsert records

    def upsert(self, **kwargs):
        table_tid = kwargs.get('_table_tid')
        records = kwargs.get('_records')
        fields_to_merge_on = kwargs.get('_fields_to_merge_on')
        if (records is None):
            print('WARNING:AIR_WRAPPER', 'Records must not be None')
            return
        http = urllib3.PoolManager()

        # Airtable only allows 10 records per request
        for records_set in chunker(records, 10):
            # Dev Print

            # Upsert Call Params
            data = {'performUpsert': {
                "fieldsToMergeOn": fields_to_merge_on},
                "typecast": True}

            data['records'] = records_set
            encoded_data = json.dumps(data).encode('utf-8')
            r = http.request(
                'PATCH',
                f'{self.base_url}{table_tid}',
                body=encoded_data,
                headers={'Content-Type': 'application/json',
                         'Authorization': f'Bearer {self.airtable_api_key}'}
            )
            print('INFO:AIR_WRAPPER', 'Sending', len(
                records_set), 'records to Airtable')
