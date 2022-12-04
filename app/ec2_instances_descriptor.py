import os
import json
from multipledispatch import dispatch
from airtable_wrapper import Airtable_Api
from airtable_wrapper import ec2_instances_to_records, security_groups_to_records
from botocore.exceptions import ClientError
from boto3_wrapper import EC2_Boto, flatten

# # Enviroment variables fetched from lambda context
airtable_api_key = os.environ.get("AIRTABLE_API_KEY")

airtable_base_url = os.environ.get("AIRTABLE_BASE_URL")

ec2_instances_tid = os.environ.get("EC2_INSTANCES_TID")

ec2_security_groups_tid = os.environ.get("EC2_SECURITY_GROUPS_TID")

ec2_old_documentation_tid = os.environ.get("EC2_OLD_DOCUMENTATION_TID")


def catch(func, *args,
          handle=lambda e, kwargs=None: print(
              "EXCEPTION:EC2_INSTANCES_DESCRIPTOR", e, kwargs),
          **kwargs):
    try:
        if func is not None and (not isinstance(func, list)):  # Not invocable function
            return func(*args, **kwargs)
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


def set_environment_variables(envs):
    """Set environment variables from a context distinct from lambda.

    :param envs: Dictionary of environment variables.
    :type envs: Dictionary
    """
    global airtable_api_key, airtable_base_url, ec2_instances_tid, ec2_security_groups_tid
    airtable_api_key = envs.get("AIRTABLE_API_KEY")
    airtable_base_url = envs.get("AIRTABLE_BASE_URL")
    ec2_instances_tid = envs.get("EC2_INSTANCES_TID")
    ec2_security_groups_tid = envs.get("EC2_SECURITY_GROUPS_TID")


def init_airtable_api_client():
    return Airtable_Api(
        _base_url=airtable_base_url, _api_key=airtable_api_key
    )


def security_groups_routine(**kwargs):
    airtable_api_client = init_airtable_api_client()
    security_groups_requests = kwargs.get("security_groups_requests")
    # # Fetch security groups requests
    [catch(group.fetch_security_groups) for group in security_groups_requests]

    records = flatten(
        [
            security_groups_to_records(
                groups=groups.security_groups, region=groups.region
            )
            for groups in security_groups_requests
        ]
    )

    print(
        "INFO:EC2_INSTANCES_DESCRIPTOR",
        "Number of scanned security groups:",
        len(records),
    )

    # # Send security groups collected data to Airtable (Upsert)
    catch(
        airtable_api_client.upsert(
            _records=records,
            _table_tid=ec2_security_groups_tid,
            _fields_to_merge_on=["Group ID"],
        )
    )


def ec2_instances_routine(**kwargs):
    airtable_api_client = init_airtable_api_client()
    ec2_instances_requests = kwargs.get("ec2_instances_requests")
    # # Fetch ec2 instances
    [catch(request.fetch_ec2_instances) for request in ec2_instances_requests]

    # # Create a Tag whit Key 'Description' if it's not already present
    # # Not required by the time, but even if it's present, the filled Description tags won't be override
    [catch(request.create_description_tags)
     for request in ec2_instances_requests]

    # # Send EC2 instances collected data to Airtable (Upsert)
    records = flatten(
        [
            catch(
                ec2_instances_to_records,
                instances=response.instances,
                region=response.region,
            )
            for response in ec2_instances_requests
        ]
    )

    print(
        "INFO:EC2_INSTANCES_DESCRIPTOR",
        " Total number of scanned ec2 instances:",
        len(records),
    )

    catch(
        airtable_api_client.upsert(
            _records=records,
            _table_tid=ec2_instances_tid,
            _fields_to_merge_on=["Instance ID"],
        )
    )


@dispatch(dict, object)
def ec2_instances_desc(event, context):
    print("DEBUG", "event", "\n", event)
    available_regions = EC2_Boto.get_available_regions_names()
    # # EC2 describe_instances request list
    boto_requests = [EC2_Boto(region_name=region)
                     for region in available_regions]

    # security_groups_routine(security_groups_requests=boto_requests)
    ec2_instances_routine(ec2_instances_requests=boto_requests)

    return {"status code": 200, "body": json.dumps("Scan End V1.1")}


@dispatch(dict)
def ec2_instances_desc(envs):
    """EC2 instances descriptor local invocable function.

    :param envs: A dictionary containing all the enviroment variables necessary to execute the script locally.
    :type envs: Dictionary
    :return: Boolean indicating whether the script was successfully executed.
    :rtype: Boolean
    """
    if envs is None:
        return False
    set_environment_variables(envs)

    available_regions = EC2_Boto.get_available_regions_names()
    # # EC2 describe_instances request list
    boto_requests = [EC2_Boto(region_name=region)
                     for region in available_regions]
    # security_groups_routine(security_groups_requests=boto_requests)
    ec2_instances_routine(ec2_instances_requests=boto_requests)
