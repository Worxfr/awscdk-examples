from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
from constructs import Construct

class CdkTGW(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        vpc = ec2.Vpc(self, "MyVpc",
                      max_azs=1,
                      ip_addresses=ec2.IpAddresses.cidr("10.10.0.0/16"),
                      subnet_configuration=[ec2.SubnetConfiguration(
                          subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                          name="vpc1sub1Routable",
                          cidr_mask=24
                      )]
        )

        vpc1cidr2 = ec2.CfnVPCCidrBlock(self, "VPC1CIDR2",
            vpc_id=vpc.vpc_id,
            cidr_block="100.64.0.0/16"
        )

        private_subnet = ec2.CfnSubnet(self, "vpc1sub2NonRoutable",
            availability_zone=vpc.availability_zones[0],
            cidr_block="100.64.0.0/24",
            vpc_id=vpc.vpc_id,
            tags= [cdk.CfnTag(key="Name", value="Tgwarch/MyVpc/vpc1sub2NonRoutable")]) 


        private_subnet.add_dependency(vpc1cidr2)
        

        vpc2 = ec2.Vpc(self, "MyVpc2",
                max_azs=1,
                ip_addresses=ec2.IpAddresses.cidr("10.20.0.0/16"),
                subnet_configuration=[ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    name="vpc2sub1Routable",
                    cidr_mask=24
                )]
        )
        vpc2cidr2 = ec2.CfnVPCCidrBlock(self, "VPC2CIDR2",
            vpc_id=vpc2.vpc_id,
            cidr_block="100.64.0.0/16"
        )

        private_subnet2 = ec2.CfnSubnet(self, 
            "vpc2sub2NonRoutable",
            availability_zone=vpc2.availability_zones[0],
            cidr_block="100.64.0.0/24",
            vpc_id=vpc2.vpc_id,
            tags= [cdk.CfnTag(key="Name", value="Tgwarch/MyVpc2/vpc2sub2NonRoutable")])
        
        private_subnet2.add_dependency(vpc2cidr2)