from bs4 import BeautifulSoup
from urllib.parse import urljoin
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data
import requests


def extract_page_data(html, page_url):
	my_dict = {}
	my_dict["url"] = page_url
	my_dict["heading"] = get_heading_from_html(html)
	my_dict["first_paragraph"] = get_first_paragraph_from_html(html)
	my_dict["outoing_links"] = get_urls_from_html(html, page_url)
	my_dict["image_urls"] = get_images_from_html(html, page_url)
	
	return my_dict


input_url = "https://crawler-test.com"
input_body = "<html><body><div>No h1, p, links, or images</div></body></html>"

def get_html(url):
	r = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
	print(r.text)

get_html("https://wagslane.dev")