# download_models.py
from transformers import pipeline, BartTokenizer
from keybert import KeyBERT

# Pre-download the tokenizer and model
kw_model = KeyBERT()
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")