import requests

def get_wordpress_categories(url):
    """
    Fetch categories from a WordPress site via the REST API.

    Args:
    - url (str): The base URL of the WordPress site.

    Returns:
    - list of dict: A list of categories with details.
    """
    # URL for the WordPress categories API endpoint
    categories_url = f'{url}/wp-json/wp/v2/categories'
    
    # Send a GET request to fetch categories
    response = requests.get(categories_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Return the list of categories as Python dictionaries
        return response.json()
    else:
        # Return an error message if something went wrong
        return f"Failed to retrieve categories: {response.status_code}"

# Example usage
url = 'https://digitravelgalaxy.com/'
categories = get_wordpress_categories(url)
print(categories)
