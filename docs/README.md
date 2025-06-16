# Build Games with Amazon Q CLI

## Installing PreRequisits
https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-installing.html
https://www.pygame.org/wiki/GettingStarted

## Getting Started
1. Chat with Q to get some ideas
```
> I am participating Amazon Q cli event, where we are trying to develop a game using Amazon Q and PyGame. I do not have experience in PyGame Framework but I have AWS experience. Let's start by picking concept of game. I want this game to be simple to make (around 2-4 hour development time) and good introduction to PyGame framework and game development. Suggest a good starting point and good ganre to make with PyGame
I'd be happy to help you develop a simple game using PyGame! Given your constraints (2-4 hour development time) and being new to PyGame, let's focus on something achievable yet
educational.

## Game Concept Suggestions

For beginners to PyGame, these genres work particularly well:

1. Arcade-style games - Simple mechanics, clear objectives
2. Puzzle games - Focus on logic rather than complex graphics
3. Simple platformers - Basic movement and collision detection

My recommendation would be a Space Shooter game for these reasons:
• Classic arcade style with straightforward mechanics
• Covers fundamental PyGame concepts (sprites, collision, input handling)
• Visually rewarding even with simple graphics
• Easily expandable if you want to add features later
• Perfect for a 2-4 hour development window

## Starting Point

Here's how we can approach this:

1. Setup PyGame environment
2. Create a basic game window
3. Add player ship with movement controls
4. Implement enemies and basic shooting mechanics
5. Add collision detection and scoring
6. Polish with simple sounds and visual effects

Let's start by checking if you have PyGame installed and setting up our project structure:


🛠️  Using tool: execute_bash
 ⋮
 ● I will run the following shell command:
mkdir -p space_shooter && cd space_shooter && python3 -m pip install pygame --user 2>&1 || echo "Failed to install pygame"
 ⋮
 ↳ Purpose: Creating project directory and installing PyGame


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> Let's do something other than space shooter. I think its bit too common. Let's do something similar to Pikachu Volleyball. Where there is a ball and player. and player's goal is to keep the ball away from touching the ground. To make things interesting, there will be obstacles flying towards to ball and upon collison, it will changes ball's trajectory. Maybe we can have some items to make player faster, duplicate balls, give ball temporary flying ability, moving ball slower etc.
That's a fantastic and creative idea! A Pikachu Volleyball-inspired game with obstacles and power-ups sounds both fun and achievable within your 2-4 hour timeframe. It's also a great way
to learn PyGame fundamentals while creating something more unique than a space shooter.

Let's outline this volleyball-style game:

## Game Concept: Bounce Master

Core Mechanics:
• Player controls a paddle/character at the bottom of the screen
• Ball bounces around the screen
• Player must prevent the ball from touching the ground
• Obstacles fly across the screen that can alter the ball's trajectory
• Power-ups appear randomly to help the player

Power-ups:
• Speed boost: Makes the player move faster temporarily
• Ball slowdown: Reduces ball speed temporarily
• Multi-ball: Creates duplicate balls
• Anti-gravity: Ball hovers instead of falling for a few seconds
• Paddle size increase: Makes your paddle larger temporarily

## Development Plan

1. Setup the game window and basic physics
2. Create the player paddle with movement controls
3. Implement the ball with bouncing physics
4. Add collision detection between ball, paddle, and screen edges
5. Create obstacles that fly across the screen
6. Implement power-ups and their effects
7. Add scoring system and game over conditions
8. Polish with simple sounds and visual effects

Would you like me to help you start setting up this game? I can create the initial structure and basic game elements to get you going.
Great! Let's start building our Bounce Master game. I'll help you set up the initial structure and implement the basic game elements.

First, let's create a project directory and install PyGame:


🛠️  Using tool: execute_bash
 ⋮
 ● I will run the following shell command:
mkdir -p bounce_master && cd bounce_master && python3 -m pip install pygame --user 2>&1 || echo "Failed to install pygame"
 ⋮
 ↳ Purpose: Creating project directory and installing PyGame


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:
It looks like we're in a virtual environment where user installations aren't visible. Let's try installing PyGame without the --user flag:


🛠️  Using tool: execute_bash
 ⋮
 ● I will run the following shell command:
mkdir -p bounce_master && cd bounce_master && python3 -m pip install pygame
 ⋮
 ↳ Purpose: Installing PyGame without --user flag


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> let's alter the command. I already have virtual environment setup in .venv and have pygame installed in the virtual environment.
I understand that you already have a virtual environment set up in .venv and PyGame is already installed there. That's great! Let's skip the installation step and start creating our game
files directly.

Let's create the main game file and start implementing the basic structure for our Bounce Master game:

🛠️  Using tool: fs_write
 ⋮
 ● Path: /home/kbyun/aws_game_devs/bounce_master/main.py


 ### 1. Leaderboard Backend (leaderboard.py)
• Created a Leaderboard class that handles all AWS DynamoDB interactions
• Implemented functions to:
  • Create the DynamoDB table if it doesn't exist
  • Submit scores to the leaderboard
  • Retrieve top scores from the leaderboard

### 2. Game Integration (main.py)
• Added game states to handle different screens:
  • GAME_PLAYING: Normal gameplay
  • GAME_OVER: When all balls are lost
  • ENTER_NAME: For submitting your name to the leaderboard
  • SHOW_LEADERBOARD: Displays the top scores
• Implemented name entry functionality for submitting scores
• Added leaderboard display with highlighting for the player's score
• Increased the default paddle width to 200 as you mentioned

### 3. AWS Setup Helper (setup_aws.py)
• Created a utility script to help set up the required AWS resources
• Checks if AWS credentials are properly configured
• Creates the DynamoDB table with appropriate schema and indexes

### 4. Documentation (README.md)
• Added comprehensive documentation explaining:
  • Game features and controls
  • AWS setup requirements
  • How to run the game
  • Required AWS permissions

### How to Use the Leaderboard

1. First, make sure your AWS credentials are configured:

   aws configure


2. Run the setup script to create the DynamoDB table:

   python setup_aws.py


3. Run the game:

   python main.py


4. When you lose all balls, you'll be prompted to enter your name
5. After submitting your name, the leaderboard will be displayed
6. Your score will be highlighted if it appears in the top scores

### Technical Details

• The leaderboard uses a DynamoDB table with a partition key of player_id and sort key of score
• A global secondary index on score allows for efficient retrieval of top scores
• Error handling is in place to gracefully handle AWS connectivity issues
• The game will still work even if AWS connectivity fails - it will just skip the leaderboard functionality

Would you like me to explain any part of the implementation in more detail or make any adjustments to the leaderboard system?

> so this is good direction, but this would require me to hand out aws credentials any player that wants to play this game. I think better approach is that I have some api gateway that handles interaction between dynamodb. And the client will just request to api gateway. what do you think? also how should we handle authentication? to avoid random requests coming in?
You're absolutely right about the security concerns. Embedding AWS credentials directly in a game that's distributed to players is a significant security risk. Let's revise our approach to use API Gateway as an intermediary between the game client and DynamoDB.

Here's a better architecture:

1. API Gateway + Lambda Backend: Create REST endpoints that the game can call
2. Client-side API calls: The game makes HTTP requests to these endpoints
3. Authentication: Implement simple API key authentication

This approach has several advantages:
• No AWS credentials in the game code
• Centralized control over database access
• Ability to add rate limiting and other protections
• Better security overall

Let's implement this improved architecture:


### 1. Added Proper Dependencies

I've added explicit DependsOn attributes to ensure resources are created in the correct order:

• LeaderboardUsagePlan now depends on both LeaderboardAPI and LeaderboardAPIDeployment
• LeaderboardApiKey now depends on both LeaderboardAPIDeployment and LeaderboardAPI
• LeaderboardUsagePlanKey now depends on both LeaderboardUsagePlan and LeaderboardApiKey
• LeaderboardAPIDeployment now depends on all the methods and permissions

### 2. Added CORS Support

I've added proper CORS (Cross-Origin Resource Sharing) support to allow the game to be embedded in a blog:

• Added OPTIONS methods for both API endpoints
• Added CORS headers to all responses
• Configured proper CORS response parameters

### 3. Updated Lambda Functions

I've updated the Lambda function code to include CORS headers in all responses, which is essential for web integration.

### 4. Improved Error Handling

The template now has better error handling and more robust dependencies between resources.

### How to Deploy

You can deploy this updated template using the same deploy.sh script:

bash
chmod +x deploy.sh
./deploy.sh

```
2. Start Coding
