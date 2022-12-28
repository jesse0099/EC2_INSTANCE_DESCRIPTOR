import sys
import boto3_wrapper
from boto3_wrapper import IAM_Boto


def get_all_users():
    iam_client = IAM_Boto()
    all_users_arns = iam_client.get_account_users_arns()
    return all_users_arns


def get_policies_granting_services(_users_arns, _services_namespaces):
    iam_client = IAM_Boto()

    granted_policies = [
        {
            'user_arn': user_arn,
            'policies_granting_services': iam_client.get_arn_policies_granting_services_access(
                _arn=user_arn,
                _services_namespaces=_services_namespaces)
        }
        for user_arn in _users_arns]

    return granted_policies


def main(**kwargs):
    granting_policies_by_user = get_policies_granting_services(
        _users_arns=get_all_users(), _services_namespaces=['ec2'])

    [print(user_granting_policies, '\n\n')
     for user_granting_policies in granting_policies_by_user
        if user_granting_policies.get('policies_granting_services')]


if __name__ == '__main__':
    main(**dict(arg.split('=') for arg in sys.argv[1:]))
