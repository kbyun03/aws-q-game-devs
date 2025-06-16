#!/bin/bash

# Deploy CloudFormation stack for Bounce Master leaderboard API
STACK_NAME="bounce-master-leaderboard"
REGION="us-east-1"  # Change this to your preferred region

echo "Deploying CloudFormation stack: $STACK_NAME in region $REGION"

# Deploy the CloudFormation stack
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# Check if deployment was successful
if [ $? -eq 0 ]; then
  echo "Stack deployed successfully!"
  
  # Get the API endpoint URL
  API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text \
    --region $REGION)
  
  # Get the API key ID
  API_KEY_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='ApiKeyId'].OutputValue" \
    --output text \
    --region $REGION)
  
  # Get the actual API key value
  API_KEY=$(aws apigateway get-api-key \
    --api-key $API_KEY_ID \
    --include-value \
    --query "value" \
    --output text \
    --region $REGION)
  
  echo ""
  echo "API Endpoint: $API_ENDPOINT"
  echo "API Key: $API_KEY"
  
  # Create a config file for the game
  echo "Creating config file with API details..."
  cat > config.py << EOL
# Bounce Master API Configuration
# Generated automatically by deploy.sh

API_ENDPOINT = "$API_ENDPOINT"
API_KEY = "$API_KEY"
EOL
  
  echo ""
  echo "Configuration saved to config.py"
  echo "You can now run the game with: python main.py"
  
else
  echo "Stack deployment failed. Check the AWS CloudFormation console for details."
fi
