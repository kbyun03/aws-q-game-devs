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
- Global leaderboard using AWS DynamoDB

## Requirements

- Python 3.6+
- PyGame
- AWS account with appropriate permissions
- Boto3 (AWS SDK for Python)

## Setup

1. Make sure you have Python installed
2. Install required packages:
   ```
   pip install pygame boto3
   ```
3. Configure AWS credentials:
   ```
   aws configure
   ```
   Or set up credentials in `~/.aws/credentials`

## Running the Game

```
python main.py
```

## Game Controls

- **Left/Right Arrow Keys**: Move the paddle
- **ESC**: Quit the game
- **SPACE**: Restart after game over or submit score

## Leaderboard Setup

The game uses AWS DynamoDB to store and retrieve leaderboard data. The table will be created automatically when you run the game for the first time if it doesn't exist.

Required AWS permissions:
- dynamodb:CreateTable
- dynamodb:DescribeTable
- dynamodb:PutItem
- dynamodb:Scan

## Game Architecture

- `main.py`: Main game loop and rendering
- `leaderboard.py`: AWS DynamoDB integration for the global leaderboard

## Customization

You can modify various game parameters in the code:
- Paddle size and speed
- Ball physics (gravity, bounce angles)
- Power-up effects and duration
- Obstacle spawn rate and behavior
