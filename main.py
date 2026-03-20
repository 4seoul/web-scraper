import sys
from crawl import crawl_site_async
from json_report import write_json_report
import asyncio

async def main():
	if len(sys.argv) < 4:
		print("not enough inputs")
		sys.exit(1)
	elif len(sys.argv) > 4:
		print("too many arguments provided")
		sys.exit(1)
	
	if not sys.argv[2].isdigit():
		print("max_concurrency input must be intiger")
		sys.exit(1)
	
	if not sys.argv[3].isdigit():
		print("max_pages input must be intiger")
		sys.exit(1)
	
	website = sys.argv[1]
	max_concurrency = int(sys.argv[2])
	max_pages = int(sys.argv[3])
	
	print(f"starting crawl of: {sys.argv[1]}")
	
	
	data = await crawl_site_async(website, max_concurrency, max_pages)
		
	write_json_report(data)
	
	print("data saved to report.json")
		
	sys.exit(0)


if __name__ == "__main__":
	asyncio.run(main())
