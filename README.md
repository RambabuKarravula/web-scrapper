# Web Content Scraper 🌐

A powerful and user-friendly web scraping application built with Streamlit that allows users to recursively extract content from websites. The scraper collects text content, links, images, and metadata while respecting website crawling etiquette.

![image](https://github.com/user-attachments/assets/7905a211-b291-417a-9952-4cc25291cec9)


## Live Demo 🌐

Try out the live version of the Web Content Scraper:
[https://web-scrapper-ijdv.onrender.com](https://web-scrapper-ijdv.onrender.com)

## Features ✨

- 🔄 Recursive web crawling from a single starting URL
- 📑 Extracts multiple content types:
  - Page titles and meta descriptions
  - Headings (H1-H6)
  - Paragraphs and text content
  - Links and navigation structure
  - Images with alt text
- 📊 Real-time progress tracking
- 🔄 Rotating user agents for better request management
- 📦 Content export in multiple formats (JSON, CSV)
- 🖼️ Automatic image downloading and organization
- ⚡ Performance metrics and statistics
- 🎯 Domain-specific crawling (stays within the same domain)

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/RambabuKarravula/web-scrapper.git
cd web-scrapper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies 📚

Create a `requirements.txt` file with the following contents:

```txt
streamlit
requests
beautifulsoup4
pandas
```

## Usage 💻

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (typically `http://localhost:8501`)

3. Enter the website URL you want to scrape in the input field

4. Wait for the scraping process to complete

5. Download the extracted content using the "Download All Content" button

## Output Format 📄

The scraper generates a ZIP file containing:

### 1. scraped_data.json
Contains all extracted data in JSON format:
```json
{
    "url": {
        "title": "Page Title",
        "meta_description": "Page meta description",
        "headings": [
            {
                "level": "h1",
                "text": "Heading text"
            }
        ],
        "paragraphs": ["Paragraph text"],
        "links": [
            {
                "text": "Link text",
                "url": "Link URL"
            }
        ],
        "images": [
            {
                "src": "Image source URL",
                "alt": "Image alt text",
                "data": "Base64 encoded image data"
            }
        ]
    }
}
```

### 2. links.csv
A CSV file containing all extracted links with columns:
- source_url
- link_text
- link_url

### 3. images/ directory
Contains all downloaded images, named according to their source page

## Features in Detail 🔍

### Intelligent Crawling
- Respects same-domain policy
- Implements polite crawling with delays
- Avoids duplicate page visits
- Handles relative and absolute URLs

### Error Handling
- Graceful handling of network errors
- Timeout management
- Invalid URL detection
- Image download failure recovery

### Performance Optimization
- Session reuse for better performance
- User agent rotation
- Efficient memory management
- Progress tracking

## Best Practices 📌

1. Always check the website's robots.txt file before scraping
2. Implement reasonable delays between requests (currently set to 0.5 seconds)
3. Use the tool responsibly and in accordance with the website's terms of service
4. Be mindful of server load and bandwidth usage

## Limitations ⚠️

- JavaScript-rendered content cannot be scraped
- Some websites may block automated access
- Rate limiting may affect scraping speed
- Large websites may take significant time to scrape completely

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/featur`)
3. Commit your changes (`git commit -m 'Add some Feature'`)
4. Push to the branch (`git push origin feature/Feature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Built with [Streamlit](https://streamlit.io/)
- Uses [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- Inspired by the need for an easy-to-use web scraping tool

## Support 💬

For support, please open an issue in the GitHub repository or contact [karravularambabu@gmail.com]
