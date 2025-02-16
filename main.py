import tkinter as tk
import nltk
from textblob import TextBlob
from newspaper import Article

try:
    nltk.download("punkt")
except Exception as e:
    print(f"NLTK Download Error: {e}")

def summarize():
    url = utext.get('1.0', "end").strip()
    article = Article(url)

    try:
        article.download()
        article.parse()
        article.nlp()

        pub_date = article.meta_data.get('datePublished', 'Not Available')
        authors = ', '.join(article.authors) if article.authors else "Not Available"
        summary_text = article.summary if article.summary else "Summary not available"

        analysis = TextBlob(article.text)
        polarity = analysis.polarity
        sentiment_value = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

        # Enable Text Widgets
        for widget in [title, author, publication, summary, sentiment]:
            widget.config(state="normal")
            widget.delete('1.0', 'end')

        # Insert Data
        title.insert('1.0', article.title)
        author.insert('1.0', authors)
        publication.insert('1.0', pub_date)
        summary.insert('1.0', summary_text)
        sentiment.insert('1.0', f'Polarity: {polarity:.2f}, Sentiment: {sentiment_value}')

        # Disable Text Widgets Again
        for widget in [title, author, publication, summary, sentiment]:
            widget.config(state="disabled")

    except Exception as e:
        print(f"Error: {e}")

# GUI Window
root = tk.Tk()
root.title("News Summarizer")
root.configure(bg="#1e1e1e")  # Dark background

# Set Full Screen for Mac
root.attributes('-fullscreen', True)

def create_label(text):
    return tk.Label(root, text=text, fg="#ffffff", bg="#1e1e1e", font=("Arial", 14, "bold"))

def create_text_widget(height):
    return tk.Text(root, height=height, width=150, state='disabled', bg="#2b2b2b", fg="#ffffff", font=("Arial", 14))

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

# Summary
create_label('Summary').pack(pady=10)
summary = create_text_widget(20)
summary.pack(padx=20, pady=5)

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
