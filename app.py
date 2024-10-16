from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import json
import os
from filelock import FileLock

app = Flask(__name__)

# Path to the generated_posts.json file and the image folder
POSTS_JSON_PATH = 'posts/generated_posts.json'
IMAGE_FOLDER = 'static/article_images' 
LOCK_PATH = POSTS_JSON_PATH + '.lock'  # Lock file path

# Function to load posts from the JSON file with locking
def load_posts():
    with FileLock(LOCK_PATH):
        with open(POSTS_JSON_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)

# Function to save updated posts to the JSON file with locking
def save_posts(posts):
    with FileLock(LOCK_PATH):
        with open(POSTS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(posts, file, ensure_ascii=False, indent=4)

# Route to display all unposted posts
@app.route('/')
def index():
    posts = load_posts()
    # Filter posts to show only those with "posted" == False
    unposted_posts = [post for post in posts if not post['posted']]
    return render_template('index.html', posts=unposted_posts)

# Route to serve images from the article_images folder
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# Route to handle approval form submission
@app.route('/approve', methods=['POST'])
def approve_posts():
    posts = load_posts()
    approved_posts = request.form.getlist('approved')
    
    for post in posts:
        if not post['posted']:  # Only modify unposted posts
            if post['title'] in approved_posts:
                post['approved'] = True  
            else:
                post['approved'] = False 
    # Save the updated posts
    save_posts(posts)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
