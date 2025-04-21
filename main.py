import streamlit as st
import nltk
from textblob import TextBlob
from newspaper import Article
from bs4 import BeautifulSoup
import requests

# 🧹 Clean NLTK resource check & download
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# 🩹 Override any misreference to 'punkt_tab' if caused by old cache (optional precaution)
if hasattr(nltk, 'data'):
    import os
    path = os.path.join(nltk.data.find("tokenizers/punkt"), '..', 'punkt_tab')
    if os.path.exists(path):
        os.remove(path)  # this will only run if some bad file exists

def extract_authors(url):
    """ Extract authors from multiple sources (Newspaper3k + BeautifulSoup) """
    article = Article(url)

    try:
        article.download()
        article.parse()
        article.nlp()

        pub_date = article.meta_data.get('datePublished', 'Not Available')
        authors = ', '.join(article.authors) if article.authors else "Not Available"

        st.write(f"Newspaper3k Authors: {article.authors}")
        st.write(f"Metadata: {article.meta_data}")

        if authors == "Not Available":
            possible_author_keys = ["author", "dc.creator", "byline"]
            for key in possible_author_keys:
                if key in article.meta_data:
                    authors = article.meta_data[key]
                    break

        if authors == "Not Available":
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            meta_authors = soup.find("meta", {"name": "author"})
            if meta_authors and meta_authors.get("content"):
                authors = meta_authors["content"]

        return article, pub_date, authors

    except Exception as e:
        st.error(f"Error Extracting Article: {e}")
        return None, None, "Error retrieving authors"

st.set_page_config(page_title="News Summarizer", layout="wide")
st.title("📰 News Summarizer & Sentiment Analyzer")

url = st.text_input("Enter News Article URL")

if st.button("Summarize"):
    if url:
        article, pub_date, authors = extract_authors(url)

        if article:
            st.subheader("Title")
            st.write(article.title)

            st.subheader("Author(s)")
            st.write(authors)

            st.subheader("Publication Date")
            st.write(pub_date)

            st.subheader("Summary")
            st.write(article.summary if article.summary else "Summary not available")

            analysis = TextBlob(article.text)
            polarity = analysis.polarity
            sentiment_value = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
            st.subheader("Sentiment Analysis")
            st.write(f"Polarity: {polarity:.2f}, Sentiment: {sentiment_value}")
        else:
            st.error("Failed to extract the article.")
    else:
        st.error("Please enter a valid URL.")
