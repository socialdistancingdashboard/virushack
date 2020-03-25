#!/bin/bash
RESSOURCE="SddApiDbGetSpatialData"
STACK="sdd-get-spatial-data"

# build 
sam build --use-container

# remove dist infos to avoid aws think dependencies are missing
rm -r .aws-sam/build/$RESSOURCE/*.dist-info

# package and upload
sam package \
  --template-file .aws-sam/build/$RESSOURCE/template.yaml \
  --s3-prefix $STACK \
  --s3-bucket sdd-s3-basebucket \
  --output-template-file .aws-sam/build/$RESSOURCE/packaged.yaml

# deploy
sam deploy \
  --template-file .aws-sam/build/$RESSOURCE/packaged.yaml \
  --stack-name $STACK \
  --capabilities CAPABILITY_IAM \
  --region eu-central-1 
