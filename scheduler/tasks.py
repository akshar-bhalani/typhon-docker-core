from urllib.parse import urlparse
from lib.log import log_error, log_info
from lib.utilities import GenerateArticle, generateContentIdea, create_wordpress_post
import requests
import json
import os
from dotenv import load_dotenv
import logging
import pandas as pd
import re
from scheduler.celery_app import app
from datetime import datetime
from lib.token_manager import with_django_auth


# Load environment variables
load_dotenv()


def get_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'localhost':
        return 'localhost'
    return parsed_url.netloc.split('.')[-2]

def markdown_table_to_dataframe(markdown_table, word_count):
    lines = markdown_table.strip().split('\n')
    header = [re.sub(r'^\||\|$', '', cell).strip() for cell in lines[0].split('|')]
    header.insert(1, 'Word Count')
    data = []
    
    for line in lines[2:]:
        row = [re.sub(r'^\||\|$', '', cell).strip() for cell in line.split('|')]
        row.insert(1, word_count)
        if len(row) == len(header):
            data.append(row)
        else:
            print(f"Ignoring row with invalid number of columns: {row}")
    
    df = pd.DataFrame(data, columns=header)
    return df[['Blog Post Title', 'Word Count', 'Primary Keyword', 'Secondary Keywords', 'Category']]

@with_django_auth
def process_row(row_as_dict, url, domain, wordpress_username, wordpress_api_key, user_id,
                setting_id, headers=None):
    try:
       

        content = GenerateArticle(row_as_dict)
        create_wordpress_post(url, row_as_dict["title"], row_as_dict["Category"], content,wordpress_username,wordpress_api_key, user_id,
                setting_id,headers=headers)
        log_info(f"post created {row_as_dict}")
        return True
    except Exception as e:
        print(f"An error occurred while processing the row: {e}")
        log_error(f"An error occurred while processing the domain:{domain} ")
        return False

# Function to fetch user configurations from API

@with_django_auth
def get_user_config(email, password, headers=None):

    try:
        base_url = os.getenv("BASE_API_URL")
        if not base_url:
            raise ValueError("BASE_API_URL not set in environment variables.")
        
        # Step 1: Login to get the token
        # login_url = f"{base_url}/api/v1/login/"
        # login_data = {
        #     "email": email,
        #     "password": password
        # }
        
        # login_response = requests.post(login_url, json=login_data)
        # if login_response.status_code != 200:
        #     print(f"Login failed: {login_response.status_code}")
        #     return []
            
        # # Extract token from login response
        # token = login_response.json().get('token')
        # if not token:
        #     print("No token received in login response")
        #     return []
            
        # Step 2: Call user config API with the token
        config_url = f"{base_url}/api/v1/users/user_config/"
        # headers = {
        #     'Authorization': f'Token {token}'
        # }
        
        config_response = requests.get(config_url, headers=headers)
        if config_response.status_code == 200:
            return config_response.json()
        else:
            print(f"Error fetching user config: {config_response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error in get_user_config: {e}")
        return []

# Example usage:

# Function to store content ideas in the database
def store_content_idea_in_db(content_ideas):
    try:
        print(content_ideas)
        url = "http://your-django-backend-url/api/store_content_idea/"
        response = requests.post(url, json=content_ideas)
        if response.status_code == 200:
            print("Content ideas successfully stored in the database.")
        else:
            print(f"Failed to store content ideas: {response.status_code}")
    except Exception as e:
        print(f"Error storing content ideas in DB: {e}")
        log_error("Error storing content ideas in DB.")
        return False
    return True

# @app.task(bind=True, max_retries=3, name='scheduler.tasks.process_single_user')
# @with_django_auth
# def process_single_user(self, user_config, headers=None):
#     """
#     Process a single user's configuration as a Celery task
#     """
#     try:
#         URL = user_config["wordpress_url"]
#         number_of_post = str(user_config["number_of_posts"])
#         # categories = user_config["categories"]
#         categories = ", ".join([sub["name"] for sub in user_config["subcategories"]])
#         print("categories=========================",categories)
#         word_count = user_config["word_count"]
#         wordpress_username = user_config["wordpress_username"]
#         wordpress_api_key = user_config["wordpress_api_key"]
#         user_id=user_config["id"]
#         setting_id=user_config["setting_id"]
        
#         base_url = os.getenv("BASE_API_URL")
#         if not base_url:
#             raise ValueError("BASE_API_URL not set in environment variables.")
        
        
#         latest_topics_url = f"{base_url}/api/v1/generated-topics/get_topics?user_id={user_id}"
#         try:
#             latest_topics_response = requests.get(latest_topics_url,headers=headers)
#             if latest_topics_response.status_code == 200:
#                 latest_topics = latest_topics_response.json().get("latest_topics", [])
#                 # Convert the list of latest topics into a comma-separated string
#                 latest_topics_str = ", ".join(latest_topics)
#             else:
#                 print(f"Failed to fetch latest topics for user {user_id}: {latest_topics_response.status_code}")
#                 latest_topics_str = ""
#         except Exception as e:
#             print(f"Error fetching latest topics for user {user_id}: {e}")
#             latest_topics_str = ""
#         # Generate content ideas
#         print("letest topics ==========================",latest_topics_str)
#         markdown_table = generateContentIdea(number_of_post, categories,latest_topics_str)
#         df = markdown_table_to_dataframe(markdown_table, word_count)
#         print("user_config===========================================",user_config)
#         domain = get_domain(URL)
#         category_to_id = {
#             'Beauty': 4,
#             'Blog': 1,
#             'Electronics': 5,
#             'Fashion': 3,
#             'Travel': 2,
#             'AI Coding Assistants': 6,
#             'AI Code Automation': 7,
#             'AI Website Builders': 8,
#             'AI App Development': 9,
#             'AI Web & App Development': 10
#         }


#         for index, row in df.iterrows():
#             process_row(
#                 {
#                     "title": row["Blog Post Title"],
#                     "WordCount": row["Word Count"],
#                     "PrimaryKeyword": row["Primary Keyword"],
#                     "SecondaryKeywords": row["Secondary Keywords"].split(", ") if row["Secondary Keywords"] else [],
#                     "Category": category_to_id.get(row["Category"]),
#                     "additionalInformation": "don't pitch the company at all - make it very informative and provide as much value as you can.",
#                 },
#                 URL,
#                 domain,
#                 wordpress_username,
#                 wordpress_api_key,
#                 user_id,
#                 setting_id,
#                 headers=headers
#             )

#         return f"Successfully processed configuration for {wordpress_username}"

#     except Exception as e:
#         log_error(f"Error processing user {user_config['wordpress_username']}: {str(e)}")
#         raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds


@app.task(bind=True, max_retries=3, name='scheduler.tasks.process_single_user')
@with_django_auth
def process_single_user(self, user_config, headers=None):
    """
    Process a single user's configuration as a Celery task
    """
    try:
        URL = user_config["wordpress_url"]
        number_of_post = int(user_config["number_of_posts"])
        categories = ", ".join([sub["name"] for sub in user_config.get("subcategories", [])]) \
            if "subcategories" in user_config else ", ".join(user_config.get("categories", []))
        word_count = user_config["word_count"]
        wordpress_username = user_config["wordpress_username"]
        wordpress_api_key = user_config["wordpress_api_key"]
        user_id = user_config["id"]
        setting_id = user_config["setting_id"]
        
        base_url = os.getenv("BASE_API_URL")
        if not base_url:
            raise ValueError("BASE_API_URL not set in environment variables.")
        
        today = datetime.now().strftime('%Y-%m-%d')
        todays_topics_url = f"{base_url}/api/v1/custom-blog-topics/list_topics/?user_id={user_id}&usage_date={today}"
        try:
            todays_topics_response = requests.get(todays_topics_url, headers=headers)
            if todays_topics_response.status_code == 200:
                todays_topics_data = todays_topics_response.json()
                todays_topics = todays_topics_data.get("results", [])
                # Only use up to number_of_post topics
                if todays_topics:
                    print(f"Found existing topics for today: {todays_topics}")
                    data = [{
                        "Blog Post Title": topic["title"],
                        "Word Count": word_count,
                        "Primary Keyword": topic.get("primary_keyword", ""),
                        "Secondary Keywords": topic.get("secondary_keyword", ""),
                        "Category": categories.split(", ")[0] if categories else ""
                    } for topic in todays_topics[:number_of_post]]
                    df = pd.DataFrame(data)
                else:
                    # No topics for today, generate exactly number_of_post topics
                    latest_topics_url = f"{base_url}/api/v1/generated-topics/get_topics?user_id={user_id}"
                    latest_topics_response = requests.get(latest_topics_url, headers=headers)
                    latest_topics = latest_topics_response.json().get("latest_topics", []) if latest_topics_response.status_code == 200 else []
                    latest_topics_str = ", ".join(latest_topics)
                    markdown_table = generateContentIdea(str(number_of_post), categories, latest_topics_str)
                    df = markdown_table_to_dataframe(markdown_table, word_count)
            else:
                print(f"Failed to fetch today's topics for user {user_id}: {todays_topics_response.status_code}")
                return f"Failed to fetch today's topics for user {wordpress_username}"
        except Exception as e:
            print(f"Error fetching topics for user {user_id}: {e}")
            return f"Error fetching topics for user {wordpress_username}"

        print("Processing topics for user:", wordpress_username)
        domain = get_domain(URL)
        category_to_id = {
            'Beauty': 4,
            'Blog': 1,
            'Electronics': 5,
            'Fashion': 3,
            'Travel': 2,
            'AI Coding Assistants': 6,
            'AI Code Automation': 7,
            'AI Website Builders': 8,
            'AI App Development': 9,
            'AI Web & App Development': 10
        }

        # Only process up to number_of_post rows
        for index, row in df.head(number_of_post).iterrows():
            process_row(
                {
                    "title": row["Blog Post Title"],
                    "WordCount": row["Word Count"],
                    "PrimaryKeyword": row["Primary Keyword"],
                    "SecondaryKeywords": row["Secondary Keywords"].split(", ") if isinstance(row["Secondary Keywords"], str) else [row["Secondary Keywords"]],
                    "Category": category_to_id.get(row["Category"], None),
                    "additionalInformation": "don't pitch the company at all - make it very informative and provide as much value as you can.",
                },
                URL,
                domain,
                wordpress_username,
                wordpress_api_key,
                user_id,
                setting_id,
                headers=headers
            )

        return f"Successfully processed configuration for {wordpress_username}"

    except Exception as e:
        log_error(f"Error processing user {user_config['wordpress_username']}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    
    
@app.task(name='scheduler.tasks.process_wordpress_posts')
@with_django_auth
def process_wordpress_posts(headers=None):

    """
    Main task that fetches user configs and spawns individual tasks
    """
    try:
        print(f"Starting WordPress posting job at {datetime.now()}")
        
        email = os.getenv('USER_EMAIL')
        password = os.getenv('USER_PASSWORD')
        
        user_configs = get_user_config(email, password,headers=headers)
        if not user_configs:
            print("No user configurations found.")
            return

        # Create separate tasks for each user config
        for user_config in user_configs:
            process_single_user.delay(user_config)
            
    except Exception as e:
        print(f"Error in main task: {e}")
        log_error(f"Error in main task: {e}")



