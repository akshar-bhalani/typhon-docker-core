import os
import json
import requests
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

POST_USER = os.environ.get("POST_USER")
PASSWORD = os.environ.get("PASSWORD")

# Set your OpenAI API key
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


keyword_list = []


def get_keyword_from_csv(filename):

    input_df = pd.read_csv(filename)

    for index, row in input_df.iterrows():
        keyword = row['keyword']
        keyword_list.append(keyword)

def generate_title(keyword_list):
    """
    Generate a similar title using GPT-4 based on the provided keyword.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4", 
            # response_format={ "type": "json_object" },
             messages=[
                {"role": "system", "content": "You are a Expert SEO Content Writer, Skilled in writing SEO post content, that rank in browser search"},
                {"role": "user", "content": f"Rewrite this all slug into a post title, for example '5-ways-to-make-your-small-business-more-sustainable' slug can be rewrite as '5 Methods to Boost Your Small Business's Sustainability' slugs: {keyword_list} give output as python list and use double quotes to store title in list"}
            ],
        )
        print('TITLE GENERATOR IS CALLED')
        # print(response)
        response_message = response.choices[0].message.content
        # print(response_message )
        return response_message
    except Exception as e:
        print(f"Error: {e}")
        return "Title generation failed"
    

def generate_post(title):
    try:
        response = client.chat.completions.create(
            model="gpt-4", 
            # response_format={ "type": "json_object" },
             messages=[
                {"role": "system", "content": "You are a Expert SEO Content Writer, Skilled in writing SEO post content, that rank in browser search"},
                {"role": "user", "content": f'write an SEO optimized in depth and detailed article about {title} in 1500 words, content should be in html format and give every html tag class="" as blogpost-<HTML-TAG-NAME>, give output only string of object containing meta_description as text and html_content without body tag, no extra things only string object that i can use in json.loads()'}
            ],
        )

        print('Post GENERATOR IS CALLED')

        response_message = response.choices[0].message.content
       
        return response_message
    
    except Exception as e:
        print(f"Error: {e}")
        return "Post generation failed"


def create_wordpress_post(title, content, user, password, url, slug, seo_title, meta_description):
    credentials = (user, password)
    headers = {'Content-Type': 'application/json'}
    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
         'slug': slug,
         'meta': {
            'yoast_wpseo_title': seo_title,
            'yoast_wpseo_metadesc': meta_description
        }
    }

    response = requests.post(f'{url}/wp-json/wp/v2/posts', json=post_data, headers=headers, auth=credentials)
    return response.json()



# Getting Keywords From CSV File

get_keyword_from_csv('input.csv')

print(keyword_list)

# generate title from keywords

title_list_string = generate_title(keyword_list)

print(title_list_string)

title_list = json.loads(title_list_string)

print(title_list)

# Generate post from title

for title in title_list:

    try:
        print(title)

        post_obj =  generate_post(title)
        
        print(post_obj)

        post = json.loads(post_obj)

        print(post)

        post["title"] = title
        post["slug"] = title.replace(" ", "-")

        post_response = create_wordpress_post(
            title=post["title"],
            content= post["html_content"],
            user=POST_USER,
            password=PASSWORD,
            url="https://mevycapital.com/",
            slug=post["slug"],
            seo_title=f"Mevycapital - {post['title']}",
            meta_description=post["meta_description"]
        )

        if post_response :
            print(f"{post['title']} Post created...")

    except Exception as e:
        print(f"Error: {e}")
           

    





      
    

print(title_list)
