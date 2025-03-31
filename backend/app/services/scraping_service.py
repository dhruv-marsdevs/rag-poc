import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Set, Any, Optional
import uuid
from datetime import datetime
import tempfile
import time
import shutil

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class WebScraper:
    """Service for scraping websites and saving content"""
    
    def __init__(self, base_url: str, max_pages: int = 50, max_depth: int = 3):
        """
        Initialize the web scraper
        
        Args:
            base_url: The starting URL to scrape
            max_pages: Maximum number of pages to scrape
            max_depth: Maximum depth of links to follow
        """
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.pages_scraped = 0
        self.pages_queue: List[Dict[str, Any]] = []
        self.content: List[Dict[str, Any]] = []
    
    def start_scraping(self) -> Dict[str, Any]:
        """
        Start the scraping process from the base URL
        
        Returns:
            Dict with scraping results
        """
        logger.info(f"Starting to scrape website: {self.base_url}")
        start_time = time.time()
        
        # Add the base URL to the queue
        self.pages_queue.append({"url": self.base_url, "depth": 0})
        
        # Process queue until empty or limits reached
        while self.pages_queue and self.pages_scraped < self.max_pages:
            # Get next URL from queue
            page_info = self.pages_queue.pop(0)
            current_url = page_info["url"]
            current_depth = page_info["depth"]
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
            
            # Mark as visited
            self.visited_urls.add(current_url)
            
            try:
                # Scrape the page
                soup, links = self._scrape_page(current_url)
                if soup:
                    self.pages_scraped += 1
                    logger.info(f"Scraped page {self.pages_scraped}: {current_url}")
                    
                    # Extract and save content
                    title = soup.title.string if soup.title else "No title"
                    text = self._extract_text(soup)
                    
                    # Save content
                    self.content.append({
                        "url": current_url,
                        "title": title,
                        "text": text,
                        "scraped_at": datetime.utcnow().isoformat()
                    })
                    
                    # If not at max depth, add links to queue
                    if current_depth < self.max_depth:
                        for link in links:
                            if link not in self.visited_urls:
                                self.pages_queue.append({
                                    "url": link,
                                    "depth": current_depth + 1
                                })
            
            except Exception as e:
                logger.error(f"Error scraping {current_url}: {str(e)}")
        
        # Calculate total time
        total_time = time.time() - start_time
        
        logger.info(f"Finished scraping {self.pages_scraped} pages in {total_time:.2f} seconds")
        
        return {
            "pages_scraped": self.pages_scraped,
            "time_taken": total_time,
            "base_url": self.base_url
        }
    
    def _scrape_page(self, url: str) -> tuple:
        """
        Scrape a single page
        
        Args:
            url: URL to scrape
            
        Returns:
            Tuple of (BeautifulSoup object, list of links)
        """
        try:
            # Add delay to be respectful
            time.sleep(1)
            
            # Make request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract links
            links = self._extract_links(soup, url)
            
            return soup, links
        
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None, []
    
    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Extract valid links from page
        
        Args:
            soup: BeautifulSoup object
            current_url: Current URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = []
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            
            # Skip empty links, anchors, javascript, mailto
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue
            
            # Convert to absolute URL
            absolute_link = urljoin(current_url, href)
            
            # Parse the URL
            parsed_link = urlparse(absolute_link)
            
            # Only keep links from the same domain
            if parsed_link.netloc == self.base_domain:
                # Remove fragments
                clean_link = absolute_link.split("#")[0]
                if clean_link and clean_link not in links:
                    links.append(clean_link)
        
        return links
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract readable text from page
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Cleaned text content
        """
        # Remove script and style elements
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.extract()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a single line
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Join lines, removing empty ones
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def save_to_document(self, user_id: str) -> Dict[str, Any]:
        """
        Save scraped content as a document
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with document info
        """
        if not self.content:
            logger.warning("No content to save")
            return {"error": "No content scraped"}
        
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Create a temporary file to store the content
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
                # Write metadata
                temp_file.write(f"Website: {self.base_url}\n")
                temp_file.write(f"Scraped: {datetime.utcnow().isoformat()}\n")
                temp_file.write(f"Pages: {self.pages_scraped}\n\n")
                temp_file.write("=" * 80 + "\n\n")
                
                # Write content for each page
                for page in self.content:
                    temp_file.write(f"URL: {page['url']}\n")
                    temp_file.write(f"Title: {page['title']}\n\n")
                    temp_file.write(page['text'])
                    temp_file.write("\n\n" + "=" * 80 + "\n\n")
            
            # Create sanitized filename for the domain
            domain_name = self.base_domain.replace(".", "_")
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            original_filename = f"web_{domain_name}_{timestamp}.txt"
            safe_filename = f"{document_id}_{original_filename}"
            
            # Move to permanent location
            os.makedirs(settings.DOCUMENTS_DIRECTORY, exist_ok=True)
            final_path = os.path.join(settings.DOCUMENTS_DIRECTORY, safe_filename)
            shutil.move(temp_file.name, final_path)
            
            logger.info(f"Saved scraped content to {final_path}")
            
            # Return document info
            return {
                "id": document_id,
                "filename": original_filename,
                "pages_scraped": self.pages_scraped,
                "content_type": "text/plain",
                "size": os.path.getsize(final_path)
            }
            
        except Exception as e:
            logger.error(f"Error saving scraped content: {str(e)}", exc_info=True)
            return {"error": f"Error saving scraped content: {str(e)}"}


def scrape_website(url: str, user_id: str, max_pages: int = 50, max_depth: int = 3) -> Dict[str, Any]:
    """
    Scrape a website and save content as a document
    
    Args:
        url: URL to scrape
        user_id: ID of the user
        max_pages: Maximum number of pages to scrape
        max_depth: Maximum depth of links to follow
        
    Returns:
        Dict with document info
    """
    try:
        # Create scraper
        scraper = WebScraper(url, max_pages, max_depth)
        
        # Start scraping
        scraping_result = scraper.start_scraping()
        
        # Save to document
        document_info = scraper.save_to_document(user_id)
        
        # If document was saved successfully, process it for the vector store
        if "error" not in document_info:
            try:
                # Get document path
                domain_name = scraper.base_domain.replace(".", "_")
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                original_filename = f"web_{domain_name}_{timestamp}.txt"
                safe_filename = f"{document_info['id']}_{original_filename}"
                file_path = os.path.join(settings.DOCUMENTS_DIRECTORY, safe_filename)
                
                # Process the document for the vector store
                from app.services.document_service import process_document
                process_document(
                    file_path=file_path,
                    document_id=document_info['id'],
                    filename=document_info['filename'],
                    user_id=user_id
                )
                
                logger.info(f"Website content processed for vector store: {document_info['id']}")
            except Exception as e:
                logger.error(f"Error processing scraped content for vector store: {str(e)}", exc_info=True)
                # We still return the document info since the file was saved successfully
        
        # Return combined info
        return {**scraping_result, **document_info}
    
    except Exception as e:
        logger.error(f"Error scraping website {url}: {str(e)}", exc_info=True)
        return {"error": f"Error scraping website: {str(e)}"} 