import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, urljoin
import json
from datetime import datetime
import queue
from collections import defaultdict
import re
import base64
from io import BytesIO
import zipfile
import time
import random

class WebScraper:
    def __init__(self):
        self.visited_urls = set()
        self.results = defaultdict(dict)
        self.base_url = None
        self.session = self.setup_session()
        
    def setup_session(self):
        """Configure requests session with rotating user agents"""
        session = requests.Session()
        # List of common user agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        ]
        return session

    def get_headers(self):
        """Generate headers for requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def is_valid_url(self, url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def normalize_url(self, url, parent_url):
        """Normalize URL and filter invalid ones"""
        if not url:
            return None
        if url.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')):
            return None
        try:
            normalized = urljoin(parent_url, url)
            # Ensure URL is from same domain
            if urlparse(normalized).netloc == self.base_url:
                return normalized
            return None
        except:
            return None

    def download_image(self, url):
        """Download and encode image"""
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode()
            return None
        except:
            return None

    def scrape_page(self, url):
        """Scrape single page content"""
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)
        
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            st.error(f"Error scraping {url}: {str(e)}")
            return None

        # Extract content
        content = {
            'title': soup.title.string if soup.title else '',
            'meta_description': '',
            'headings': [],
            'paragraphs': [],
            'links': [],
            'images': []
        }

        # Get meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            content['meta_description'] = meta_desc.get('content', '')

        # Extract headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = heading.get_text(strip=True)
            if text:
                content['headings'].append({
                    'level': heading.name,
                    'text': text
                })

        # Extract paragraphs
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                content['paragraphs'].append(text)

        # Extract links
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text(strip=True)
            normalized_url = self.normalize_url(href, url)
            if normalized_url and text:
                content['links'].append({
                    'text': text,
                    'url': normalized_url
                })

        # Extract images
        for img in soup.find_all('img'):
            src = img.get('src')
            alt = img.get('alt', '')
            normalized_src = self.normalize_url(src, url)
            if normalized_src:
                img_data = self.download_image(normalized_src)
                if img_data:
                    content['images'].append({
                        'src': normalized_src,
                        'alt': alt,
                        'data': img_data
                    })

        self.results[url] = content
        return content

    def recursive_scrape(self, start_url, progress_bar=None):
        """Recursively scrape website"""
        self.base_url = urlparse(start_url).netloc
        self.visited_urls.clear()
        self.results.clear()

        urls_to_visit = queue.Queue()
        urls_to_visit.put(start_url)
        total_processed = 0

        while not urls_to_visit.empty():
            current_url = urls_to_visit.get()
            if current_url in self.visited_urls:
                continue

            content = self.scrape_page(current_url)
            total_processed += 1
            
            if progress_bar is not None:
                progress_bar.text(f"Processed {total_processed} pages | Current URL: {current_url}")

            if content:
                for link in content['links']:
                    new_url = link['url']
                    if new_url and new_url not in self.visited_urls:
                        urls_to_visit.put(new_url)

            # Add delay to prevent overwhelming the server
            time.sleep(0.5)

        return self.results

def create_download_zip(data):
    """Create ZIP file with scraped content"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Save complete data as JSON
        zip_file.writestr('scraped_data.json', 
                         json.dumps(data, indent=2, ensure_ascii=False))
        
        # Save links as CSV
        links_data = []
        for url, content in data.items():
            for link in content['links']:
                links_data.append({
                    'source_url': url,
                    'link_text': link['text'],
                    'link_url': link['url']
                })
        if links_data:
            df_links = pd.DataFrame(links_data)
            zip_file.writestr('links.csv', df_links.to_csv(index=False))
        
        # Save images
        for url, content in data.items():
            for i, img in enumerate(content['images']):
                if 'data' in img:
                    try:
                        img_data = base64.b64decode(img['data'])
                        img_filename = f"images/{urlparse(url).netloc}_{i}.png"
                        zip_file.writestr(img_filename, img_data)
                    except Exception as e:
                        st.warning(f"Could not save image {i} from {url}")

    return zip_buffer.getvalue()

def main():
    # Page configuration
    st.set_page_config(
        page_title="Web Content Scraper",
        page_icon="🌐",
        layout="wide"
    )

    # Custom styling
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(to right, #4CAF50, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .subheader {
            color: #666;
            font-size: 20px;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<p class="main-header">🌐 Web Content Scraper</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Extract content from any website automatically using single main URL</p>', unsafe_allow_html=True)

    # Input URL
    url = st.text_input("Enter website URL to scrape:", 
                       help="Enter the full URL including http:// or https://")

    if url:
        scraper = WebScraper()
        if not scraper.is_valid_url(url):
            st.error("⚠️ Please enter a valid URL")
            return

        progress_placeholder = st.empty()

        try:
            with st.spinner("🔄 Scraping website content..."):
                start_time = time.time()
                results = scraper.recursive_scrape(url, progress_placeholder)
                end_time = time.time()
                
                if results:
                    # Display statistics
                    total_pages = len(results)
                    total_links = sum(len(content['links']) for content in results.values())
                    total_images = sum(len(content['images']) for content in results.values())
                    
                    st.success(f"✅ Successfully scraped {total_pages} pages!")
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Pages Scraped", total_pages)
                    with col2:
                        st.metric("Links Found", total_links)
                    with col3:
                        st.metric("Images Found", total_images)
                    with col4:
                        st.metric("Time Taken", f"{end_time - start_time:.1f}s")

                    # Create download
                    zip_data = create_download_zip(results)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download All Content",
                        data=zip_data,
                        file_name=f"website_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        help="Download all scraped content including images and data"
                    )

                    # Display sample content
                    st.subheader("📄 Sample Content")
                    if results:
                        sample_url = next(iter(results))
                        st.write("**Title:**", results[sample_url]['title'])
                        if results[sample_url]['paragraphs']:
                            st.write("**Sample Text:**")
                            st.write(results[sample_url]['paragraphs'][0][:300] + "...")

                else:
                    st.warning("No content was found. Please check the URL and try again.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()