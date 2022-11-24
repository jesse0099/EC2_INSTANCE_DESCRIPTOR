import os
# import logging
import json
from airtable_wrapper import Airtable_Api
from airtable_wrapper import ec2_instances_to_records, security_groups_to_records
from botocore.exceptions import ClientError
from boto3_wrapper import EC2_Boto, flatten

airtable_api_key = os.environ.get("AIRTABLE_API_KEY")

airtable_base_url = os.environ.get("AIRTABLE_BASE_URL")

ec2_instances_tid = os.environ.get("EC2_INSTANCES_TID")

ec2_security_groups_tid = os.environ.get("EC2_SECURITY_GROUPS_TID")

ec2_old_documentation_tbname = os.environ.get("EC2_OLD_DOCUMENTATION_TID")

airtable_api_client = Airtable_Api(
    _base_url=airtable_base_url, _api_key=airtable_api_key)
# Nearly (X,,D) Generic function to handle errors inside list comprehension.


def catch(func, *args, handle=lambda e, kwargs=None: print('EXCEPTION:EC2_INSTANCES_DESCRIPTOR', e, kwargs), **kwargs):
    try:
        if (func is not None and (not isinstance(func, list))):  # Not invocable function
            return func(*args, **kwargs)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            return handle(e, kwargs)
        return print('INFO', 'DryRunOperation Success')
    except TypeError as e:
        return handle(e)
    except KeyError as e:
        return handle(e)
    except Exception as e:
        return handle(e, kwargs)


def security_groups_routine(**kwargs):
    security_groups_requests = kwargs.get('security_groups_requests')
    # # Fetch security groups requests
    [catch(group.fetch_security_groups)
     for group in security_groups_requests]

    records = flatten([security_groups_to_records(groups=groups.security_groups, region=groups.region)
                       for groups in security_groups_requests])

    print('INFO:EC2_INSTANCES_DESCRIPTOR',
          'Number of scanned security groups:', len(records))

    # # Send security groups collected data to Airtable (Upsert)
    catch(airtable_api_client.upsert(_records=records,
                                     _table_tid=ec2_security_groups_tid,
                                     _fields_to_merge_on=['Group ID']))


def ec2_instances_routine(**kwargs):
    ec2_instances_requests = kwargs.get('ec2_instances_requests')
    # # Fetch ec2 instances
    [catch(request.fetch_ec2_instances)
     for request in ec2_instances_requests]

    # # Create a Tag whit Key 'Description' if it's not already present
    # # Not required by the time, but even if it's present, the filled Description tags won't be override
    [catch(request.create_description_tags)
     for request in ec2_instances_requests]

    # # Send EC2 instances collected data to Airtable (Upsert)
    records = flatten([catch(ec2_instances_to_records, instances=response.instances, region=response.region)
                       for response in ec2_instances_requests])

    print('INFO:EC2_INSTANCES_DESCRIPTOR',
          ' Total number of scanned ec2 instances:', len(records))

    catch(airtable_api_client.upsert(_records=records,
                                     _table_tid=ec2_instances_tid,
                                     _fields_to_merge_on=['Instance ID']))


def ec2_instances_desc(event, context):
    print('DEBUG', 'event', '\n', event)
    available_regions = EC2_Boto.get_available_regions_names()
    # # EC2 describe_instances request list
    boto_requests = [EC2_Boto(region_name=region)
                     for region in available_regions]

    security_groups_routine(security_groups_requests=boto_requests)
    ec2_instances_routine(ec2_instances_requests=boto_requests)

    # fields = ['Instance ID', 'Description', 'Region']
    # old_descriptions = catch(airtable_api_client.get_records,
    #                          _fields=fields,
    #                          _view='Grid view',
    #                          _table_tid=ec2_old_documentation_tbname)

    # [catch(EC2_Boto.upsert_ec2_tags_static, rec.get('fields').get('Region'),
    #        [{'Key': 'Description',
    #          'Value': rec.get('fields').get('Description')}],
    #        rec.get('fields').get('Instance ID'))
    #  for rec in old_descriptions.get('records') if rec.get('fields').get('Description') is not None]

    return {"status code": 200, "body": json.dumps("Scan End V1.1")}
