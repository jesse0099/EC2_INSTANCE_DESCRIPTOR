import boto3
import copy
from botocore.exceptions import ClientError
from copy import deepcopy
# probably need refactor
_group_id = ('Group ID', 'GroupId')


def flatten(l):
    return [item for sublist in l for item in sublist]


class IAM_Boto:
    client_type = 'iam'

    def __init__(self, dry_run=False):
        self.client = boto3.client(IAM_Boto.client_type)
        self.account_users_arns = []

    def get_account_users_arns(self):
        """
        Get all users arns in the account
        :return: a new list of users arns
        :rtype: [string...]
        """
        self.account_users_arns = []
        paginator = self.client.get_paginator('list_users')

        [[self.account_users_arns.append(user['Arn'])
            for user in response.get('Users')
            if user.get('Arn')]
         for response in paginator.paginate()
         if response.get('Users')]

        return deepcopy(self.account_users_arns)

    def get_arn_policies_granting_services_access(self, _arn, _services_namespaces):
        """
        Get all policies that grant access to a list of services.
        :param _arn: Arn(amazon resource name) can be: User, Group, Role
        :type _arn: string
        :param _services_namespaces: AWS services namespaces where access wants to be checked
        :type _services_namespaces: [string...]
        :return: a new list of dictionaries
        :rtype: [{Policies, ServiceNamespace}]
        """
        user_policies_granting_access = []
        marker = ''

        while True:
            response = self.client.list_policies_granting_service_access(
                Marker=marker,
                Arn=_arn,
                ServiceNamespaces=_services_namespaces
            ) if marker else self.client.list_policies_granting_service_access(
                Arn=_arn,
                ServiceNamespaces=_services_namespaces
            )

            if response.get('PoliciesGrantingServiceAccess'):
                user_policies_granting_access.extend(
                    response.get('PoliciesGrantingServiceAccess'))

            if not response.get('IsTruncated'):
                break

            marker = response.get('Marker')

        return user_policies_granting_access


class EC2_Boto:
    client_type = 'ec2'
    # No region name defined for the static_client
    static_client = boto3.client(client_type)

    @ staticmethod
    def get_available_regions_names():
        try:
            return [region['RegionName'] for region in EC2_Boto.static_client.describe_regions()['Regions']]
        except Exception as e:
            print('EXCEPTION:BOTO_WRAPPER', e)
            return []

    @ staticmethod
    def tag_exists(instance, tag_key):
        tags = instance.get('Tags')
        if tags is None:
            return False
        if len(tags) == 0:
            return False
        return len([tag for tag in instance.get('Tags') if tag.get('Key') == tag_key])

    @ staticmethod
    def ec2_tags_get_value(tags, key):
        """Get the value of an ec2-tag, given a tags list and a key.

        :param tags:  EC2 instance list of tags.
        :type tags: [{'Key': 'String', 'Value': 'String'...}]
        :param key: EC2 instance tag key.
        :type key: String
        :return: String value of the tag if it's present, empty string otherwise.
        :rtype: String
        """
        if tags is None:
            return ''
        desired_tag = [tag for tag in tags if tag.get(
            'Key') == key]
        if len(desired_tag) > 0:
            return desired_tag[0].get('Value')
        return ''

    @ staticmethod
    def stringify_ec2_tags(tags):
        """Stringify ec2 tags list

        :param tags: EC2 instance list of tags.
        :type tags: [{'Key': 'String', 'Value': 'String'...}]
        :return: Stringified tags if tags is not None, empty string otherwise.
        :rtype: String
        """
        if tags is None:
            return ''
        # Extract tags from response
        return ','.join([tag.get('Value') for tag in tags if tag.get('Value')])

    @ staticmethod
    def ec2_get_security_groups_ids(security_groups):
        if security_groups is None:
            return []
        return [group.get(_group_id[1]) for group in security_groups if group is not None]

    @ staticmethod
    def upsert_ec2_tags_static(region_name, tags, instance_id):
        EC2_Boto.static_client = boto3.client(
            EC2_Boto.client_type, region_name=region_name)
        EC2_Boto.static_client.create_tags(
            Resources=[instance_id], Tags=tags)
        EC2_Boto.static_client = boto3.client(EC2_Boto.client_type)

    def __init__(self, region_name, dry_run=False):
        self.instances = []
        self.region = region_name
        self.security_groups = []
        self.dry_run = dry_run
        self.client = boto3.client(
            EC2_Boto.client_type, region_name=region_name)

    def fetch_ec2_instances(self):
        describe_instance_response = self.client.describe_instances(
            DryRun=self.dry_run)
        reservations = describe_instance_response.get('Reservations')
        self.instances = flatten([reservation.get('Instances') for reservation in reservations if len(
            reservation.get('Instances')) > 0])
        print('INFO:BOTO_WRAPPER', 'Number of instances:',
              len(self.instances), ' - Region:', self.region)

    def upsert_ec2_tags(self, instance_id, tags):
        self.client.create_tags(
            Resources=[instance_id], Tags=tags)

    def create_description_tags(self):
        [self.upsert_ec2_tags(instance.get('InstanceId'), [{'Key': 'Description', 'Value': ''}])
         for instance in self.instances if not EC2_Boto.tag_exists(instance, 'Description')
         and instance.get('State').get('Name') not in ['shutting-down', 'terminated']]

    def fetch_security_groups(self):
        boto_response = self.client.describe_security_groups(
            DryRun=self.dry_run).get('SecurityGroups')
        self.security_groups = boto_response
        print('INFO:BOTO_WRAPPER', 'Number of security groups:',
              len(self.security_groups), 'Region:', self.region)
