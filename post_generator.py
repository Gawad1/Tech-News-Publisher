import json
import os
from transformers import pipeline, BartTokenizer
from keybert import KeyBERT
import random


os.environ["HF_HOME"] = "/app/huggingface_cache"

# Initialize models
kw_model = KeyBERT()
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Emoji and title prefixes
breaking_emojis = ['🚨', '📰', '⚡️', '🌟']
summary_emojis = ['📢', '🔍', '📄', '🗣️', '✨']
cta_emojis = ['🤔', '🗨️', '❓', '💭']
link_emojis = ['👉', '🔗']
title_prefixes = ['BREAKING', 'LATEST', 'JUST IN', 'EXCLUSIVE', 'SPOTLIGHT', 'ANNOUNCEMENT', 'HEADS UP']

def load_scraped_content(json_file):
    """Load scraped content from a JSON file."""
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_previous_posts(output_file):
    """Load previously generated posts."""
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def smart_summarize(body):
    """Summarize the body of the article using the Hugging Face summarization model."""
    try:
        # Tokenize the body
        tokens = tokenizer(body, return_tensors="pt")

        # Truncate the body if the number of tokens exceeds 1022
        if tokens['input_ids'].shape[1] > 1022:
            body = tokenizer.decode(tokens['input_ids'][0][:1022], skip_special_tokens=True)

        # Set max_length to one-third of the body length in tokens
        max_length = max(50, len(tokenizer(body)['input_ids']) // 3)
        min_length = max(40, max_length // 2)

        # Generate a summary for the body
        summary = summarizer(body, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
        return summary.strip()
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return None

def generate_hashtags(summary):
    """Generate hashtags from the summary using KeyBERT."""
    # Extract keywords from the summary
    keywords = kw_model.extract_keywords(summary, top_n=5)

    # Create hashtags from the keywords
    hashtags = [f"#{keyword[0].replace(' ', '')}" for keyword in keywords]

    return hashtags

def generate_facebook_post(title, body, link, image_path=None):
    """Generate an engaging Facebook post using a summary."""
    # Summarize the body of the article
    summary = smart_summarize(body)
    breaking_emoji = random.choice(breaking_emojis)
    summary_emoji = random.choice(summary_emojis)
    cta_emoji = random.choice(cta_emojis)
    link_emoji = random.choice(link_emojis)
    title_prefix = random.choice(title_prefixes)

    if summary:
        # Format the post content
        hashtags = generate_hashtags(summary)
        hashtags_str = ' '.join(hashtags)

        post_content = f"""{breaking_emoji} {title_prefix}: {title}

{summary_emoji} {summary}

{cta_emoji} What are your thoughts on this news? Share your thoughts below!

{link_emoji} Full story: {link}

#TechNews #TheVerge #LatestTech {hashtags_str}
        """
        return {
            "title": title,
            "link": link,
            "image_path": image_path,
            "post_content": post_content.strip(),
            "approved": False,  # Post not approved yet
            "posted": False     # Post not yet published
        }
    else:
        return None

def generate_posts(scraped_content, existing_links):
    """Generate Facebook posts based on scraped content."""
    posts = []
    for item in scraped_content:
        title = item.get('title', 'No Title')
        body = item.get('body', 'No Body')
        link = item.get('link', 'No Link')
        image_path = item.get('image_path', None)

        # Skip the article if it has already been posted
        if link in existing_links:
            print(f"Skipping duplicate post for: {title}")
            continue

        # Generate the Facebook post
        facebook_post = generate_facebook_post(title, body, link, image_path)

        if facebook_post:
            posts.append(facebook_post)
            print(f"Generated post for: {title}")
        else:
            print(f"Failed to generate post for: {title}")
    return posts

def save_posts_to_json(posts, output_file):
    """Save generated posts to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)
    print(f'Posts saved to {output_file}')

def review_posts(posts_file):
    """Review generated posts and mark them as approved or not."""
    # Load posts
    with open(posts_file, 'r', encoding='utf-8') as file:
        posts = json.load(file)

    # Iterate over unapproved posts for review
    for post in posts:
        if not post['approved']:  # Only review unapproved posts
            print(f"Title: {post['title']}")
            print(f"Content:\n{post['post_content']}")
            print(f"Link: {post['link']}")
            decision = input("Approve this post? (y/n): ").strip().lower()

            if decision == 'y':
                post['approved'] = True
                print("Post approved.")
            else:
                print("Post rejected.")

    # Save the updated posts back to the file
    save_posts_to_json(posts, posts_file)

def main():
    # Define the path to your JSON files
    scraped_content_json = 'posts/scraped_topic_content.json'
    posts_file = 'posts/generated_posts.json'

    # Load scraped content
    scraped_content = load_scraped_content(scraped_content_json)

    # Load previously generated posts
    previous_posts = load_previous_posts(posts_file)
    print(f"Loaded {len(previous_posts)} previously generated posts.")
    existing_links = {post['link'] for post in previous_posts}

    # Generate new posts, avoiding duplicates
    new_posts = generate_posts(scraped_content, existing_links)

    # Combine new posts with previous ones
    all_posts = previous_posts + new_posts

    # Save combined posts to the file
    save_posts_to_json(all_posts, posts_file)