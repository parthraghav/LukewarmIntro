import requests
import json
import time
import heapq
import tweepy
import openai
import firebase_admin
from os import environ
from dotenv import dotenv_values
from itertools import combinations

def get_env_var(key):
    local_env_config = dotenv_values(".env")
    return environ.get(key, local_env_config[key])

openai.api_key = get_env_var('openai_api_key')

twitter_api_v1 = None
twitter_api_v2 = None

def init_firebase():
    if len(firebase_admin._apps) > 0:
        return
    cred = firebase_admin.credentials.Certificate("./service-account.json")
    firebase_admin.initialize_app(cred)

def init_twitter_api_v1():
    global twitter_api_v1

    # check if auth is already initialized
    if 'twitter_api_v1' in globals() and twitter_api_v1 is not None:
        return twitter_api_v1
    
    twitter_auth = tweepy.auth.OAuth1UserHandler(
        consumer_key = get_env_var('twitter_consumer_key'),
        consumer_secret = get_env_var('twitter_consumer_secret'),
    )
    twitter_auth.set_access_token(
        get_env_var('twitter_access_token'),
        get_env_var('twitter_access_token_secret')
    )
    twitter_api_v1 = tweepy.API(twitter_auth)
    return twitter_api_v1

def init_twitter_api_v2():
    global twitter_api_v2

    # check if auth is already initialized
    if 'twitter_api_v2' in globals() and twitter_api_v2 is not None:
        return twitter_api_v2

    twitter_api_v2 = tweepy.Client(
        consumer_key = get_env_var('twitter_consumer_key'),
        consumer_secret = get_env_var('twitter_consumer_secret'),
        bearer_token = get_env_var('twitter_bearer_token')
    )

    return twitter_api_v2

def get_user_from_handle(handle):
    twitter_api = init_twitter_api_v2()
    res = twitter_api.get_user(username=handle)
    if res is None:
        return None
    user = res.data
    return user

def get_popular_tweets_from_handle(handle):
    twitter_api = init_twitter_api_v1()
    res = twitter_api.user_timeline(screen_name=handle, count=100)
    if res is None:
        return None
    tweets = res.data
    return tweets

cookies = None
with open('cookies.json', 'r') as f:
    cookies = json.load(f)

headers = {
    'authorization': 'Bearer {bearer_token}'.format(bearer_token=get_env_var('twitter_client_bearer_token')),
    'x-csrf-token': get_env_var('twitter_client_csrf_token'),
}

def create_group_dm(text, participantIds):
    """_summary_: Create a group DM with the given participantIds
    
        FAILURE
        {
            "data": {
                "create_dm": {
                    "__typename": "CreateDmFailed"
                }
            }
        }
        SUCCESS
        {
            "data": {
                "create_dm": {
                    "__typename": "CreateDmSuccess",
                    "conversation_id": "1593697250269712389", # use this to send messages instead of participant_ids
                    "dm_id": "1593697250269712393"
                }
            }
        }
    """
    json_data = {
        'variables': {
            'message': {
                'card': None,
                'media': None,
                'text': {
                    'text': text,
                },
                'tweet': None,
            },
            'requestId': '301e7cc0-6737-11ed-9772-45ab3155398b',
            'target': {
                # 'conversation_id': '1586635172249731075',
                'participant_ids': participantIds
            },
        },
        'queryId': 'MaxK2PKX1F9Z-9SwqwavTw',
    }
    response = requests.post('https://twitter.com/i/api/graphql/MaxK2PKX1F9Z-9SwqwavTw/useSendMessageMutation', cookies=cookies, headers=headers, json=json_data)
    assert response.status_code == 200, f"Instead receieved {response.status_code}\n\n\n{response.text}"
    parsed = json.loads(response.text)
    status = parsed['data']['create_dm']['__typename']
    if status == "CreateDmFailed":
        raise Exception(f"Failed to create DM with {participantIds}")
    elif status == "CreateDmSuccess":
        conversationId = parsed['data']['create_dm']['conversation_id']
        print(f"Created DM with {participantIds} with conversationId {conversationId}")
        return conversationId
    else:
        raise NotImplementedError(f"Unknown status {status}")


def exit_group_dm(conversationId):
    json_data = {
        'dm_secret_conversations_enabled': 'false',
        'krs_registration_enabled': 'false',
        'cards_platform': 'Web-12',
        'include_cards': '1',
        'include_ext_alt_text': 'true',
        'include_ext_limited_action_results': 'false',
        'include_quote_count': 'true',
        'include_reply_count': '1',
        'tweet_mode': 'extended',
        'include_ext_views': 'true',
        'dm_users': 'false',
        'include_groups': 'true',
        'include_inbox_timelines': 'true',
        'include_ext_media_color': 'true',
        'supports_reactions': 'true',
        'include_conversation_info': 'true'
    }
    requests.post(f'https://twitter.com/i/api/1.1/dm/conversation/{conversationId}/delete.json', cookies=cookies, headers=headers, data=json_data)

def generate_warm_intro(user1Name, user1Details, user2Name, user2Details):
    res = openai.Completion.create(
        engine="text-davinci-003",
        temperature=0.9,
        max_tokens=50,
        prompt="You are an AI network matchmaker. You're candid and personable. Your responsibility is to break ice between two people and have the conversation get going. You meet {user1} and {user2}. Please introduce each other by briefly talking about a cool fact about them or their previous experience. You can use the following information from their applications to craft a crisp and friendly warm intro: 1. {user1}\n\n{user1details}\n\n2.{user2}\n\n{user2details}".format(
            user1 = user1Name,
            user2 = user2Name,
            user1details = user1Details,
            user2details = user2Details
        )
    )
    return res['choices'][0]['text']
