import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional
from apps.content_creation.models import ProductAnalysis


class ProductAnalyzer:
    """Service for analyzing products from URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_product(self, workspace_id: str, product_url: str) -> ProductAnalysis:
        """Analyze product from URL and return analysis"""
        
        # Check if analysis already exists
        existing_analysis = ProductAnalysis.objects.filter(
            workspace_id=workspace_id,
            product_url=product_url
        ).first()
        
        if existing_analysis:
            return existing_analysis
        
        # Scrape product data
        product_data = self._scrape_product_data(product_url)
        
        # Create analysis
        analysis = ProductAnalysis.objects.create(
            workspace_id=workspace_id,
            product_url=product_url,
            title=product_data.get('title'),
            description=product_data.get('description'),
            price=product_data.get('price'),
            currency=product_data.get('currency', 'SAR'),
            images=product_data.get('images', []),
            features=product_data.get('features', []),
            category=product_data.get('category'),
            brand=product_data.get('brand'),
            analysis_data=product_data
        )
        
        return analysis
    
    def _scrape_product_data(self, url: str) -> Dict[str, Any]:
        """Scrape product data from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Detect platform and use appropriate scraper
            domain = urlparse(url).netloc.lower()
            
            if 'shopify' in domain or self._is_shopify_store(soup):
                return self._scrape_shopify_product(soup, url)
            elif 'salla.sa' in domain:
                return self._scrape_salla_product(soup, url)
            elif 'zid.sa' in domain:
                return self._scrape_zid_product(soup, url)
            elif 'amazon' in domain:
                return self._scrape_amazon_product(soup, url)
            elif 'noon.com' in domain:
                return self._scrape_noon_product(soup, url)
            else:
                return self._scrape_generic_product(soup, url)
                
        except Exception as e:
            return {
                'title': 'Failed to analyze product',
                'description': f'Error: {str(e)}',
                'error': str(e)
            }
    
    def _is_shopify_store(self, soup: BeautifulSoup) -> bool:
        """Check if the page is a Shopify store"""
        shopify_indicators = [
            soup.find('script', {'src': lambda x: x and 'shopify' in x}),
            soup.find('meta', {'name': 'shopify-checkout-api-token'}),
            soup.find('link', {'href': lambda x: x and 'shopify' in x})
        ]
        return any(shopify_indicators)
    
    def _scrape_shopify_product(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Scrape Shopify product data"""
        data = {}
        
        # Title
        title_selectors = [
            'h1.product-title',
            'h1[data-testid="product-title"]',
            '.product__title h1',
            'h1.h2'
        ]
        data['title'] = self._extract_text_by_selectors(soup, title_selectors)
        
        # Description
        desc_selectors = [
            '.product-description',
            '.product__description',
            '[data-testid="product-description"]',
            '.rte'
        ]
        data['description'] = self._extract_text_by_selectors(soup, desc_selectors)
        
        # Price
        price_selectors = [
            '.price',
            '.product-price',
            '[data-testid="price"]',
            '.money'
        ]
        data['price'] = self._extract_price(soup, price_selectors)
        
        # Images
        data['images'] = self._extract_product_images(soup, url)
        
        # Features
        data['features'] = self._extract_product_features(soup)
        
        return data
    
    def _scrape_salla_product(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Scrape Salla product data"""
        data = {}
        
        # Salla-specific selectors
        data['title'] = self._extract_text_by_selectors(soup, [
            'h1.product-title',
            '.product-name h1',
            'h1'
        ])
        
        data['description'] = self._extract_text_by_selectors(soup, [
            '.product-description',
            '.description',
            '.product-details'
        ])
        
        data['price'] = self._extract_price(soup, [
            '.price',
            '.product-price',
            '.price-current'
        ])
        
        data['images'] = self._extract_product_images(soup, url)
        data['features'] = self._extract_product_features(soup)
        data['currency'] = 'SAR'
        
        return data
    
    def _scrape_zid_product(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Scrape Zid product data"""
        data = {}
        
        # Zid-specific selectors
        data['title'] = self._extract_text_by_selectors(soup, [
            'h1.product-title',
            '.product-name',
            'h1'
        ])
        
        data['description'] = self._extract_text_by_selectors(soup, [
            '.product-description',
            '.description'
        ])
        
        data['price'] = self._extract_price(soup, [
            '.price',
            '.product-price'
        ])
        
        data['images'] = self._extract_product_images(soup, url)
        data['features'] = self._extract_product_features(soup)
        data['currency'] = 'SAR'
        
        return data
    
    def _scrape_amazon_product(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Scrape Amazon product data"""
        data = {}
        
        data['title'] = self._extract_text_by_selectors(soup, [
            '#productTitle',
            'h1.a-size-large'
        ])
        
        data['description'] = self._extract_text_by_selectors(soup, [
            '#feature-bullets ul',
            '#productDescription'
        ])
        
        data['price'] = self._extract_price(soup, [
            '.a-price-whole',
            '#price_inside_buybox'
        ])
        
        data['images'] = self._extract_product_images(soup, url)
        data['features'] = self._extract_amazon_features(soup)
        
        return data
    
    def _scrape_noon_product(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Scrape Noon product data"""
        data = {}
        
        data['title'] = self._extract_text_by_selectors(soup, [
            'h1[data-qa="product-name"]',
            'h1'
        ])
        
        data['description'] = self._extract_text_by_selectors(soup, [
            '[data-qa="product-description"]',
            '.description'
        ])
        
        data['price'] = self._extract_price(soup, [
            '[data-qa="product-price"]',
            '.price'
        ])
        
        data['images'] = self._extract_product_images(soup, url)
        data['features'] = self._extract_product_features(soup)
        data['currency'] = 'AED'
        
        return data
    
    def _scrape_generic_product(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Generic product scraper for unknown platforms"""
        data = {}
        
        # Generic selectors
        data['title'] = self._extract_text_by_selectors(soup, [
            'h1',
            '.product-title',
            '.title',
            '[data-testid="product-title"]'
        ])
        
        data['description'] = self._extract_text_by_selectors(soup, [
            '.description',
            '.product-description',
            '.content',
            'p'
        ])
        
        data['price'] = self._extract_price(soup, [
            '.price',
            '.cost',
            '.amount',
            '[data-testid="price"]'
        ])
        
        data['images'] = self._extract_product_images(soup, url)
        data['features'] = self._extract_product_features(soup)
        
        return data
    
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None
    
    def _extract_price(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[float]:
        """Extract price from multiple selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Extract numeric value
                import re
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        return float(price_match.group())
                    except ValueError:
                        continue
        return None
    
    def _extract_product_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract product images"""
        images = []
        
        # Common image selectors
        img_selectors = [
            '.product-image img',
            '.product-gallery img',
            '[data-testid="product-image"] img',
            '.main-image img',
            'img[alt*="product"]'
        ]
        
        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(base_url, src)
                    if full_url not in images:
                        images.append(full_url)
        
        return images[:5]  # Limit to 5 images
    
    def _extract_product_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product features"""
        features = []
        
        # Look for feature lists
        feature_selectors = [
            '.features li',
            '.specifications li',
            '.product-features li',
            '.bullets li'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements:
                feature = element.get_text(strip=True)
                if feature and len(feature) > 5:  # Filter out empty or very short features
                    features.append(feature)
        
        return features[:10]  # Limit to 10 features
    
    def _extract_amazon_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract Amazon-specific features"""
        features = []
        
        # Amazon feature bullets
        feature_bullets = soup.select('#feature-bullets li span.a-list-item')
        for bullet in feature_bullets:
            feature = bullet.get_text(strip=True)
            if feature and not feature.startswith('Make sure'):
                features.append(feature)
        
        return features