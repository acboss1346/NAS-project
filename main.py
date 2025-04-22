import streamlit as st
from newspaper import Article
import nltk
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import random

# Initialize NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Configure app
st.set_page_config(page_title="📰 News Summarizer & Sentiment Analyzer")
st.title("📰 News Summarizer & Sentiment Analyzer")

# User input
url = st.text_input("Enter News Article URL", "https://www.bbc.com/news/world-us-canada-68767453")

def extract_article(url):
    """Improved article extraction with error handling and headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        # First try with requests + newspaper
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        article = Article(url)
        article.set_html(response.text)
        article.parse()
        article.nlp()
        
        return {
            'title': article.title,
            'authors': ', '.join(article.authors) if article.authors else "Not available",
            'publish_date': article.publish_date.strftime("%Y-%m-%d") if article.publish_date else "Not available",
            'summary': article.summary,
            'text': article.text,
            'image': article.top_image
        }

    except Exception as e:
        st.warning(f"Newspaper failed, trying fallback method... Error: {str(e)}")
        try:
            # Fallback to BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            return {
                'title': soup.title.string if soup.title else "No title found",
                'authors': "Not available (fallback)",
                'publish_date': "Not available (fallback)",
                'summary': ' '.join([p.get_text() for p in soup.find_all('p')][:3]),
                'text': ' '.join([p.get_text() for p in soup.find_all('p')]),
                'image': None
            }
        except Exception as fallback_error:
            st.error(f"Failed to extract article: {str(fallback_error)}")
            return None

# Process and display
if url:
    article_data = extract_article(url)
    
    if article_data:
        st.subheader("📰 Title")
        st.write(article_data['title'])

        st.subheader("✍️ Author(s)")
        st.write(article_data['authors'])

        st.subheader("📅 Publication Date")
        st.write(article_data['publish_date'])

        if article_data['image']:
            st.image(article_data['image'], caption="Article Image")

        st.subheader("📝 Summary")
        st.write(article_data['summary'])

        st.subheader("📊 Sentiment Analysis")
        blob = TextBlob(article_data['text'])
        polarity = blob.sentiment.polarity
        sentiment = "😊 Positive" if polarity > 0 else "😞 Negative" if polarity < 0 else "😐 Neutral"
        st.metric("Sentiment", sentiment, delta=f"{polarity:.2f} polarity")
        
        # Visual indicator
        st.progress((polarity + 1) / 2)