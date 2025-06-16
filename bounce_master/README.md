# Bounce Master Game

A fun arcade-style game built with PyGame where you control a paddle to keep balls from falling off the screen while avoiding obstacles and collecting power-ups.

## Features

- Player-controlled paddle
- Physics-based ball bouncing
- Flying obstacles that change ball trajectory
- Multiple power-ups with different effects:
  - Speed boost: Makes the player paddle move faster
  - Size increase: Makes the player paddle wider
  - Ball slowdown: Reduces the ball's speed
  - Multi-ball: Adds additional balls to the game
  - Anti-gravity: Makes the ball float upward slightly
- Global leaderboard using AWS API Gateway, Lambda, and DynamoDB

## Requirements

- Python 3.6+
- PyGame
- Requests library (for API calls)
- AWS account (for deploying the leaderboard backend)

## Setup

### 1. Install Required Packages

```bash
pip install pygame requests
```

### 2. Deploy the AWS Backend

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

This will:
- Create a CloudFormation stack with API Gateway, Lambda functions, and DynamoDB
- Generate a config.py file with your API endpoint and API key

### 3. Run the Game

```bash
python main.py
```

## Game Controls

- **Left/Right Arrow Keys**: Move the paddle
- **ESC**: Quit the game
- **SPACE**: Restart after game over or submit score
- **Enter**: Submit your name to the leaderboard

## AWS Architecture

The game uses a serverless architecture for the leaderboard:

1. **API Gateway**: Provides HTTP endpoints for submitting scores and retrieving top scores
2. **Lambda Functions**: Process requests and interact with DynamoDB
3. **DynamoDB**: Stores player scores
4. **API Key Authentication**: Secures the API endpoints

## Security Considerations

- The API key is stored in the config.py file, which is generated during deployment
- API Gateway enforces rate limiting to prevent abuse
- No AWS credentials are stored in the game code

## Customization

You can modify various game parameters in the code:
- Paddle size and speed
- Ball physics (gravity, bounce angles)
- Power-up effects and duration
- Obstacle spawn rate and behavior

## Files

- `main.py`: Main game loop and rendering
- `leaderboard_api.py`: Client for interacting with the leaderboard API
- `template.yaml`: CloudFormation template for AWS resources
- `deploy.sh`: Deployment script for AWS resources
- `config.py`: Generated configuration file with API details
