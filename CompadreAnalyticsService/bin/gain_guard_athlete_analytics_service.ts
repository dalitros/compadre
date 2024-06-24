#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { PipelineStack } from "../lib/pipeline-stack";

const app = new cdk.App();
new PipelineStack(app, "GainGuardAthleteAnalyticsServicePipelineStack", {
  env: {
    account: "645332125184",
    region: "us-east-1",
  },
});

app.synth();
