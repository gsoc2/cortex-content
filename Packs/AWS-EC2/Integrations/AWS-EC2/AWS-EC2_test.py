from AWSApiModule import *
import importlib
import pytest
AWS_EC2 = importlib.import_module("AWS-EC2")


VALID_ARGS = {"groupId": "sg-0566450bb5ae17c7d",
              "IpPermissionsfromPort": 23,
              "IpPermissionsToPort": 23,
              "IpPermissionsIpProtocol": "TCP",
              "region": "reg",
              "roleArn": "role",
              "roleSessionName": "role_Name",
              "roleSessionDuration": 200}

IPPERMISSIONSFULL_ARGS = {"groupId": "sg-0566450bb5ae17c7d",
                          "IpPermissionsFull": """[{"IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                          "Ipv6Ranges": [], "PrefixListIds": [], "UserIdGroupPairs": []}]"""}

INVALID_ARGS = {"groupId": "sg-0566450bb5ae17c7d",
                "region": "reg",
                "roleArn": "role",
                "roleSessionName": "role_Name",
                "roleSessionDuration": 200}


class Boto3Client:
    def authorize_security_group_egress(self, **kwargs):
        pass

    def authorize_security_group_ingress(self, **kwargs):
        pass


def create_client():
    aws_client_args = {
        'aws_default_region': 'us-east-1',
        'aws_role_arn': None,
        'aws_role_session_name': None,
        'aws_role_session_duration': None,
        'aws_role_policy': None,
        'aws_access_key_id': 'test_access_key',
        'aws_secret_access_key': 'test_secret_key',
        'aws_session_token': 'test_sts_token',
        'verify_certificate': False,
        'timeout': 60,
        'retries': 3
    }

    client = AWSClient(**aws_client_args)
    return client


def validate_kwargs(*args, **kwargs):
    normal_kwargs = {'IpPermissions': [{'ToPort': 23, 'FromPort': 23, 'UserIdGroupPairs': [{}], 'IpProtocol': 'TCP'}],
                     'GroupId': 'sg-0566450bb5ae17c7d'}
    ippermsfull_kwargs = {'GroupId': 'sg-0566450bb5ae17c7d', 'IpPermissions':
                          [{'IpProtocol': '-1', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                           'Ipv6Ranges': [], 'PrefixListIds': [], 'UserIdGroupPairs': []}]}
    if kwargs in (normal_kwargs, ippermsfull_kwargs):
        return {'ResponseMetadata': {'HTTPStatusCode': 200}, 'Return': "some_return_value"}
    else:
        return {'ResponseMetadata': {'HTTPStatusCode': 404}, 'Return': "some_return_value"}


@pytest.mark.parametrize('args, expected_results', [
    (IPPERMISSIONSFULL_ARGS, "The Security Group ingress rule was created"),
    (INVALID_ARGS, None)
])
def test_aws_ec2_authorize_security_group_ingress_rule(mocker, args, expected_results):
    """
    Given
    - authorize-security-group-ingress-command arguments and aws client
    - Case 1: Valid arguments.
    - Case 2: Invalid arguments.
    When
    - running authorize-security-group-ingress-command.
    Then
    - Ensure that the information was parsed correctly
    - Case 1: Should ensure that the right message was resulted return true.
    - Case 2: Should ensure that no message was resulted return true.
    """
    aws_client = create_client()
    mocker.patch.object(AWSClient, "aws_session", return_value=Boto3Client())
    mocker.patch.object(Boto3Client, 'authorize_security_group_ingress', side_effect=validate_kwargs)
    mocker.patch.object(demisto, 'results')
    AWS_EC2.authorize_security_group_ingress_command(args, aws_client)
    if not expected_results:
        assert not demisto.results.call_args
    else:
        results = demisto.results.call_args[0][0]
        assert results == expected_results


def test_create_policy_kwargs_dict():
    """
    Given
    - empty policy kwargs

    When
    - running create_policy_kwargs_dict function

    Then
    - make sure that create_policy_kwargs_dict does not fail on any exception

    """
    assert AWS_EC2.create_policy_kwargs_dict({}) == {}


@pytest.mark.parametrize('args, expected_results', [
    (VALID_ARGS, "The Security Group egress rule was created"),
    (INVALID_ARGS, None)
])
def test_aws_ec2_authorize_security_group_egress_rule(mocker, args, expected_results):
    """
    Given
    - authorize-security-group-egress-command arguments and aws client
    - Case 1: Valid arguments.
    - Case 2: Invalid arguments.
    When
    - running authorize-security-group-egress-command.
    Then
    - Ensure that the information was parsed correctly
    - Case 1: Should ensure that the right message was resulted return true.
    - Case 2: Should ensure that no message was resulted return true.
    """
    aws_client = create_client()
    mocker.patch.object(AWSClient, "aws_session", return_value=Boto3Client())
    mocker.patch.object(Boto3Client, 'authorize_security_group_egress', side_effect=validate_kwargs)
    mocker.patch.object(demisto, 'results')
    AWS_EC2.authorize_security_group_egress_command(args, aws_client)
    if not expected_results:
        assert not demisto.results.call_args
    else:
        results = demisto.results.call_args[0][0]
        assert results == expected_results


@pytest.mark.parametrize('filter, expected_results', [
    ("Name=iam-instance-profile.arn,Values=arn:aws:iam::664798938958:instance-profile/AmazonEKSNodeRole",
     [{'Name': 'iam-instance-profile.arn', 'Values': ['arn:aws:iam::664798938958:instance-profile/AmazonEKSNodeRole']}])
])
def test_parse_filter_field(filter, expected_results):
    """
    Given
    - A filter string.
    - Case 1: a filter string including ':' in the value.
    When
    - Running parse_filter_field method.
    Then
    - Ensure that the filter was parsed correctly.
    - Case 1: Should ensure that the filter value include the whole value (including the part after the ':').
    """
    res = AWS_EC2.parse_filter_field(filter)
    assert res == expected_results


def test_update_snap_permission(mocker):
    """
    Given
    - Snapshot to update
    When
    - Running modify_snapshot_permission_command
    Then
    - Validate params like userId and groupId sent as expected.
    """
    mocker.patch.object(AWSClient, "aws_session")

    AWS_EC2.modify_snapshot_permission_command(
        {
            'operationType': 'add',
            'userIds': 'userIds',
            'snapshotId': 'snapshotId'
        }, create_client())
    mocked_command = AWSClient.aws_session().modify_snapshot_attribute

    assert mocked_command.call_args.kwargs['Attribute'] == 'createVolumePermission'
    assert mocked_command.call_args.kwargs['UserIds'] == ['userIds']
    assert 'GroupNames' not in mocked_command.call_args.kwargs
