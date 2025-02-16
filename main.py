import tkinter as tk
import nltk
from textblob import TextBlob
from newspaper import Article
from bs4 import BeautifulSoup
import requests

# Download NLTK data
try:
    nltk.download("punkt")
except Exception as e:
    print(f"NLTK Download Error: {e}")

def extract_authors(url):
    """ Extract authors from multiple sources (Newspaper3k + BeautifulSoup) """
    article = Article(url)

    try:
        article.download()
        article.parse()
        article.nlp()

        # Extract Metadata
        pub_date = article.meta_data.get('datePublished', 'Not Available')

        # Extract Authors (Improved)
        authors = ', '.join(article.authors) if article.authors else "Not Available"

        # Debugging Info
        print(f"Newspaper3k Authors: {article.authors}")
        print(f"Metadata: {article.meta_data}")

        # Check alternative metadata fields
        if authors == "Not Available":
            possible_author_keys = ["author", "dc.creator", "byline"]
            for key in possible_author_keys:
                if key in article.meta_data:
                    authors = article.meta_data[key]
                    break

        # If still not found, use BeautifulSoup as a fallback
        if authors == "Not Available":
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            meta_authors = soup.find("meta", {"name": "author"})
            if meta_authors and meta_authors.get("content"):
                authors = meta_authors["content"]

        return article, pub_date, authors

    except Exception as e:
        print(f"Error Extracting Article: {e}")
        return None, None, "Error retrieving authors"

def summarize():
    url = utext.get('1.0', "end").strip()

    article, pub_date, authors = extract_authors(url)

    if article is None:
        return  # Exit if there's an error in fetching the article

    # Extract Summary
    summary_text = article.summary if article.summary else "Summary not available"

    # Sentiment Analysis
    analysis = TextBlob(article.text)
    polarity = analysis.polarity
    sentiment_value = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

    # Enable Text Widgets Before Updating
    for widget in [title, author, publication, summary, sentiment]:
        widget.config(state="normal")
        widget.delete('1.0', 'end')

    # Insert Data
    title.insert('1.0', article.title)
    author.insert('1.0', authors)
    publication.insert('1.0', pub_date)
    summary.insert('1.0', summary_text)
    sentiment.insert('1.0', f'Polarity: {polarity:.2f}, Sentiment: {sentiment_value}')

    # Disable Text Widgets After Updating
    for widget in [title, author, publication, summary, sentiment]:
        widget.config(state="disabled")

# GUI Window
root = tk.Tk()
root.title("News Summarizer")
root.configure(bg="#1e1e1e")  # Dark background

# Set Full Screen for Mac
root.attributes('-fullscreen', True)

def create_label(text):
    return tk.Label(root, text=text, fg="#ffffff", bg="#1e1e1e", font=("Arial", 14, "bold"))

def create_text_widget(height, wrap=tk.WORD):
    widget = tk.Text(root, height=height, width=150, state='disabled', bg="#2b2b2b", fg="#ffffff", font=("Arial", 14), wrap=wrap)
    return widget

# Title
create_label('Title').pack(pady=10)
title = create_text_widget(2)
title.pack(padx=20, pady=5)

# Author
create_label('Author').pack(pady=10)
author = create_text_widget(2)
author.pack(padx=20, pady=5)

# Publication Date
create_label('Publication Date').pack(pady=10)
publication = create_text_widget(2)
publication.pack(padx=20, pady=5)

# Summary (Added Scrollbar)
create_label('Summary').pack(pady=10)
summary_frame = tk.Frame(root)
summary_scroll = tk.Scrollbar(summary_frame, orient="vertical")
summary = tk.Text(summary_frame, height=20, width=150, state='disabled', bg="#2b2b2b", fg="#ffffff", font=("Arial", 14), wrap=tk.WORD, yscrollcommand=summary_scroll.set)
summary_scroll.config(command=summary.yview)
summary_scroll.pack(side="right", fill="y")
summary.pack(side="left", fill="both", expand=True)
summary_frame.pack(padx=20, pady=5, fill="both", expand=True)

# Sentiment Analysis
create_label('Sentiment Analysis').pack(pady=10)
sentiment = create_text_widget(2)
sentiment.pack(padx=20, pady=5)

# URL Input
create_label('Enter URL:').pack(pady=10)
utext = tk.Text(root, height=2, width=150, bg="#2b2b2b", fg="#ffffff", font=("Arial", 14))
utext.pack(padx=20, pady=5)

# Summarize Button
btn = tk.Button(root, text="Summarize", command=summarize, bg="#007acc", fg="white", font=("Arial", 14, "bold"), height=2, width=20)
btn.pack(pady=20)

# Exit Button
exit_btn = tk.Button(root, text="Exit", command=root.quit, bg="#ff4444", fg="white", font=("Arial", 14, "bold"), height=2, width=20)
exit_btn.pack(pady=10)

root.mainloop()
