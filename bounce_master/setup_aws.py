import boto3
import json
import sys
from botocore.exceptions import ClientError

def create_dynamodb_table(table_name='BounceGameLeaderboard', region='us-east-1'):
    """
    Creates a DynamoDB table for the game leaderboard if it doesn't exist.
    
    Args:
        table_name (str): Name of the DynamoDB table
        region (str): AWS region
        
    Returns:
        bool: True if table was created or already exists, False otherwise
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=region)
        
        # Check if table already exists
        try:
            dynamodb.meta.client.describe_table(TableName=table_name)
            print(f"Table {table_name} already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise
        
        # Create the table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'player_id', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'score', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'player_id', 'AttributeType': 'S'},
                {'AttributeName': 'score', 'AttributeType': 'N'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'ScoreIndex',
                    'KeySchema': [
                        {'AttributeName': 'score', 'KeyType': 'HASH'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ]
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Created table {table_name}")
        return True
        
    except Exception as e:
        print(f"Error creating DynamoDB table: {e}")
        return False

def check_aws_credentials():
    """
    Checks if AWS credentials are properly configured.
    
    Returns:
        bool: True if credentials are configured, False otherwise
    """
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            print("AWS credentials not found. Please configure your AWS credentials.")
            print("Run 'aws configure' or set up credentials in ~/.aws/credentials")
            return False
            
        # Test credentials by making a simple API call
        sts = boto3.client('sts')
        sts.get_caller_identity()
        
        print("AWS credentials are properly configured.")
        return True
        
    except Exception as e:
        print(f"Error checking AWS credentials: {e}")
        return False

def main():
    print("Setting up AWS resources for Bounce Master game...")
    
    # Check AWS credentials
    if not check_aws_credentials():
        sys.exit(1)
    
    # Create DynamoDB table
    if create_dynamodb_table():
        print("\nAWS setup completed successfully!")
        print("You can now run the game with: python main.py")
    else:
        print("\nAWS setup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
