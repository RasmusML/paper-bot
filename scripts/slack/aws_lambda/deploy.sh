
### CHANGE THESE ###
AWS_ACCOUNT_ID=111222333444
REGION=eu-central-1
ROLE_NAME=lambda_slack_bot

### DO NOT CHANGE ###
AWS_REPOSITORY_NAME=paperbot
ECR_REPOSITORY_URI=${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${AWS_REPOSITORY_NAME}

# sign in to ECR and create a repository for the image
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
aws ecr create-repository --repository-name ${AWS_REPOSITORY_NAME} --region ${REGION} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

# Copy the Dockerfile to the root of the project
cp scripts/slack/aws_lambda/Dockerfile .

# push the image to ECR
docker build --platform linux/amd64 -t docker-image:test .
docker tag docker-image:test ${ECR_REPOSITORY_URI}:latest
docker push ${ECR_REPOSITORY_URI}:latest

# create the lambda function
aws lambda create-function \
  --function-name ${AWS_REPOSITORY_NAME} \
  --package-type Image \
  --code ImageUri=${ECR_REPOSITORY_URI}:latest \
  --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}


### If you want to update the code, use the following command
#aws lambda update-function-code \
#  --function-name ${AWS_REPOSITORY_NAME} \
#  --image-uri ${ECR_REPOSITORY_URI}:latest \
#  --publish

# clean up
rm Dockerfile
