import * as cdk from "aws-cdk-lib";
import { LambdaIntegration, RestApi } from "aws-cdk-lib/aws-apigateway";
import { Table } from "aws-cdk-lib/aws-dynamodb";
import { Subnet, Vpc } from "aws-cdk-lib/aws-ec2";
import {
  AssetCode,
  Code,
  Function,
  LayerVersion,
  Runtime,
} from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";
import { ALPHA_SESSION_DATA_TABLE_ARN } from "../constants/table-arn";
import { PythonFunction } from "@aws-cdk/aws-lambda-python-alpha";
import {
  Certificate,
  CertificateValidation,
} from "aws-cdk-lib/aws-certificatemanager";
import {
  ARecord,
  AaaaRecord,
  HostedZone,
  RecordSet,
  RecordTarget,
  RecordType,
} from "aws-cdk-lib/aws-route53";

export interface LambdaServiceStackProps extends cdk.StackProps {
  readonly stage: string;
  readonly vpc?: Vpc;
  readonly fargateServiceDnsName: string;
}

export class LambdaServiceStack extends cdk.Stack {
  public readonly vpc: Vpc;
  constructor(scope: Construct, id: string, props: LambdaServiceStackProps) {
    super(scope, id, props);

    const sessionDataTable = Table.fromTableArn(
      this,
      "GainGuardAthleteAnalyticsServiceSessionDataTable",
      ALPHA_SESSION_DATA_TABLE_ARN
    );

    // python lambda function
    const lambdaFunction = new PythonFunction(
      this,
      "GainGuardAthleteAnalyticsServiceLambda",
      {
        entry: "lambda", // required
        runtime: Runtime.PYTHON_3_11,
        index: "handler.py",
        handler: "handler",
        timeout: cdk.Duration.seconds(60),
        environment: {
          SESSION_DATA_TABLE_NAME: sessionDataTable.tableName,
          ML_MODEL_CONTAINER_DNS_NAME: props.fargateServiceDnsName,
        },
        layers: [
          new LayerVersion(
            this,
            "GainGuardAthleteAnalyticsServiceLambdaLayer",
            {
              code: Code.fromAsset("layers/python.zip"),
              compatibleRuntimes: [Runtime.PYTHON_3_11],
            }
          ),
        ],
      }
    );

    sessionDataTable.grantReadData(lambdaFunction);

    const api = new RestApi(this, "GainGuardAthleteAnalyticsServiceApi", {
      restApiName: "GainGuardAthleteAnalyticsServiceApi",
      description: "This service serves GainGuard Athlete Analytics",
      defaultCorsPreflightOptions: {
        allowOrigins: ["*"],
        allowMethods: ["*"],
        allowHeaders: ["*"],
      },
    });

    const lambdaIntegration = new LambdaIntegration(lambdaFunction, {
      requestTemplates: { "application/json": '{ "statusCode": "200" }' },
    });

    const rootHostedZone = HostedZone.fromHostedZoneAttributes(
      this,
      "RootHostedZone",
      {
        hostedZoneId: "Z05690503SGWP9QUT225O",
        zoneName: "gainguard.io",
      }
    );

    const endpointPrefix = `${props.stage.toLowerCase()}-athlete-analytics.api`;

    const certificate = new Certificate(
      this,
      "GainGuardAthleteAnalyticsECSCertificate",
      {
        domainName: `${endpointPrefix}.${rootHostedZone.zoneName}`,
        validation: CertificateValidation.fromDns(rootHostedZone),
      }
    );

    api.root.addMethod("POST", lambdaIntegration);

    const apiDomainName = api.addDomainName(
      "GainGuardAthleteAnalyticsServiceApiDomainName",
      {
        domainName: `${endpointPrefix}.${rootHostedZone.zoneName}`,
        certificate: certificate,
      }
    );

    new ARecord(this, "GainGuardAthleteAnalyticsServiceApiARecord", {
      zone: rootHostedZone,
      recordName: `${endpointPrefix}.${rootHostedZone.zoneName}`,
      target: RecordTarget.fromAlias({
        bind: () => ({
          dnsName: apiDomainName.domainNameAliasDomainName,
          hostedZoneId: apiDomainName.domainNameAliasHostedZoneId,
        }),
      }),
    });

    new AaaaRecord(this, "GainGuardAthleteAnalyticsServiceApiAaaaRecord", {
      zone: rootHostedZone,
      recordName: `${endpointPrefix}.${rootHostedZone.zoneName}`,
      target: RecordTarget.fromAlias({
        bind: () => ({
          dnsName: apiDomainName.domainNameAliasDomainName,
          hostedZoneId: apiDomainName.domainNameAliasHostedZoneId,
        }),
      }),
    });
  }
}
