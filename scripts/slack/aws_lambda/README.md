# Slack - AWS Lambda Deployment

1. You need an AWS account and your AWS credentials set up on your machine.
2. Make sure you have an AWS IAM Role defined with the needed permissions for your Lambda function powering your Slack app:
    - Head to the AWS IAM section of AWS Console.
    - Click Roles from the menu.
    - Click the Create Role button.
    - Under "Select type of trusted entity", choose "AWS service".
    - Under "Choose a use case", select "Common use cases: Lambda".
    - Click "Next: Permissions".
    - Under "Attach permission policies", enter "lambda" in the Filter input.
    - Check the "AWSLambdaBasicExecutionRole", "AWSLambdaExecute" and "AWSLambdaRole" policies.
    - Click "Next: tags".
    - Click "Next: review".
    - Enter `lambda_slack_bot` as the Role name.
3. Ensure you have created an app on api.slack.com/apps as per the [Getting
   Started Guide](https://slack.dev/bolt-python/tutorial/getting-started).
   - Configure the slack app by copying the manifest in `config/slack/app_manifest.yaml`.
4. Ensure you have exported your Slack Bot Token and Slack Signing Secret for your
   apps as the environment variables `SLACK_BOT_TOKEN` and
   `SLACK_SIGNING_SECRET` in `.env` in the project root.
```bash
SLACK_SIGNING_SECRET= # Signing Secret from Basic Information page
SLACK_BOT_TOKEN= # Slack Bot Oath Token from Install App page
```
6. Let's deploy the Lambda. First set your AWS account id and region in the script. Now run `scripts/slack/aws_lambda/deploy.sh` (Important: run it from the root-folder).
7. Load up AWS Lambda inside the AWS Console - make sure you are in the correct region that you deployed your app to. You should see a `paperbot` Lambda there.
8. While your Lambda exists, it is not accessible to the internet, so Slack cannot send events happening in your Slack workspace to your Lambda. Let's fix that by adding an AWS Lambda Function URL to your Lambda so that your Lambda can accept HTTP requests:
    - Click on your `paperbot` Lambda.
    - In the Function Overview click "Configuration".
    - On the left side, click "Function URL".
    - Click "Create function URL".
    - Choose auth type "NONE".
    - Click "Save".
9. Congrats! Your Slack app is now accessible to the public. On the right side of your `paperbot` Function Overview you should see your Lambda Function URL.
10. Copy this URL to your clipboard.
11. We will now inform Slack that this app can accept Slash Commands.
    - Back on api.slack.com/apps, select your app and choose Slash Commands from the left menu.
    - Edit each command.
    - Under Request URL, paste in the previously-copied Lambda Function URL.
    - Click "Save".
12. Test it out! Back in your Slack workspace, try typing `/paperlike "attention is all you need"`.


