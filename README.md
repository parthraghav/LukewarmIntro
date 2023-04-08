## LukewarmIntro

This script reverse-engineers the Twitter API to expose its internal group DM endpoint, allowing the creation of a bot that sends warm introductions to people in the [@_nightsweekends](https://twitter.com/_nightsweekends) community.

### Structure
- `.env`: Contains environment variables and API keys for the project.
- `.gitignore`: Specifies files and directories that should be ignored by Git.
- `cookies.json`: Stores cookies needed for requests.
- `hack.py`: The main script for the Twitter Group DM Hack.
- `README.md`: This file, containing instructions and details about the project.
- `requirements.txt`: Lists the required Python libraries for this project.

### Dependencies
Make sure to install the necessary Python libraries listed in the requirements.txt file:

```pip install -r requirements.txt```

### Usage
Before running the script, make sure to set up the following environment variables in the .env file:

- `openai_api_key`: Your OpenAI API key.
- `twitter_consumer_key`: Your Twitter consumer key.
- `twitter_consumer_secret`: Your Twitter consumer secret.
- `twitter_access_token`: Your Twitter access token.
- `twitter_access_token_secret`: Your Twitter access token secret.
- `twitter_bearer_token`: Your Twitter bearer token.
- `twitter_client_bearer_token`: Your Twitter client bearer token.
- `twitter_client_csrf_token`: Your Twitter client CSRF token.

Once the environment variables are set, run the script using:

```python hack.py```

The script will fetch user information from their Twitter handles, generate a warm introduction using OpenAI's GPT-3, create a group DM with the specified participants and send the introduction message, and automatically exit the group DM.