from apscheduler.schedulers.background import BackgroundScheduler
import time
from scraper import main as scrape_main
from post_generator import main as generate_posts_main
from post import main as post_main
from filelock import FileLock

# Load environment variables from .env file
PAGE_ACCESS_TOKEN = None
try:
    with open('/run/secrets/facebook_token.txt', 'r') as f:
        PAGE_ACCESS_TOKEN = f.read().strip()
except Exception as e:
    print(f"Error: {e}")
    
POSTS_JSON_PATH = 'posts/generated_posts.json'
LOCK_PATH = POSTS_JSON_PATH + '.lock'  # Lock file path

def main():
    # Step 1: Scrape new content
    print("Starting content scraping...")
    scrape_main()  # Scrape the articles and save to JSON

    # Step 2: Generate Facebook posts from the scraped content
    print("Generating Facebook posts...")
    generate_posts_main()  # Call the main function from post_generator

    # Step 3: Post to Facebook
    if PAGE_ACCESS_TOKEN:
        print("Posting to Facebook...")
        post_main(PAGE_ACCESS_TOKEN)  # Call the main function from post
    else:
        print("No Facebook Page Access Token found.")

def job_function():
    print("Job is running...")
    with FileLock(LOCK_PATH):
        main()

# Schedule the main function to run every 4 hours
if __name__ == "__main__":
    print("I am ALIVEEEEE main")
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_function, 'interval', seconds=10)
    scheduler.start()

    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
   