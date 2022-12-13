import re
import os
import sys
import json
import logging
from envs import Environment_varibles
from multipledispatch import dispatch
from airtable_wrapper import Airtable_Api
from airtable_wrapper import ec2_instances_to_records, security_groups_to_records
from botocore.exceptions import ClientError
from boto3_wrapper import EC2_Boto, flatten

logger = logging.getLogger(__name__)

# # Template dictionary to return when an exception is raised (not yet implemented)
exception_return_template = {
    'exception': 'exception_object'
}

catch_invocable_types = r'function|method|builtin_function_or_method'


def catch(func, *args, handle=lambda e, kwargs=None:
          (print("EXCEPTION:EC2_INSTANCES_DESCRIPTOR", e, kwargs)),
          **kwargs):
    try:
        if re.match(catch_invocable_types, str(type(func))[8:-2]) is not None:

            return func(*args, **kwargs)
        return func
    except ClientError as e:
        if "DryRunOperation" not in str(e):
            return handle(e, kwargs)
        return print("INFO", "DryRunOperation Success")
    except TypeError as e:
        return handle(e)
    except KeyError as e:
        return handle(e)
    except Exception as e:
        return handle(e, kwargs)


def set_environment_variables_from_os():
    """
    Set environment variables from os.environ
    """
    Environment_varibles.AIRTABLE_API_KEY = os.environ.get(
        "AIRTABLE_API_KEY")
    Environment_varibles.AIRTABLE_BASE_ID = os.environ.get(
        "AIRTABLE_BASE_ID")
    Environment_varibles.EC2_INSTANCES_TID = os.environ.get(
        "EC2_INSTANCES_TID")
    Environment_varibles.EC2_SECURITY_GROUPS_TID = os.environ.get(
        "EC2_SECURITY_GROUPS_TID")


def init_airtable_api_client():
    """
    Initialize airtable api client
    """
    return Airtable_Api(_base_url=f"https://api.airtable.com/v0/{Environment_varibles.AIRTABLE_BASE_ID}/",
                        _api_key=Environment_varibles.AIRTABLE_API_KEY)


def current_documented_instances():
    # # Get current documented instances
    airtable_api_client = init_airtable_api_client()

    response = {'records': [], 'offset': ''}
    # # Sorting is not necessary here, but I wanted to test it
    while True:
        response_set = airtable_api_client.get_records(
            _table_tid=Environment_varibles.EC2_INSTANCES_TID,
            _offset=response.get('offset'),
            _view='Grid_view',
            _fields=['instance_id', 'start_date', 'instance_record_id'],
            _sorts=[{'field': 'start_date', 'direction': 'desc'}])

        response.update({'offset': response_set.get('offset')})

        None if not bool(response_set.get('records')) else response.get(
            'records').extend(response_set.get('records'))

        if (not bool(response.get('offset'))):
            if response.get('errors'):
                print('INFO: EC2_INSTANCES_DESCRIPTOR', 'currrent_documented_instances',
                      type(current_documented_instances),
                      'terminated due to GET call non 200 response status')
            break

    print('INFO:EC2_INSTANCES_DESCRIPTOR',
          'Number of fetched EC2 instances from Airtable Base:',
          len(response.get('records')))

    return response.get('records')


def current_documented_security_groups():
    # # Get current documented instances
    airtable_api_client = init_airtable_api_client()

    response = {'records': [], 'offset': ''}
    # # Sorting is not necessary here, but I wanted to test it
    # # implement catch later, when strategy migration is done
    while True:
        response_set = airtable_api_client.get_records(
            _table_tid=Environment_varibles.EC2_SECURITY_GROUPS_TID,
            _offset=response.get('offset'),
            _view='Grid_view',
            _fields=['group_id', 'security_group_record_id'])

        response.update({'offset': response_set.get('offset')})

        None if not bool(response_set.get('records')) else response.get(
            'records').extend(response_set.get('records'))

        if (not bool(response.get('offset'))):
            if response.get('errors'):
                print('\n', 'INFO: EC2_INSTANCES_DESCRIPTOR',
                      'currrent_documented_instances',
                      type(current_documented_security_groups),
                      'terminated due to GET call non 200 response status', '\n')
            break

    print('INFO:EC2_INSTANCES_DESCRIPTOR',
          'Number of fetched EC2 security groups from Airtable Base:',
          len(response.get('records')), '\n')

    return response.get('records')


def security_groups_documentation_routine(**kwargs):

    print('INFO: EC2_INSTANCES_DESCRIPTOR',
          'Beginning scan AWS EC2 security groups \n')

    airtable_api_client = init_airtable_api_client()
    security_groups_requests = kwargs.get("security_groups_requests")
    records = []
    # # Fetch security groups requests
    [catch(group.fetch_security_groups) for group in security_groups_requests]

    [records.extend(security_groups_to_records(groups=groups.security_groups,
                                               region=groups.region))
     for groups in security_groups_requests]

    print("\nINFO:EC2_INSTANCES_DESCRIPTOR",
          "Number of scanned security groups:",
          len(records), '\n')

    print('INFO: EC2_INSTANCES_DESCRIPTOR',
          'Ending scan AWS EC2 security groups \n')

    # # Delete current airtable records
    _current_documented_security_groups = current_documented_security_groups()
    _current_documented_security_groups_recordsids = []

    [_current_documented_security_groups_recordsids.append(group.get('fields').get('security_group_record_id'))
     for group in _current_documented_security_groups]

    catch(airtable_api_client.delete_records,
          _records=_current_documented_security_groups_recordsids,
          _table_tid=Environment_varibles.EC2_SECURITY_GROUPS_TID)

    # Send security groups collected data to Airtable (Upsert)
    catch(airtable_api_client.upsert(
        _records=records,
        _table_tid=Environment_varibles.EC2_SECURITY_GROUPS_TID,
        _fields_to_merge_on=["group_id"]))


def ec2_instances_documentation_routine(**kwargs):
    print('INFO: EC2_INSTANCES_DESCRIPTOR',
          'Beginning scan AWS EC2 instances\n')
    records = []
    scanned_instances = []

    airtable_api_client = init_airtable_api_client()
    # # Check for None or Empty requests list
    ec2_instances_requests = kwargs.get("ec2_instances_requests")

    # # Fetch ec2 instances
    [catch(request.fetch_ec2_instances) for request in ec2_instances_requests]

    # # Last Scanned Instances
    [catch(scanned_instances.extend, instances_by_region.instances)
     for instances_by_region in ec2_instances_requests]

    # # Create a Tag whit Key 'Description' if it's not already present
    [catch(request.create_description_tags)
     for request in ec2_instances_requests]

    # # Transform aws response into airtable records set
    [catch(records.extend, ec2_instances_to_records(
        instances=response.instances,
        region=response.region))
        for response in ec2_instances_requests]

    print("\nINFO:EC2_INSTANCES_DESCRIPTOR",
          " Total number of scanned ec2 instances:",
          len(records), '\n')

    # # Delete current airtable records
    _current_documented_ec2_instances = current_documented_instances()
    _current_documented_ec2_instances_recordsids = []

    [_current_documented_ec2_instances_recordsids.append(instance.get('fields').get('instance_record_id'))
     for instance in _current_documented_ec2_instances]

    catch(airtable_api_client.delete_records,
          _records=_current_documented_ec2_instances_recordsids,
          _table_tid=Environment_varibles.EC2_INSTANCES_TID)
    # # Send EC2 instances collected data to Airtable (Upsert)
    documented_instances = catch(airtable_api_client.upsert(_records=records,
                                                            _table_tid=Environment_varibles.EC2_INSTANCES_TID,
                                                            _fields_to_merge_on=["instance_id"]))

    print('INFO: EC2_INSTANCES_DESCRIPTOR',
          'Ending scan AWS EC2 security groups\n')
    return {'scanned_instances': scanned_instances,
            'documented_instances': documented_instances}


def get_aws_iams():
    pass


@ dispatch(dict, object)
def ec2_instances_desc(event, context):
    """
    EC2 instances descriptor lambda invocable function.
    """
    set_environment_variables_from_os()
    available_regions = EC2_Boto.get_available_regions_names()
    # # EC2 describe_instances request list
    boto_requests = [EC2_Boto(region_name=region)
                     for region in available_regions]

    security_groups_documentation_routine(
        security_groups_requests=boto_requests)
    ec2_instances_documentation_routine(
        ec2_instances_requests=boto_requests)

    return {"status code": 200, "body": json.dumps("Scan End V1.1")}


@ dispatch()
def ec2_instances_desc():
    """
    EC2 instances descriptor local invocable function.
    """
    available_regions = EC2_Boto.get_available_regions_names()
    # # EC2 describe_instances request list
    boto_requests = [EC2_Boto(region_name=region)
                     for region in available_regions]

    security_groups_documentation_routine(
        security_groups_requests=boto_requests)

    ec2_instances_documentation_routine(
        ec2_instances_requests=boto_requests)


def main(**kwargs):
    ec2_instances_desc()


if __name__ == '__main__':
    main(**dict(arg.split('=') for arg in sys.argv[1:]))
