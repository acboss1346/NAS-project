import streamlit as st
from newspaper import Article
import nltk
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

st.title("📰 News Summarizer & Sentiment Analyzer")
url = st.text_input("Enter News Article URL")

def extract_authors(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        article = Article(url)
        article.set_html(response.text)
        article.download_state = 2  # Mark as downloaded
        article.parse()
        article.nlp()

        pub_date = article.publish_date.strftime("%Y-%m-%d") if article.publish_date else "Not Available"
        authors = ', '.join(article.authors) if article.authors else "Not Available"

        if authors == "Not Available":
            soup = BeautifulSoup(response.text, "html.parser")
            meta_authors = soup.find("meta", {"name": "author"})
            if meta_authors and meta_authors.get("content"):
                authors = meta_authors["content"]

        return article, pub_date, authors

    except Exception as e:
        st.error(f"Error Extracting Article: {e}")
        return None, None, None

if url:
    article, pub_date, authors = extract_authors(url)
    if article:
        st.subheader("📰 Title")
        st.write(article.title)

        st.subheader("✍️ Author(s)")
        st.write(authors)

        st.subheader("📅 Publication Date")
        st.write(pub_date)

        st.subheader("📝 Summary")
        st.write(article.summary)

        st.subheader("📊 Sentiment Analysis")
        blob = TextBlob(article.text)
        polarity = blob.sentiment.polarity
        sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
        st.write(f"Polarity: {polarity:.2f}, Sentiment: {sentiment}")