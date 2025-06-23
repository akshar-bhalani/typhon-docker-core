import os
import requests
import pandas as pd
from lib.encryption_utils import decrypt_with_private_key
from lib.token_manager import with_django_auth
from openai import OpenAI
from dotenv import load_dotenv
import random
import markdown
import json


# Load environment variables from .env file
load_dotenv()

POST_USER = os.environ.get("POST_USER")
PASSWORD = os.environ.get("PASSWORD")
PEXELSKEY = os.environ.get("PEXELSAPI")

# Set your OpenAI API key
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Load json Data
with open('lib/data.json', 'r') as file:
    imageData = json.load(file)


def getImage(keyword, category):
    url = "https://api.pexels.com/v1/search"
    headers = {'Authorization': PEXELSKEY}
    params = {
        'query': keyword,
        'orientation': 'landscape',
        'per_page': 7,  
        'size': 'small'  # Request smaller image for optimization
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        # Extract the first image's optimized URL and other details
        photo = data['photos'][random.randint(0, len(data['photos'])-1)]
        optimized_url = photo['src']['large'] 
        return optimized_url
    else:
        print("Failed to fetch images:", response.status_code)
        return imageData[str(category)][random.randint(0, 4)]


def getHeroImage(keyword,category):
    url = "https://api.pexels.com/v1/search"
    headers = {'Authorization': PEXELSKEY}
    params = {
        'query': keyword,
        'orientation': 'landscape',
        'per_page': 4,  # Fetch only one image for demonstration
        'size': 'small'  # Request smaller image for optimization
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        # Extract the first image's optimized URL and other details
        photo = data['photos'][random.randint(0, len(data['photos'])-1)]
        optimized_url = photo['src']['large'] 
        print("optimized_url========",optimized_url)
        return optimized_url
    else:
        print("Failed to fetch images:", response.status_code)
        return imageData[str(category)][random.randint(0, 4)]


def generateOutline(data):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
             messages=[
                {"role": "system", "content": "you are a helpful, intelligent writing assistant."},
                {"role": "user", "content": f"use the following JSON brief to write an engaging, comprehensive outline in Mark down format (ATX) Tone of voice: 50% spartan, casual"},
                {"role": "user", "content": '''
                                                    {

                                                    tittle: "The Benefits of Blogging for Business",

                                                    WordCount: "1500",

                                                    PrimaryKeyword: "blogging",

                                                    SecondaryKeywords: ["blogging in businesses", "marketing", "SEO"],

                                                    additionalInformation: "don't pitch the
                                                    company at all - make it very informative
                                                    and provide as much value as you can."
                                                    }
                                                    '''
                 },
                {"role": "assistant", "content": '''
                 
                        ## Introduction

                        - Definition of blogging for business
                        - Brief explanation of the growing popularity of blogging in the business world
                        - Explanation of its relevance in the business context

                        ## Increased Online Visibility

                        - Discuss how blogging can improve a business's online presence
                        - Importance of search engine optimization (SEO) and how blogging can help with it
                        - Examples of businesses that have benefited from increased online visibility through blogging

                        ## Establishing Authority and Expertise

                        - Explain how blogging allows businesses to showcase their knowledge and expertise in their industry
                        - Importance of providing valuable and informative content to attract and engage readers
                        - How blogging can help businesses build trust and credibility with their audience

                        ## Building a Community and Engaging with Customers

                        - Discuss the role of blogging in fostering a sense of community among customers and followers
                        - Importance of encouraging comments, feedback, and discussions on blog posts
                        - Examples of businesses that have successfully built a loyal community through blogging
                        ## Generating Leads and Increasing Sales

                        - Explain how blogging can be an effective lead generation tool for businesses
                        - Importance of including call-to-action (CTA) buttons and links in blog posts
                        - How blogging can help businesses nurture leads and convert them into customers

                        ## Cost-Effective Marketing Strategy

                        - Discuss the cost advantages of blogging compared to traditional marketing methods
                        - Importance of creating valuable content that can be repurposed across different platforms
                        - Examples of businesses that have saved money by utilizing blogging as a marketing strategy

                        ## Improving Customer Service and Support

                        - Explain how blogging can be used to address customer concerns and provide support
                        - Importance of regularly updating blog content to address frequently asked questions
                        - How blogging can help businesses build stronger relationships with their customers

                        ## Staying Ahead of the Competition

                        - Discuss how blogging can give businesses a competitive edge in their industry
                        - Importance of staying up-to-date with industry trends and sharing insights through blog posts
                        - Examples of businesses that have outperformed their competitors by leveraging blogging

                        ## Measuring Success and Analyzing Data

                        - Explain the importance of tracking and analyzing blog metrics to measure success
                        - Discuss key performance indicators (KPIs) that businesses should monitor
                        - How businesses can use data to optimize their blogging strategy and achieve better results

                        ## Conclusion

                        - Recap the benefits of blogging for business discussed in the blog post
                        - Encourage businesses to start or improve their blogging efforts
                        - Final thoughts on the long-term advantages of blogging for business success.
                            
                 
                 '''
                 },
                 {"role": "user", "content": f"{data}"}
            ],
        )
        
        response_message = response.choices[0].message.content
        # print(response_message )
        return response_message
    except Exception as e:
        print(f"Error: {e}")
        return "outline generation failed"


def generateContentIdea(number, categories, latest_topics_str):
    userContent = f'''
Dear ChatGPT,

You are an experienced, authoritative content strategist and SEO expert.

Your task is to generate **{number} unique and trending blog post ideas** for our website. The goal is to create blog topics that are in high demand and widely searched by internet users.

Please follow these instructions carefully:

1. Avoid generating blog post titles that are similar to or duplicate any of the following recent topics:
{latest_topics_str}

2. You must choose topics that strictly belong to the following content categories:
{categories}

3. Each blog post idea should include:
   - Blog Post Title (minimum 60 characters)
   - Primary Keyword
   - Secondary Keywords
   - Category

4. Only include the year **2025** in the title if absolutely necessary.

5. Your response should be in a clean **Markdown table format**. Do not include any text or explanation outside of the table.

Ensure the ideas are original, relevant to the listed categories, and SEO-optimized.
'''

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful, intelligent writing assistant."},
                {"role": "user", "content": userContent},
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Content Idea generation failed. Error: {e}")
        return None



def getHeadings(outline):
    
    # Split the outline into lines
    lines = outline.splitlines()

    # Initialize an array to hold lines that start with ##
    headings = []

    # Loop through each line and check if it starts with ##
    for line in lines:
        if line.startswith('##'):
            headings.append(line.strip())
    
    return headings


def generateSection(outline):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
             messages=[
                {"role": "system", "content": "you are a helpful, intelligent writing assistant."},
                {"role": "user", "content": f"The following is an outline for an award-winning article. Your task is to write one section and one section only: the one marked by a '←'. Tone of voice: 50% spartan, casual outline: {outline}"},
            ],
        )
        response_message = response.choices[0].message.content
        # print(response_message )
        return response_message
    except Exception as e:
        print(f"Error: {e}")
        return "Section generation failed"
    

def formatSection(section):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
             messages=[
                {"role": "system", "content": "you are a helpful, intelligent writing assistant."},
                {"role": "user", "content": f"Edit the following text to break up the flow. Add bullet points and subheadings where needed for variety. Use Markdown (atx) format"},
                {"role": "user", "content": """
                        ##Understanding AI and its Growth

                        Artificial intelligence (AI) is a rapidly evolving field with the potential to transform our world. But what exactly is AI, and how is it growing? In this blog section, we'll break down the basics of AI and explore the factors fueling its current boom.

                        AI refers to the intelligence exhibited by machines, ranging from simple automation tasks to complex decision-making processes. There are two main categories of AI. Narrow AI, or ANI, is the type we encounter most often, excelling at specific tasks like playing chess or recognizing faces. Artificial General Intelligence (AGI), on the other hand, is a hypothetical type of AI that would possess human-level intelligence capable of learning and reasoning across a wide range of situations. AGI remains within the realm of science fiction for now.

                        The rapid growth of AI is driven by several factors. The explosion of data in today's world provides AI systems with the necessary fuel to learn and improve, as AI thrives on data. The development of increasingly powerful computers allows AI algorithms to process this massive amount of data efficiently. Additionally, recent breakthroughs in machine learning, a branch of AI that enables systems to learn from data without explicit programming, have significantly enhanced AI capabilities.

                        The impact of AI's growth is profound across various sectors. In healthcare, AI is used to analyze medical images, diagnose diseases, and develop personalized treatment plans. In finance, AI-powered algorithms are transforming financial markets by analyzing trends and making investment decisions. In manufacturing, AI is automating tasks in factories, improving efficiency and productivity.

                        As AI continues to grow, it is crucial to consider both its potential benefits and challenges. We need to ensure that AI is developed and used responsibly, with a focus on ethical considerations and human well-being.
                        """
                 },
                {"role": "assistant", "content": """
                        ## Understanding AI and its Growth

                        Artificial intelligence (AI) is a rapidly evolving field with the potential to transform our world. But what exactly is AI, and how is it growing? In this blog section, we'll break down the basics of AI and explore the factors fueling its current boom.

                        ### What is AI?

                        AI refers to the intelligence exhibited by machines. This can range from simple automation tasks to complex decision-making processes. There are two main categories of AI:

                        - **Narrow AI (ANI):** This is the type of AI we encounter most often. ANI excels at specific tasks, like playing chess or recognizing faces.
                        - **Artificial General Intelligence (AGI):** This hypothetical type of AI would possess human-level intelligence, capable of learning and reasoning across a wide range of situations. AGI is still in the realm of science fiction.

                        ### What's Driving the Growth of AI?

                        Several factors are contributing to the rapid growth of AI:

                        - **Increased Data Availability:** AI thrives on data. The explosion of data generated in today's world provides AI systems with the fuel they need to learn and improve.
                        - **Advancements in Computing Power:** The development of ever-more powerful computers allows AI algorithms to process massive amounts of data efficiently.
                        - **Breakthroughs in Machine Learning:** Machine learning is a branch of AI that enables systems to learn from data without explicit programming. Recent advancements in this field have significantly enhanced AI capabilities.

                        ### The Impact of AI Growth

                        The growth of AI is having a profound impact on various sectors, including:

                        - **Healthcare:** AI is being used to analyze medical images, diagnose diseases, and even develop personalized treatment plans.
                        - **Finance:** AI-powered algorithms are transforming financial markets by analyzing trends and making investment decisions.
                        - **Manufacturing:** AI is automating tasks in factories, improving efficiency and productivity.

                        As AI continues to grow, it's crucial to consider both its potential benefits and challenges. We need to ensure that AI is developed and used responsibly, with a focus on ethical considerations and human well-being.
                        """
                 },
                {"role": "user", "content": section},
            ],
        )
        response_message = response.choices[0].message.content
        # print(response_message )
        return response_message
    except Exception as e:
        print(f"Error: {e}")
        return "Section formatting failed"
    

def GenerateArticle(data):
    sections = []  # Initialize a list to store sections of the article
    
    outline = generateOutline(data)  # Generate an outline based on the data
    headings = getHeadings(outline)  # Get headings from the outline

    print("Generating Article")
    
    # URL and attributes for the image
    hero_image = f'<img class="post_hero_image" src="{getHeroImage(data["PrimaryKeyword"],data["Category"])}" alt="{data["PrimaryKeyword"]}">'
    
    # Loop over each heading and process sections
    for index, heading in enumerate(headings):
        # Append a marker to the current heading in the outline to update it
        updated_outline = outline.replace(heading, heading + ' ←')

        image_keyword = data['title'] if 'conclusion' in heading.lower() else heading

        
        # Generate the section based on the updated outline
        section = generateSection(updated_outline)

        if index == 0:
            
            sections.append(section)
            sections.append(hero_image)

        elif random.randint(1, 4) == 4:
            formattedSection = formatSection(section)
            if index != 1:
                image = f'<img class="post_image" src="{getImage(image_keyword,data["Category"])}" alt="{heading}">'
                sections.append(image)
            sections.append(formattedSection)

        else:
            if index != 1:
                image = f'<img class="post_image" src="{getImage(image_keyword,data["Category"])}" alt="{heading}">'
                sections.append(image)
            sections.append(section)
            

    # Join all sections (and the image) into a single string with appropriate newlines between them
    article = '\n'.join(sections)

    html = markdown.markdown(article)
    
    return html


@with_django_auth
def create_wordpress_post(url, title, category, content, wordpress_username, wordpress_api_key, user_id, setting_id, headers=None):


    if len(content) > 10:

        print("Publishing Article...")
        wordpress_api_key = decrypt_with_private_key(wordpress_api_key)
        credentials = (wordpress_username, wordpress_api_key)
        wp_headers = {'Content-Type': 'application/json'}
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'slug': title.replace(' ', '-').lower(),  # Generate slug from title
            'categories': category  # Assign categories by IDs
        }



        response = requests.post(f'{url}/wp-json/wp/v2/posts/', json=post_data, headers=wp_headers, auth=credentials)

        # Check if the request was successful
        if response.status_code == 201:
            base_url = os.getenv("BASE_API_URL")
            add_blog_url = f"{base_url}/api/v1/blogs/add_blog/"
            wordpress_response = response.json()
            print(f"Post Created: {wordpress_response['title']['rendered']}")

            # Extract title and link from WordPress response
            wp_title = wordpress_response['title']['rendered']
            wp_link = wordpress_response['link']

            # Make the second POST request
            add_blog_payload = {
                "title": wp_title,
                "link": wp_link,
                "wordpress_key": wordpress_response['id'],
                "publish_date": wordpress_response['date_gmt'],
                "setting_id": setting_id,  # Replace or remove if not applicable
                "user_id": user_id # Replace with the actual user ID
            }

            add_blog_response = requests.post(add_blog_url, json=add_blog_payload, headers={**headers, 'Content-Type': 'application/json'})

          
            
            if add_blog_response.status_code == 201:
                    print(f"Blog successfully added to API: {add_blog_payload['title']}")
                    print("i am in positng============================================")
                    # Call the additional API to add topics
                    add_topics_url = f"{base_url}/api/v1/generated-topics/add_topics/"
                    add_topics_payload = {
                        "topics": [
                            {
                                "user": user_id,
                                "title": wp_title,
                                "date": wordpress_response['date_gmt'].split("T")[0]  # Use the publish date from WordPress response
                            }
                        ]
                    }
                    print("payload ============",add_blog_payload)
                    try:
                        add_topics_response = requests.post(add_topics_url, json=add_topics_payload, headers={**headers, 'Content-Type': 'application/json'})
                        if add_topics_response.status_code == 201:
                            print(f"Topics successfully added to API: {add_topics_payload['topics']}")
                        else:
                            print(f"Failed to add topics to API: {add_topics_response.json()}")
                    except Exception as e:
                        print(f"Error calling add_topics API: {e}")

                    return add_blog_response.json()
            else:
                print(f"Failed to add blog to API: {add_blog_response.json()}")
                return f"Failed to add blog to API: {add_blog_response.status_code}"
            

        else:
            print(f"Failed to create post: {response.json()}")
            return f"Failed to create post: {response.status_code}"
        


    else:
        print("The content has no elements.")
        return None
