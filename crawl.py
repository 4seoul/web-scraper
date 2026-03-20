from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio



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
	

def safe_get_html(url):
	try:
		return get_html(url)
	except Exception as e:
		print(f"{e}")
		return None



class AsyncCrawler:
	def __init__(self, base_url, max_concurrency, max_pages):
		self.base_url = base_url
		self.base_domain = urlparse(base_url).netloc
		self.page_data = {}
		self.lock = asyncio.Lock()
		self.max_concurrency = max_concurrency
		self.sem = asyncio.Semaphore(self.max_concurrency)
		self.session = None
		self.max_pages = max_pages
		self.should_stop = False
		self.all_tasks = set()
	
	async def __aenter__(self):
		self.session = aiohttp.ClientSession()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.session.close()
	
	async def add_page_visit(self, normalized):
		async with self.lock:
			if self.should_stop == True:
				return False
			if normalized in self.page_data:
				return False
			if len(self.page_data) >= self.max_pages:
				self.should_stop = True
				print("Reached maximum number of pages to crawl")
				for task in self.all_tasks:
					if not task.done():
						task.cancel()
				return False
			return True
			
	async def get_html(self, url):
		try:
			async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
				if response.status > 399:
					print(f"Error: HTTP {response.status} for {url}")
					return None
				
				content_type = response.headers.get("content-type", "")
				if "text/html" not in content_type:
					print(f"got non-HTML response {content_type} for {url}")
					return None
	
				return await response.text()
		except Exception as e:
			print(f"network error while fetching {url}: {e}")
			return None
			
	async def crawl_page(self, current_url):
		if self.should_stop:
			return
		
		parsed_current = urlparse(current_url)
	
		if self.base_domain != parsed_current.netloc:
			return
	
		normalized = normalize_url(current_url)
	
		check = await self.add_page_visit(normalized)
		if check == False:
			return
			
		async with self.sem:
	
			html = await self.get_html(current_url)
		
			if html is None:
				return

			rich_data = extract_page_data(html, current_url)
			async with self.lock:
				self.page_data[normalized] = rich_data
	
			urls = get_urls_from_html(html, self.base_url)

		
		tasks = []
	
		for url in urls:
			task = asyncio.create_task(self.crawl_page(url))
			self.all_tasks.add(task)
			tasks.append(task)
			
					
	
		if tasks:
			try:
				await asyncio.gather(*tasks)
			except asyncio.CancelledError:
				pass
			finally:
				for task in tasks:
					self.all_tasks.discard(task)
		
	async def crawl(self):
		await self.crawl_page(self.base_url)
		return self.page_data




async def crawl_site_async(base_url, max_concurrency, max_pages):
	async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
		return await crawler.crawl()

		














	