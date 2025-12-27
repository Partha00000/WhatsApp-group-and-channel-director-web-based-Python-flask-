import requests
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

def fetch_group_image(invite_link):
    """
    Fetch WhatsApp group image from invite link
    Returns the image URL or None if not found
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(invite_link, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image['content']
            
            # Look for Twitter card image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                return twitter_image['content']
            
            # Look for any img tag with WhatsApp patterns
            images = soup.find_all('img')
            for img in images:
                src = img.get('src', '')
                if 'whatsapp' in src.lower() or 'pps.whatsapp.net' in src:
                    return src
        
        logger.warning(f"Could not fetch image from {invite_link}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching group image from {invite_link}: {str(e)}")
        return None

def get_group_info(invite_link):
    """
    Get basic group information from WhatsApp invite link
    Returns dict with name, description, image_url, member_count
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(invite_link, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract group name
        group_name = None
        title_tag = soup.find('title')
        if title_tag:
            group_name = title_tag.get_text().strip()
        
        # Extract description from meta tags
        description = None
        desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', property='og:description')
        if desc_tag:
            description = desc_tag.get('content', '').strip()
        
        # Extract image
        image_url = fetch_group_image(invite_link)
        
        # Try to extract member count (this might not always be available)
        member_count = 0
        text_content = soup.get_text()
        member_match = re.search(r'(\d+)\s*members?', text_content, re.IGNORECASE)
        if member_match:
            member_count = int(member_match.group(1))
        
        return {
            'name': group_name,
            'description': description,
            'image_url': image_url,
            'member_count': member_count
        }
        
    except Exception as e:
        logger.error(f"Error getting group info from {invite_link}: {str(e)}")
        return None

def verify_invite_link(invite_link):
    """
    Verify if a WhatsApp invite link is valid and active
    Returns True if valid, False otherwise
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.head(invite_link, headers=headers, timeout=10, allow_redirects=True)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error verifying invite link {invite_link}: {str(e)}")
        return False
