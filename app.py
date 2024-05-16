#!/usr/bin/env python3
import os

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import awscdk_examples_tgwarch_stack
from constructs import Construct


app = cdk.App()

awscdk_examples_tgwarch_stack(app, "awscdk_examples_tgwarch_stack",)

app.synth()
