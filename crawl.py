from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup



def normalize_url(input_url):
	parsed = urlparse(input_url)
	url = parsed.netloc + parsed.path # get the www.___ part of url and add to the path (/page/page2/)
	url = url.rstrip("/") # remove / at end of url
	return url.lower()

def get_heading_from_html(html):
	soup = BeautifulSoup(html, 'html.parser')
	head = soup.find('h1') or soup.find('h2') # search for <h1> and <h2> tags
	if head:
		return head.get_text(strip=True)
	else:
		return ""
		

def get_first_paragraph_from_html(html):
	soup = BeautifulSoup(html, 'html.parser')
	main = soup.find('main') # search for <main> tags
	if main:
		pg = main.find('p') # search for <p> within <main> tag
	else:
		pg = soup.find('p')
	
	return pg.get_text(strip=True) if pg else ""

def get_urls_from_html(html, base_url):
	links = []
	soup = BeautifulSoup(html, 'html.parser')
	
	for a in soup.find_all('a', href=True):
		url = urljoin(base_url, a['href'])
		links.append(url)
		
	return links

def get_images_from_html(html, base_url):
	links = []
	soup = BeautifulSoup(html, 'html.parser')
	
	for a in soup.find_all('img', src=True):
		url = urljoin(base_url, a['src'])
		links.append(url)
		
	return links
		

def extract_page_data(html, page_url):
	my_dict = {}
	my_dict["url"] = page_url
	my_dict["heading"] = get_heading_from_html(html)
	my_dict["first_paragraph"] = get_first_paragraph_from_html(html)
	my_dict["outgoing_links"] = get_urls_from_html(html, page_url)
	my_dict["image_urls"] = get_images_from_html(html, page_url)
	
	return my_dict
	






















	