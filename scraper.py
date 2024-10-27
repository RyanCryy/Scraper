import requests
from bs4 import BeautifulSoup
import re
import random
import time
import asyncio

HEADERS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    # Add more user agents if necessary
]

def get_random_header():
    """Randomly selects a User-Agent for each request."""
    return {"User-Agent": random.choice(HEADERS)}

def get_search_results(query, location, num_pages=5):
    """Perform a Google search and retrieve the search results URLs across multiple pages."""
    search_query = f"{query} {location} email contact"
    result_links = []

    for page in range(num_pages):
        start = page * 10  # Google returns 10 results per page
        url = f"https://www.google.com/search?q={search_query}&start={start}"

        try:
            response = requests.get(url, headers=get_random_header())
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching search results: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        
        for g in soup.select(".tF2Cxc"):
            link_tag = g.select_one(".yuRUbf a")
            if link_tag:
                result_links.append(link_tag.get("href"))

        # Add a delay between page requests to avoid being blocked
        time.sleep(random.uniform(1, 3))

    return result_links

def extract_emails_from_url(url):
    """Extract emails from a given URL content."""
    emails = set()  # Use a set to avoid duplicate emails
    try:
        response = requests.get(url, headers=get_random_header(), timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        print(f"Failed to fetch {url}")
        return emails

    # Extract emails from the response text using a regex pattern
    emails.update(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text))
    
    return emails

async def process_single_query(query, location):
    """Process a single query and location, returning all found emails and their URLs."""
    result_data = []  # List to hold results as dicts
    result_urls = get_search_results(query, location)
    
    for url in result_urls:
        time.sleep(random.uniform(1, 3))
        emails_found = extract_emails_from_url(url)
        result_data.append({"url": url, "emails": list(emails_found)})

    return result_data

async def process_queries(queries, locations):
    """Process multiple queries and locations asynchronously and gather emails."""
    results = []
    for query in queries:
        for location in locations:
            query_results = await process_single_query(query, location)
            results.extend(query_results)
            print(f"Completed scraping for query '{query}' in location '{location}'")
    return results
