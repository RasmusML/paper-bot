# Deployment

1. Create a new Slack App using the following link: https://api.slack.com/apps
2. Configure the slack app by copying the manifest in `config/slack/app_manifest.yaml`
3. Add SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET to the AWS Lambda environment variables

3. Install the AWS CLI and configure it
4. Create execution role for the lambda function (AWSLambdaRole, AWSLambdaBasicExecutionRole, AWSLambdaExecute)
5. Update the configurations in `deploy.sh` file
6. Run the `deploy.sh` file
7. Create the URL endpoint in AWS lambda console (Configuration -> Function URL -> Create function URL)

8. Set the slash commands `Request URL` to the AWS Lambda endpoint



https://github.com/slackapi/bolt-python/blob/main/examples/aws_lambda/README.md

https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions