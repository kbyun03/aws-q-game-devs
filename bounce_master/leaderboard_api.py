import requests
import json
import os



class LeaderboardAPI:
    def __init__(self, api_endpoint=None, api_key=None):
        """Initialize the leaderboard API client"""
        self.api_endpoint = api_endpoint or os.environ.get('LEADERBOARD_API_ENDPOINT')
        self.api_key = api_key or os.environ.get('LEADERBOARD_API_KEY')

        if not self.api_endpoint or not self.api_key:
            raise ValueError("API endpoint and API key must be provided")

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
        try:
            response = requests.post(
                f"{self.api_endpoint}/scores",
                headers=headers,
                data=json.dumps(data)
            )
            if response.status_code == 200:
                print(f"Successfully submitted score for {player_name}")
                return True
            else:
                print(f"Failed to submit score. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error submitting score: {e}")
            return False

    def get_top_scores(self, limit=10):
        """Get the top scores from the leaderboard via API"""
        headers = {
            "x-api-key": self.api_key
        }
        try:
            response = requests.get(
                f"{self.api_endpoint}/scores/top?limit={limit}",
                headers=headers
            )
            if response.status_code == 200:
                return json.loads(response.json().get('body', {})).get('scores', [])
            else:
                print(f"Failed to get top scores. Status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting top scores: {e}")
            return []

# Helper function to initialize the leaderboard API
def initialize_leaderboard_api():
    # You can set these values directly here or use environment variables
    print('----- here')
    api_endpoint = os.environ.get('LEADERBOARD_API_ENDPOINT')
    api_key = os.environ.get('LEADERBOARD_API_KEY')

    if not api_endpoint or not api_key:
        print("Warning: API endpoint or API key not set. Leaderboard functionality will be disabled.")
        return None

    try:
        return LeaderboardAPI(api_endpoint, api_key)
    except Exception as e:
        print(f"Error initializing leaderboard API: {e}")
        return None
