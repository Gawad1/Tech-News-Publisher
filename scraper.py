import requests
from bs4 import BeautifulSoup
import json
import uuid
import os

def fetch_page_content(url):
    """Fetch the content of a webpage given its URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_most_popular_articles(soup):
    """Parse the 'Most Popular' articles from the BeautifulSoup object."""
    articles = []
    most_popular_section = soup.find(
        'div', class_='relative z-10 mb-20 flex justify-between font-polysans text-11 font-medium uppercase tracking-15 text-blurple'
    )

    if most_popular_section:
        ol_tag = most_popular_section.find_next('ol', class_="styled-counter styled-counter-standard md:w-full w-full")
        if ol_tag:
            list_items = ol_tag.find_all('li')
            for item in list_items:
                title_tag = item.find('h2')
                link_tag = item.find('a')

                if title_tag and link_tag:
                    title = title_tag.text.strip()
                    relative_link = link_tag['href']
                    full_link = f"https://www.theverge.com{relative_link}"
                    articles.append((title, full_link))
    else:
        print('Most Popular section not found')
    return articles

def scrape_topic_content(topic_url):
    """Scrape the main content from the article body."""
    response = requests.get(topic_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try the first set of queries
    body_section = soup.select_one("#content > div.relative.md\\:mx-auto.md\\:flex.md\\:max-w-container-md.lg\\:max-w-none > div.duet--article--article-body-component-container.clearfix.sm\\:ml-auto.md\\:ml-100.md\\:max-w-article-body.lg\\:mx-100")

    # If body is not found, try the fallback queries
    if body_section is None:
        body_section = soup.select_one("#content")

    body_content = body_section.text.strip() if body_section else "Body section not found."

    return body_content

def scrape_image_url(topic_url):
    """Scrape the image URL from the article."""
    response = requests.get(topic_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Use the provided jspath to locate the image
    image_tag = soup.select_one("#content > div.duet--article--lede.mx-auto.mb-28.w-full.md\\:max-w-container-md.lg\\:mb-36.lg\\:max-w-none > div > div.w-full.shrink-0.lg\\:basis-\\[600px\\] > div > figure > span > img")
    
    if image_tag and 'src' in image_tag.attrs:
        return image_tag['src']
    else:
        print("Image not found in article.")
        return None

def save_image(image_url, save_dir, unique_id):
    """Download the image and save it with the unique ID as its filename."""
    try:
        # Fetch the image content
        response = requests.get(image_url)
        response.raise_for_status()

        # Define the image path with unique ID
        image_path = os.path.join(save_dir, f"{unique_id}.jpg")
        
        # Write the image content to the file
        with open(image_path, 'wb') as file:
            file.write(response.content)
        
        return image_path
    except Exception as e:
        print(f"Failed to download image: {e}")
        return None

def save_scraped_content_to_json(content_data, json_file):
    """Save the scraped content to a JSON file."""
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(content_data, file, ensure_ascii=False, indent=4)
    print(f'Scraped content saved to {json_file}')

def load_previous_scraped_data(json_file):
    """Load previously scraped content from a JSON file and return the set of URLs and a list of articles."""
    if os.path.exists(json_file):
        try:
            with open(json_file, mode='r', encoding='utf-8') as file:
                # Check if the file is empty
                if os.path.getsize(json_file) == 0:
                    return set(), []  
                data = json.load(file)
                # Ensure data is a list, not a dictionary
                if isinstance(data, list):
                    return {article['link'] for article in data}, data  
                else:
                    print(f"Error: {json_file} contains invalid data. Expected a list of articles.")
                    return set(), []  
        except json.JSONDecodeError:
            print(f"Error: {json_file} is not a valid JSON file or is empty.")
            return set(), []  
    else:
        return set(), [] 
    
def main():
    # Directory to save images
    image_save_dir = 'static/article_images'
    os.makedirs(image_save_dir, exist_ok=True)
    
    # JSON file to save scraped content
    json_file = 'posts/scraped_topic_content.json'
    
    # Load previously scraped data and URLs
    scraped_urls, scraped_content = load_previous_scraped_data(json_file)
    print(f"Loaded {len(scraped_urls)} previously scraped URLs.")

    # URL of the webpage to scrape
    url = 'https://www.theverge.com/tech' 
    
    # Fetch the page content
    page_content = fetch_page_content(url)
    if page_content:
        # Create a BeautifulSoup object and specify the parser
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Parse the articles
        articles = parse_most_popular_articles(soup)

        # Scrape each topic's content
        for title, link in articles:
            # Skip the article if it has already been scraped
            if link in scraped_urls:
                print(f"Skipping duplicate article: {title}")
                continue

            print(f'Scraping content for: {title}')
            
            # Add the URL to the set of scraped URLs
            scraped_urls.add(link)
            
            # Generate a unique ID for this article
            unique_id = str(uuid.uuid4())
            
            # Scrape body content
            body = scrape_topic_content(link)
            
            # Scrape and save the image
            image_url = scrape_image_url(link)
            if image_url:
                image_path = save_image(image_url, image_save_dir, unique_id)
            else:
                image_path = None

            # Save content along with image path
            scraped_content.append({
                'id': unique_id,
                'title': title,
                'body': body,
                'link': link,
                'image_path': image_path
            })

        # Save the updated scraped content to the JSON file
        save_scraped_content_to_json(scraped_content, json_file)

