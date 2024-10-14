# download_models.py
from transformers import pipeline, BartTokenizer
from keybert import KeyBERT
import os

# Pre-download the tokenizer and model
os.environ["HF_HOME"] = "/app/huggingface_cache"
kw_model = KeyBERT()
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")