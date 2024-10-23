import json
import facebook
import os


def post_to_facebook_page(message, photo_path, page_access_token):
    """Post message and photo to the Facebook page using the Graph API."""
    graph = facebook.GraphAPI(page_access_token)
    
    try:
        # Upload the photo and post the message
        with open(photo_path, 'rb') as photo:
            graph.put_photo(image=photo, message=message)
        print("Post posted successfully!")
        return True
    except facebook.GraphAPIError as e:
        print(f"Error posting to Facebook: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def update_post_status(posts, output_file):
    """Save the updated posts back to the JSON file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)
    print(f"Post statuses updated in {output_file}")

def main(page_access_token):
    """Main function to post approved content to Facebook."""
    # Step 1: Load the approved posts and find the first unposted one
    with open('posts/generated_posts.json', 'r', encoding='utf-8') as file:
        posts = json.load(file)

    post_to_publish = None
    for post in posts:
        if post['approved'] and not post['posted']:
            post_to_publish = post
            break

    if post_to_publish is None:
        print("No approved and unposted posts found.")
        return

    # Step 2: Post to Facebook
    print(f"Posting to Facebook: {post_to_publish['title']}")
    success = post_to_facebook_page(post_to_publish['post_content'], post_to_publish['image_path'], page_access_token)

    # Step 3: Update the post status and save if the posting was successful
    if success:
        post_to_publish['posted'] = True
        update_post_status(posts, 'posts/generated_posts.json')
    else:
        print("Failed to post on Facebook. No changes made.")
