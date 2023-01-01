from pydoc import describe
import boto3
import botocore
import os
import time
import paramiko.client as paramiko
import argparse

os.environ["AWS_ACCESS_KEY_ID"] = "REMOVED" # EDIT ACCORDINGLY
os.environ["AWS_SECRET_ACCESS_KEY"] = "REMOVED" # EDIT ACCORDINGLY

def generate_keypair(region:str, keyname="aws_c2"):
    ec2 = boto3.client('ec2', region)

    # Checks if there exist any keys within AWS with the same keyname
    
    try:
        key = ec2.describe_key_pairs(KeyNames=[keyname])['KeyPairs']

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
            key = ec2.create_key_pair(KeyName=keyname)
            with open("%s.pem" %(keyname),"w") as file:
                file.write (key['KeyMaterial'])
            print("Successfully generated key pair")
        else:
            raise

def delete_keypair(region:str,keyname: str):
    ec2 = boto3.client('ec2', region)
    ec2.delete_key_pair(KeyName=keyname)
    print("Successfully removed keypair")

def get_instance_status(region:str):
    ec2 = boto3.client('ec2',region)
    instance_filter = ec2.describe_instances(Filters=[{
                                            'Name':'instance-state-name',
                                            'Values':['running']}])['Reservations'][0]['Instances']
    print("INSTANCE ID\t\tPUBLIC IP\tPRIVATE IP")
    for instance in instance_filter:
        print(instance['InstanceId'] + "\t"
            + instance['PublicIpAddress'] + "\t"
            + instance['PrivateIpAddress'])

def build_instance( region: str,
                    ami:str,
                    keyname: str,
                    group_name: str,
                    instance_type="t2.micro"):
    
    ec2 = boto3.client('ec2', region)

    # Checks if the security group is created, and if not creates one
    try:
        group = ec2.describe_security_groups(GroupNames=[group_name])
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
            ec2.create_security_group(GroupName=group_name,
                                            Description="AWS Red Team C2 testing")
            ec2.authorize_security_group_ingress(GroupName=group_name, IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0') # Enable SSH to the C2 server
            ec2.authorize_security_group_ingress(GroupName=group_name, IpProtocol='tcp', FromPort=80, ToPort=80, CidrIp='0.0.0.0/0') # Enable HTTP to the server for hosting files and comms
            ec2.authorize_security_group_ingress(GroupName=group_name, IpProtocol='tcp', FromPort=443, ToPort=443, CidrIp='0.0.0.0/0') # Enable HTTPS to the server for hosting files and comms
            ec2.authorize_security_group_ingress(GroupName=group_name, IpProtocol='tcp', FromPort=8080, ToPort=8080, CidrIp='0.0.0.0/0') # Enable HTTP Proxy for tunneling when/if needed
        else:
            raise
    
    instance = ec2.run_instances(ImageId=ami,
                                 KeyName=keyname,
                                 SecurityGroupIds=[group_name],
                                 InstanceType=instance_type,
                                 MinCount=1,
                                 MaxCount=1)

    print("Successfully issued build commands. Waiting for IP address.")
    print("Building immage, this may take a while (No longer than 5 minutes).")

    while instance['Instances'][0]['State']['Name'] != 'running':
        time.sleep(30)
        instance = ec2.describe_instances(Filters=[{
                                            'Name':'network-interface.group-name',
                                            'Values':[group_name]
                                            }])['Reservations'][0]
    
    print("You can now login to the machine with ssh at the following IP address: %s" % instance['Instances'][0]['PublicIpAddress'])


def delete_instance(instance_id: str, region:str):
    ec2 = boto3.client('ec2',region)
    print("Terminating instance")
    ec2.terminate_instances(InstanceIds=[instance_id])
    time.sleep(15)

def configure_instance(c2: str,
                        ext_ip: str,
                        key_name: str):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(ext_ip,
                  username='kali',
                  key_filename=key_name
                  )
    std_input, std_output, std_error = ssh_client.exec_command("sudo apt-get update && \
                                                                sudo apt-get install %s" % (c2),get_pty=True)
    std_input.write('kali')
    
    for x in std_output:
        print(x)
    for x in std_error:
        print(x)
    ssh_client.close()

def main():
    args = parser.parse_args()
    if args.help:
        parser.print_help()

    if args.createkey:
        generate_keypair(keyname=args.key_name, region=args.REGION)
    
    if args.build:
        build_instance(region=args.REGION, ami=args.AMI, keyname=args.key_name, group_name=args.group_name)
        print("Allowing instance to finalize initialization.")
        time.sleep(10)

    if args.config:
        print("Configuring instance")
        configure_instance(c2=args.c2,ext_ip=args.ip,)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates AWS EC2 instances for on-demand C2 testing.')
    parser.add_argument('-r','--region',type=str,dest='REGION',default="us-east-1",help="AWS region for deployment: us-east-1")
    parser.add_argument('-i','--ami',type=str,dest='AMI',default="ami-06fd113e1286dd166",help="AMI image id: ami-06fd113e1286dd166")
    parser.add_argument('-k','--keyname',type=str,dest='key_name',default="aws_c2",help="SSH keyname: aws_c2")
    parser.add_argument('-n','--createkey',action='store_true',help="Create new AWS ssh keys: False")
    parser.add_argument('-g','--group',type=str,dest='group_name',default="aws_c2",help="Specify name for AWS security group: aws_c2")
    parser.add_argument('-b','--build',action='store_true',help="Tells the script to build the machine using the other specified parameters")
    parser.add_argument('-c','--config',action='store_true',help="Configure AWS instance using the provided ssh key SSH instance")
    parser.add_argument('-f','--framework',dest='c2',choices=["powershell-empire","poshc2"], help="Specifies which C2 framework to install on AWS instance: powershell-empire / poshc2")
    main()

    # generate_keypair()
    # build_instance()
    # delete_keypair("us-east-1")
    # get_instance_status()
    # delete_instance('i-0ae81973075a67c70')
    # configure_instance("empire",ip="3.82.174.138")