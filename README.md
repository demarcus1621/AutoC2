# AutoC2
This is a script that will use the AWS API to build a T2.micro machine,
and deploy a C2 instance to it. The script is fully capable of creating
instances, generating a security group for the instance, and installing
the C2 of choice ready for engagement start.

## Requirements
This script does require the user to have AWS API keys and Python3. This
was developed and tested using Python 3.9.

## Supported C2
- PoshC2
- PowerShell Empire

## Usage
Ensure you have the proper packages and libraries.
`pip install -r requirements.txt`

Run the tool.
`python create_ec2_instance.py -h`