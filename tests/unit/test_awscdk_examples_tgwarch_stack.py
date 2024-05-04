import aws_cdk as core
import aws_cdk.assertions as assertions

from awscdk_examples_tgwarch.awscdk_examples_tgwarch_stack import AwscdkExamplesTgwarchStack

# example tests. To run these tests, uncomment this file along with the example
# resource in awscdk_examples_tgwarch/awscdk_examples_tgwarch_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwscdkExamplesTgwarchStack(app, "awscdk-examples-tgwarch")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
