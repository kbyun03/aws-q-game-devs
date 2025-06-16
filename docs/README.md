# Building a PyGame Game with AWS Integration: The Bounce Master Journey

## Introduction

In this post, I'll share my experience creating "Bounce Master," a fun arcade-style game built with PyGame and integrated with AWS services for a global leaderboard. This project was
developed during an Amazon Q CLI event, where I collaborated with Amazon Q to build a game from scratch in just a few hours.

## The Game Concept

Bounce Master is inspired by classic volleyball games but with a twist. The player controls a paddle at the bottom of the screen and must keep balls from touching the ground. To make
things interesting, obstacles fly across the screen that can alter the ball's trajectory upon collision. The game also features power-ups that provide various effects like making the
player faster, duplicating balls, giving balls temporary anti-gravity abilities, or slowing down ball movement.

## Development Process

### Starting with the Core Game Mechanics

We began by setting up the basic PyGame structure and implementing the core game mechanics:

python
class Player:
    def __init__(self):
        self.width = 200  # Wider paddle for easier gameplay
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 8
        self.color = BLUE
        # ... other initialization code ...

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.move("left")
        if keys[pygame.K_RIGHT]:
            self.move("right")


The ball physics were implemented with realistic bouncing behavior, including gravity effects:

python
class Ball:
    def __init__(self, x=None, y=None):
        self.radius = 15
        self.x = x if x is not None else SCREEN_WIDTH // 2
        self.y = y if y is not None else SCREEN_HEIGHT // 2
        self.speed_x = random.choice([-4, -3, 3, 4])
        self.speed_y = -5
        self.gravity = 0.2
        # ... other initialization code ...

    def update(self):
        # Apply gravity
        self.speed_y += self.gravity

        # Update position
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off walls and ceiling
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.speed_x *= -1

        if self.y <= self.radius:
            self.speed_y *= -1


### Adding Power-Ups

To make the game more dynamic, we implemented various power-ups:

python
class PowerUp:
    def __init__(self):
        # ... initialization code ...

        # Choose a random power-up type
        self.types = ["speed", "size", "slow", "multiball", "antigravity"]
        self.type = random.choice(self.types)

        # Set color based on type
        if self.type == "speed":
            self.color = YELLOW  # Speed boost
        elif self.type == "size":
            self.color = CYAN    # Paddle size increase
        # ... other power-up types ...


Each power-up has a unique effect when collected:

python
# Apply power-up effect
if power_up.type == "speed" or power_up.type == "size":
    player.apply_power_up(power_up.type)
elif power_up.type == "slow" or power_up.type == "antigravity":
    for ball in balls:
        ball.apply_power_up(power_up.type)
elif power_up.type == "multiball" and len(balls) < 3:  # Limit to 3 balls max
    # Create a new ball at a random position
    new_ball = Ball(
        x=random.randint(50, SCREEN_WIDTH - 50),
        y=random.randint(100, 300)
    )
    balls.append(new_ball)


## AWS Integration: Creating a Global Leaderboard

One of the most interesting aspects of this project was integrating AWS services to create a global leaderboard. We initially considered direct DynamoDB access but realized this would
require distributing AWS credentials with the game, which is a security risk.

Instead, we implemented a more secure architecture using:
• API Gateway as an intermediary
• Lambda functions to process requests
• DynamoDB for data storage
• API key authentication for security

### CloudFormation Template

We created a comprehensive CloudFormation template to set up all the required AWS resources:

yaml
# API Gateway REST API
LeaderboardAPI:
  Type: AWS::ApiGateway::RestApi
  Properties:
    Name: BounceGameLeaderboardAPI
    Description: API for Bounce Master game leaderboard
    EndpointConfiguration:
      Types:
        - REGIONAL
    ApiKeySourceType: HEADER


The Lambda functions handle score submission and retrieval:

python
def submit_score_handler(event, context):
    try:
        # Parse request body
        body = json.loads(event['body'])
        player_name = body.get('player_name', 'Anonymous')
        score = int(body.get('score', 0))

        # Generate a unique ID for the player
        player_id = str(uuid.uuid4())

        # Add the score to the leaderboard
        table.put_item(
            Item={
                'player_id': player_id,
                'player_name': player_name,
                'score': score,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Score submitted successfully'})
        }
    except Exception as e:
        # Error handling...


### Client-Side API Integration

On the game side, we created a client to interact with the API:

python
class LeaderboardAPI:
    def __init__(self, api_endpoint=None, api_key=None):
        """Initialize the leaderboard API client"""
        self.api_endpoint = api_endpoint or os.environ.get('LEADERBOARD_API_ENDPOINT')
        self.api_key = api_key or os.environ.get('LEADERBOARD_API_KEY')

    def submit_score(self, player_name, score):
        """Submit a score to the leaderboard via API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "player_name": player_name,
            "score": score
        }
        # API call implementation...


## Challenges and Solutions

### Challenge 1: Secure Leaderboard Implementation

Initially, we considered direct DynamoDB access from the game, but this would require distributing AWS credentials. We solved this by implementing an API Gateway with API key
authentication, which is much more secure.

### Challenge 2: CloudFormation Deployment Issues

We encountered issues with resource dependencies in our CloudFormation template. The solution was to add explicit DependsOn attributes to ensure resources were created in the correct
order:

yaml
LeaderboardUsagePlan:
  Type: AWS::ApiGateway::UsagePlan
  DependsOn:
    - LeaderboardAPI
    - LeaderboardAPIDeployment
  Properties:
    # ... properties ...


### Challenge 3: JSON Serialization in Lambda

We faced issues with DynamoDB's Decimal type not being JSON serializable. We solved this by implementing a custom JSON encoder:

python
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj) if obj % 1 != 0 else int(obj)
        return super(DecimalEncoder, self).default(obj)


### Challenge 4: CORS for Web Integration

To make the game embeddable in a blog, we needed to add CORS support to our API:

yaml
ScoresResourceCORS:
  Type: AWS::ApiGateway::Method
  Properties:
    AuthorizationType: NONE
    HttpMethod: OPTIONS
    ResourceId: !Ref ScoresResource
    RestApiId: !Ref LeaderboardAPI
    Integration:
      Type: MOCK
      IntegrationResponses:
        - StatusCode: 200
          ResponseParameters:
            method.response.header.Access-Control-Allow-Headers: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
            method.response.header.Access-Control-Allow-Methods: "'POST,OPTIONS'"
            method.response.header.Access-Control-Allow-Origin: "'*'"


## Cost Analysis

One of the benefits of our serverless architecture is its cost-effectiveness. For a game with approximately 100 players over a week:

• API Gateway: ~$0.03
• Lambda: $0.00 (covered by free tier)
• DynamoDB: ~$0.01
• CloudWatch Logs: ~$0.005

Total estimated cost: ~$0.05 per week

## Conclusion

Building Bounce Master was a fun and educational experience. The combination of PyGame for game development and AWS services for the backend provided a great opportunity to create
something engaging while learning about game physics, power-up systems, and cloud integration.

The project demonstrates how even simple games can be enhanced with cloud features like global leaderboards, and how modern serverless architectures can make these integrations cost-
effective and secure.

The complete code for this project is available on GitHub, and I encourage you to try it out, make modifications, and perhaps even embed it in your own blog using the web integration
features we added.

Happy gaming and coding!