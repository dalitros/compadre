import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { LambdaServiceStack } from "./lambda-service-stack";
import { ModelContainerStack } from "./model-container-stack";

export class ApplicationStage extends cdk.Stage {
  constructor(scope: Construct, id: string, props?: cdk.StageProps) {
    super(scope, id, props);

    const modelContainerStack = new ModelContainerStack(
      this,
      "GainGuardAthleteAnalyticsModelContainerStack",
      {
        stage: id,
      }
    );

    const lambdaStack = new LambdaServiceStack(
      this,
      "GainGuardAthleteAnalyticsServiceStack",
      {
        stage: id,
        vpc: modelContainerStack.vpc,
        fargateServiceDnsName: modelContainerStack.fargateServiceDnsName,
      }
    );
  }
}
