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
```bash
usage: create_ec2_instance.py [-h] [-r REGION] [-i AMI] [-k KEY_NAME] [-n] [-g GROUP_NAME] [-b] [-c]
                              [-f {powershell-empire,poshc2}]

Creates AWS EC2 instances for on-demand C2 testing.

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        AWS region for deployment: us-east-1
  -i AMI, --ami AMI     AMI image id: ami-06fd113e1286dd166
  -k KEY_NAME, --keyname KEY_NAME
                        SSH keyname: aws_c2
  -n, --createkey       Create new AWS ssh keys: False
  -g GROUP_NAME, --group GROUP_NAME
                        Specify name for AWS security group: aws_c2
  -b, --build           Tells the script to build the machine using the other specified parameters
  -c, --config          Configure AWS instance using the provided ssh key SSH instance
  -f {powershell-empire,poshc2}, --framework {powershell-empire,poshc2}
                        Specifies which C2 framework to install on AWS instance: powershell-empire / poshc2
```