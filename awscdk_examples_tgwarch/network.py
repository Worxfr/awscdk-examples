from typing import Sequence
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    Aws
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
            tags= [cdk.CfnTag(key="Name", value=construct_id + "/MyVpc/vpc1sub2NonRoutable")]) 


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
            tags= [cdk.CfnTag(key="Name", value=construct_id + "/MyVpc2/vpc2sub2NonRoutable")])
        
        private_subnet2.add_dependency(vpc2cidr2)

        cfn_transit_gateway = ec2.CfnTransitGateway(self, "MyCfnTransitGateway",
        amazon_side_asn=64512,
        auto_accept_shared_attachments="enable",
        default_route_table_association="disable",
        default_route_table_propagation="disable",
        description="description",
        dns_support="enable",
        multicast_support="enable",
        #propagation_default_route_table_id="propagationDefaultRouteTableId",
        tags=[cdk.CfnTag(
            key="Name",
            value="TGWArch-TGW"
        )],
        #transit_gateway_cidr_blocks=["transitGatewayCidrBlocks"],
        vpn_ecmp_support="enable")

        cfn_transit_gateway_attachment = ec2.CfnTransitGatewayAttachment(self, "MyCfnTransitGatewayAttachment",
        subnet_ids=[private_subnet.attr_subnet_id],
        transit_gateway_id=cfn_transit_gateway.attr_id,
        vpc_id=vpc.vpc_id,
        # the properties below are optional
        #options=options,
        tags=[cdk.CfnTag(
            key="Name",
            value="TGWArch-TGWAttach1"
            )]
        )

        cfn_transit_gateway_attachment_2 = ec2.CfnTransitGatewayAttachment(self, "MyCfnTransitGatewayAttachment2",
        subnet_ids=[private_subnet2.attr_subnet_id],
        transit_gateway_id=cfn_transit_gateway.attr_id,
        vpc_id=vpc2.vpc_id,
        # the properties below are optional
        #options=options,
        tags=[cdk.CfnTag(
            key="Name",
            value="TGWArch-TGWAttach2"
            )]
        )

        cfn_transit_gateway_route_table = ec2.CfnTransitGatewayRouteTable(self, "MyCfnTransitGatewayRouteTable",
            transit_gateway_id=cfn_transit_gateway.attr_id,
            # the properties below are optional
            tags=[cdk.CfnTag(
                key="Name",
                value="tgwRT"
            )]
        )



        ec2.CfnTransitGatewayRouteTableAssociation(self, "MyCfnTransitGatewayRouteTableAssociation",
            transit_gateway_attachment_id=cfn_transit_gateway_attachment.attr_id,
            transit_gateway_route_table_id=cfn_transit_gateway_route_table.attr_transit_gateway_route_table_id)

        ec2.CfnTransitGatewayRouteTableAssociation(self, "MyCfnTransitGatewayRouteTableAssociation2",
            transit_gateway_attachment_id=cfn_transit_gateway_attachment_2.attr_id,
            transit_gateway_route_table_id=cfn_transit_gateway_route_table.attr_transit_gateway_route_table_id)

        cfn_transit_gateway_route = ec2.CfnTransitGatewayRoute(self, "MyCfnTransitGatewayRoute",
        destination_cidr_block="10.10.0.0/16",
        transit_gateway_route_table_id=cfn_transit_gateway_route_table.attr_transit_gateway_route_table_id,
        # the properties below are optional
        blackhole=False,
        transit_gateway_attachment_id=cfn_transit_gateway_attachment.attr_id 
        )

        cfn_transit_gateway_route_2 = ec2.CfnTransitGatewayRoute(self, "MyCfnTransitGatewayRoute2",
        destination_cidr_block="10.20.0.0/16",
        transit_gateway_route_table_id=cfn_transit_gateway_route_table.attr_transit_gateway_route_table_id,
        # the properties below are optional
        blackhole=False,
        transit_gateway_attachment_id=cfn_transit_gateway_attachment_2.attr_id 
        )

        vpc1select=vpc.select_subnets(subnet_filters=[ec2.SubnetFilter.by_cidr_ranges(["10.10.0.0/16"])])
        for subn in vpc1select.subnets :
            ec2.CfnRoute(self, 'tgwRoute',
            destination_cidr_block='10.20.0.0/16',
            route_table_id=subn.route_table.route_table_id,
            transit_gateway_id=cfn_transit_gateway.attr_id
            ).add_dependency(cfn_transit_gateway_attachment)

        vpc2select=vpc2.select_subnets(subnet_filters=[ec2.SubnetFilter.by_cidr_ranges(["10.20.0.0/16"])])
        for subn in vpc2select.subnets :
            ec2.CfnRoute(self, 'tgwRoute2',
            destination_cidr_block='10.10.0.0/16',
            route_table_id=subn.route_table.route_table_id,
            transit_gateway_id=cfn_transit_gateway.attr_id
            ).add_dependency(cfn_transit_gateway_attachment_2)

        # add private endpoints for session manager

        mySG = ec2.SecurityGroup(self, "security-group-VPCes",
            vpc=vpc,
            allow_all_outbound=True,
            description='CDK VPC Endp Security Group'
        )

        mySG.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), 'HTTPS frm anywhere')

        # add private endpoints for session manager
        ec2.CfnVPCEndpoint(self, 'ssm-vpce', 
            service_name="com.amazonaws."+Aws.REGION+".ssm",
            vpc_id=vpc.vpc_id,
            subnet_ids=[private_subnet.attr_subnet_id],
            security_group_ids=[mySG.security_group_id],
            vpc_endpoint_type='Interface',
            private_dns_enabled=True
        ).add_dependency(private_subnet)

        ec2.CfnVPCEndpoint(self, 'ssmmessages-vpce', 
            service_name="com.amazonaws."+Aws.REGION+".ssmmessages",
            vpc_id=vpc.vpc_id,
            subnet_ids=[private_subnet.attr_subnet_id],
            security_group_ids=[mySG.security_group_id],
            vpc_endpoint_type='Interface',
            private_dns_enabled=True
        ).add_dependency(private_subnet)

        ec2.CfnVPCEndpoint(self, 'ec2-vpce', 
            service_name="com.amazonaws."+Aws.REGION+".ec2",
            vpc_id=vpc.vpc_id,
            subnet_ids=[private_subnet.attr_subnet_id],
            security_group_ids=[mySG.security_group_id],
            vpc_endpoint_type='Interface',
            private_dns_enabled=True
        ).add_dependency(private_subnet)

        # add private endpoints for session manager
        mySG2 = ec2.SecurityGroup(self, "security-group-VPCes2",
            vpc=vpc2,
            allow_all_outbound=True,
            description='CDK VPC Endp Security Group'
        )

        mySG2.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), 'HTTPS frm anywhere')

        # add private endpoints for session manager
        ec2.CfnVPCEndpoint(self, 'ssm-vpce2', 
            service_name="com.amazonaws."+Aws.REGION+".ssm",
            vpc_id=vpc2.vpc_id,
            subnet_ids=[private_subnet2.attr_subnet_id],
            security_group_ids=[mySG2.security_group_id],
            vpc_endpoint_type='Interface',
            private_dns_enabled=True
        ).add_dependency(private_subnet2)

        ec2.CfnVPCEndpoint(self, 'ssmmessages-vpce2', 
            service_name="com.amazonaws."+Aws.REGION+".ssmmessages",
            vpc_id=vpc2.vpc_id,
            subnet_ids=[private_subnet2.attr_subnet_id],
            security_group_ids=[mySG2.security_group_id],
            vpc_endpoint_type='Interface',
            private_dns_enabled=True
        ).add_dependency(private_subnet2)

        ec2.CfnVPCEndpoint(self, 'ec2-vpce2', 
            service_name="com.amazonaws."+Aws.REGION+".ec2",
            vpc_id=vpc2.vpc_id,
            subnet_ids=[private_subnet2.attr_subnet_id],
            security_group_ids=[mySG2.security_group_id],
            vpc_endpoint_type='Interface',
            private_dns_enabled=True
        ).add_dependency(private_subnet2)

        # Create an EC2 instance

        myEC2SG = ec2.SecurityGroup(self, "security-group-VPCes-EC2",
            vpc=vpc,
            allow_all_outbound=True,
            description='CDK VPC Endp Security Group'
        )

        myEC2SG.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.icmp_ping(), 'icmp frm anywhere')

        instance = ec2.Instance(self, "EC2Instance VPC1",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            security_group=myEC2SG,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_filters=[ec2.SubnetFilter.by_cidr_ranges(["10.10.0.0/16"])])
        )

        # Create an EC2 instance
        myEC2SG2 = ec2.SecurityGroup(self, "security-group-VPCes-EC2-2",
            vpc=vpc2,
            allow_all_outbound=True,
            description='CDK VPC Endp Security Group'
        )

        myEC2SG2.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.icmp_ping(), 'icmp frm anywhere')

        instance2 = ec2.Instance(self, "EC2Instance VPC2",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            security_group=myEC2SG2,
            vpc=vpc2,
            vpc_subnets=ec2.SubnetSelection(subnet_filters=[ec2.SubnetFilter.by_cidr_ranges(["10.20.0.0/16"])])
        )

        
