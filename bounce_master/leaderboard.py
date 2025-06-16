import boto3
import json
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

class Leaderboard:
    def __init__(self, table_name='BounceGameLeaderboard', region='us-east-1'):
        """Initialize the leaderboard with AWS DynamoDB table"""
        self.table_name = table_name
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.table = self.dynamodb.Table(self.table_name)
    
    def create_table_if_not_exists(self):
        """Create the DynamoDB table if it doesn't exist"""
        try:
            # Check if table exists
            self.dynamodb.meta.client.describe_table(TableName=self.table_name)
            print(f"Table {self.table_name} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create the table
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
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
                table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
                print(f"Created table {self.table_name}")
            else:
                raise
    
    def submit_score(self, player_name, score):
        """Submit a score to the leaderboard"""
        try:
            # Generate a unique ID for the player
            player_id = str(uuid.uuid4())
            
            # Add the score to the leaderboard
            response = self.table.put_item(
                Item={
                    'player_id': player_id,
                    'player_name': player_name,
                    'score': score,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            print(f"Added score {score} for player {player_name}")
            return True
        except Exception as e:
            print(f"Error submitting score: {e}")
            return False
    
    def get_top_scores(self, limit=10):
        """Get the top scores from the leaderboard"""
        try:
            # Scan the table and sort by score in descending order
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Sort by score (descending)
            sorted_items = sorted(items, key=lambda x: x['score'], reverse=True)
            
            # Return the top N scores
            return sorted_items[:limit]
        except Exception as e:
            print(f"Error getting top scores: {e}")
            return []

# Helper function to initialize the leaderboard
def initialize_leaderboard():
    leaderboard = Leaderboard()
    leaderboard.create_table_if_not_exists()
    return leaderboard
