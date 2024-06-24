import { SecretValue, Stack, StackProps } from "aws-cdk-lib";
import {
  CodePipeline,
  CodePipelineSource,
  ShellStep,
} from "aws-cdk-lib/pipelines";
import { Construct } from "constructs";
import { ApplicationStage } from "./application-stage";

export class PipelineStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const pipeline = new CodePipeline(this, "Pipeline", {
      pipelineName: "GainGuardAthleteAnalyticsServicePipeline",
      synth: new ShellStep("Synth", {
        input: CodePipelineSource.gitHub(
          "GainGuard/GainGuardAthleteAnalyticsService",
          "main",
          {
            authentication: SecretValue.secretsManager(
              "arn:aws:secretsmanager:us-east-1:645332125184:secret:Master_GIT-oLzwZ6"
            ),
          }
        ),
        commands: [
          "npm i --legacy-peer-deps",
          "npm run build",
          "npx cdk --version",
          "npx cdk synth",
        ],
      }),
      dockerEnabledForSelfMutation: true,
      dockerEnabledForSynth: true,
    });

    const alphaStage = pipeline.addStage(
      new ApplicationStage(this, "Alpha", {
        env: props?.env, // in the future you might want to have different environments
      })
    );

    // TODO: add integration tests

    // https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html
  }
}
