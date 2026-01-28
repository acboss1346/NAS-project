import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from textblob import TextBlob
import nltk
import time
import socket
from urllib.parse import urlparse
import ipaddress

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
    except Exception as e:
        pass

st.set_page_config(
    page_title="AI News Insights",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_custom_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        .stApp {
            background: radial-gradient(circle at top left, #1e1e2f, #121212);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #f0f2f5;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        h1 {
            font-size: 3rem;
            background: -webkit-linear-gradient(45deg, #6a11cb, #2575fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }

        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.05);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px 16px;
            transition: all 0.3s ease;
        }
        .stTextInput > div > div > input:focus {
            background-color: rgba(255, 255, 255, 0.1);
            border-color: #2575fc;
            box-shadow: 0 0 10px rgba(37, 117, 252, 0.3);
        }

        .css-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .metric-container {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            padding: 20px;
            background: rgba(37, 117, 252, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(37, 117, 252, 0.2);
        }

        .stButton > button {
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 50px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(37, 117, 252, 0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(37, 117, 252, 0.6);
            color: white;
        }
        
        footer {visibility: hidden;}
        
    </style>
    """

def is_safe_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False, "Invalid URL scheme. Only HTTP and HTTPS are allowed."
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL: No hostname found."
            
        ip = socket.gethostbyname(hostname)
        ip_addr = ipaddress.ip_address(ip)
        
        if ip_addr.is_private or ip_addr.is_loopback:
            return False, "Access to local or private network resources is restricted."
            
        return True, ""
    except Exception as e:
        return False, f"URL Validation Error: {str(e)}"

def get_sentiment_emoji(polarity):
    if polarity > 0.1:
        return "😊", "Positive"
    elif polarity < -0.1:
        return "😞", "Negative"
    else:
        return "😐", "Neutral"

def extract_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    data = {}
    
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        article = Article(url)
        article.download(input_html=response.text)
        article.parse()
        
        try:
            article.nlp()
        except:
            pass

        data['title'] = article.title
        data['text'] = article.text
        data['summary'] = article.summary if article.summary else article.text[:500] + "..."
        data['authors'] = list(article.authors)
        data['publish_date'] = article.publish_date
        data['image'] = article.top_image
        
    except Exception as e:
        print(f"Newspaper3k failed: {e}")
        try:
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            h1 = soup.find('h1')
            data['title'] = h1.get_text().strip() if h1 else (soup.title.get_text() if soup.title else "Unknown Title")
            
            for garbage in soup(["script", "style", "nav", "header", "footer", "aside", "noscript", "iframe"]):
                garbage.decompose()

            paragraphs = soup.find_all('p')
            valid_paragraphs = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40]
            text_content = ' '.join(valid_paragraphs)
            
            data['text'] = text_content
            data['summary'] = text_content[:500] + "..."
            
            data['authors'] = []
            data['publish_date'] = None
            
            og_image = soup.find('meta', property='og:image')
            data['image'] = og_image['content'] if og_image else None
            
        except Exception as e2:
            print(f"Fallback extraction failed: {e2}")
            return None

    if not data.get('title'):
        data['title'] = "Unknown Title"
    
    if not data.get('text') or len(data['text']) < 50:
         return None

    return data

st.markdown(get_custom_css(), unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2965/2965879.png", width=80)
    st.title("AI Settings")
    st.markdown("---")
    st.info("This tool uses **NLP** to summarize news articles and analyze sentiment.")
    st.markdown("### How to use:")
    st.markdown("1. Paste a news article URL.")
    st.markdown("2. View the summary and stats.")
    st.markdown("---")
    st.caption("v2.1 • Enhanced Security")

col1, col2 = st.columns([3, 1])
with col1:
    st.title("News Article Summarizer")
    st.markdown("#### Transform long readings into quick insights.")

# Input Area
st.markdown("<br>", unsafe_allow_html=True)
url_input = st.text_input("🔗 Paste Article URL", placeholder="https://example.com/article...", help="Paste the full URL of the news article you want to summarize.")

if url_input:
    # 1. Validation Logic
    is_valid, message = is_safe_url(url_input)
    
    if not is_valid:
        st.error(f"❌ {message}")
    else:
        with st.spinner("🔍 Reading article..."):
            try:
                article_data = extract_article(url_input)
                
                if article_data:
                    # --- Analysis ---
                    blob = TextBlob(article_data['text'])
                    polarity = blob.sentiment.polarity
                    subjectivity = blob.sentiment.subjectivity
                    emoji, sentiment_label = get_sentiment_emoji(polarity)
                    
                    word_count = len(article_data['text'].split())
                    read_time = max(1, round(word_count / 200)) # Approx 200 wpm

                    # --- Results UI ---
                    st.markdown("---")
                    
                    # Header Section (Title + Image)
                    if article_data.get('image'):
                        st.image(article_data['image'], use_container_width=True, clamp=True)
                    
                    st.markdown(f"## {article_data['title']}")
                    
                    meta_cols = st.columns(3)
                    with meta_cols[0]:
                        authors = ", ".join(article_data['authors']) if article_data['authors'] else "Unknown Author"
                        st.caption(f"✍️ **{authors}**")
                    with meta_cols[1]:
                        date = article_data['publish_date'].strftime('%Y-%m-%d') if article_data['publish_date'] else "Unknown Date"
                        st.caption(f"📅 **{date}**")
                    with meta_cols[2]:
                        st.caption(f"⏱️ **{read_time} min read**")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Two Column Layout for Summary & Stats
                    col_content, col_stats = st.columns([2, 1])
                    
                    with col_content:
                        st.markdown("### 📝 Executive Summary")
                        st.info(article_data['summary'])
                        
                        with st.expander("📖 Read Full Article"):
                            st.write(article_data['text'])

                    with col_stats:
                        st.markdown("### 📊 Analysis")
                        
                        st.markdown(f"""
                        <div class="css-card">
                            <div style="font-size: 40px; text-align: center;">{emoji}</div>
                            <h3 style="text-align: center; margin: 0; color: #fff;">{sentiment_label}</h3>
                            <p style="text-align: center; color: #aaa; font-size: 14px;">Sentiment Score</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.progress((polarity + 1) / 2)
                        st.caption(f"Polarity: {polarity:.2f} ( -1 to +1 )")
                        
                        st.divider()
                        
                        st.metric("Subjectivity", f"{subjectivity:.2f}", help="0 is objective, 1 is subjective")
                        st.metric("Word Count", word_count)

                else:
                    st.error("❌ Could not extract article content. The website might be blocking scrapers or the content is empty.")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
else:
    # Empty state placeholder
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; color: #555;">
            <h3>Start by pasting a URL above 👆</h3>
        </div>
        """, unsafe_allow_html=True
    )
