#!/usr/bin/env python3
import os

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
from awscdk_examples_tgwarch.awscdk_examples_tgwarch_stack import CdkTGW
from constructs import Construct


app = cdk.App()

CdkTGW(app, "tgwarchstack",)

app.synth()
