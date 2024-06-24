import * as cdk from "aws-cdk-lib";
import { InterfaceVpcEndpointAwsService, Vpc } from "aws-cdk-lib/aws-ec2";
import { Construct } from "constructs";
import { ApplicationLoadBalancedFargateService } from "aws-cdk-lib/aws-ecs-patterns";
import { AssetImage } from "aws-cdk-lib/aws-ecs";
import { ApplicationProtocol } from "aws-cdk-lib/aws-elasticloadbalancingv2";

import { ARecord, HostedZone, RecordTarget } from "aws-cdk-lib/aws-route53";
import {
  Certificate,
  CertificateValidation,
} from "aws-cdk-lib/aws-certificatemanager";

export interface ModelContainerStackProps extends cdk.StackProps {
  readonly stage: string;
}

export class ModelContainerStack extends cdk.Stack {
  public readonly vpc: Vpc;
  public readonly fargateServiceDnsName: string;

  constructor(scope: Construct, id: string, props: ModelContainerStackProps) {
    super(scope, id, props);

    this.vpc = new Vpc(this, "GainGuardAthleteAnalyticsServiceVpc", {});

    this.vpc.addInterfaceEndpoint("GainGuardAthleteAnalyticsApiGwEndpoint", {
      service: InterfaceVpcEndpointAwsService.APIGATEWAY,
      privateDnsEnabled: true,
      open: true,
    });

    this.vpc.addInterfaceEndpoint("GainGuardAthleteAnalyticsEcrEndpoint", {
      service: InterfaceVpcEndpointAwsService.ECR,
      privateDnsEnabled: true,
      open: true,
    });

    this.vpc.addInterfaceEndpoint(
      "GainGuardAthleteAnalyticsEcrDockerEndpoint",
      {
        service: InterfaceVpcEndpointAwsService.ECR_DOCKER,
        privateDnsEnabled: true,
        open: true,
      }
    );

    this.vpc.addInterfaceEndpoint("GainGuardAthleteAnalyticsECSEndpoint", {
      service: InterfaceVpcEndpointAwsService.ECS,
      privateDnsEnabled: true,
      open: true,
    });

    const fargate = new ApplicationLoadBalancedFargateService(
      this,
      "GainGuardAthleteAnalyticsServiceFargateApp",
      {
        vpc: this.vpc,
        taskImageOptions: {
          image: new AssetImage("service"),
          containerPort: 8000,
        },
        cpu: 2048,
        memoryLimitMiB: 8192,
        publicLoadBalancer: true,
        // certificate: certificate,
        // domainZone: rootHostedZone,
        // domainName: `${endpointPrefix}.${rootHostedZone.zoneName}`,
        protocol: ApplicationProtocol.HTTP,
      }
    );

    this.fargateServiceDnsName = fargate.loadBalancer.loadBalancerDnsName;
  }
}
