
import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import os
import sqlite3
import re

def download_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    response.raise_for_status()
    return response.text

 # This function parses the sitemap XML and extracts all URLs listed in it.
def parse_sitemap(sitemap_xml):
    root = ET.fromstring(sitemap_xml) # Parse the XML string into an ElementTree object
   
    namespace = {'ns': 'https://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [] 
    for url in root.findall('ns:url', namespace): 
        loc = url.find('ns:loc', namespace) 
        if loc is not None:  
            urls.append(loc.text) 
    return urls

def download_page(url): 
    try:
        response = requests.get(url)
        response.raise_for_status() 
        return response.text
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None

def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract course_id and course_code from URL or page meta if possible
    # Here we try to extract from meta tags or URL pattern if available
    course_code = None 
    course_id = None

    # Title
    title_tag = soup.find('title') 
    title = title_tag.string.strip() if title_tag else 'No title'

    # Description from meta description or page content
    description = ''
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        description = meta_desc['content'].strip()
    else:
        # Fallback: try to get first paragraph in main content
        p = soup.find('p')
        if p:
            description = p.get_text(strip=True)

    # Extract program info from meta tags with name starting with 's_program'
    program_info = {}
    for meta in soup.find_all('meta'):
        name = meta.get('name', '')
        if name.startswith('s_program'):
            program_info[name] = meta.get('content', '').strip()

    # Extract fields from program_info
    course_code = program_info.get('s_programcode', '')
    school = program_info.get('s_programschool', '')
    career = program_info.get('s_programinterestarea', '')
    course_type = program_info.get('s_programtype', '')
    # semester and credits are not directly available in meta, will try to parse from page content

    # Extract semester info from page content (e.g., "Next intake" or "Semester")
    semester = ''
    credits = ''
    campus = ''
    # Try to find "Next intake" or "Semester" info in page
    # For example, look for elements with class containing 'intake' or 'semester'
    intake_elem = soup.find(class_=re.compile('intake', re.I))
    if intake_elem:
        semester = intake_elem.get_text(separator=', ', strip=True)

    # Try to find credits info - not found in sample, so leave empty or default
    # Try to find campus info - e.g., from location or study mode
    location_elem = soup.find(class_=re.compile('location', re.I))
    if location_elem:
        campus = location_elem.get_text(strip=True)

    # Topics and prerequisites are not clearly available in sample HTML, so leave empty lists
    topics = []
    prerequisites = []

    # Compose structured data
    data = {
        "course_id": course_id if course_id else "",
        "course_code": course_code,
        "title": title,
        "semester": semester,
        "credits": credits,
        "campus": campus,
        "school": school,
        "career": career,
        "description": description,
        "topics": topics,
        "prerequisites": prerequisites,
        "course_type": course_type
    }

    return data

def save_data_to_db(db_path, data_list):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT,
            course_code TEXT UNIQUE,
            title TEXT,
            semester TEXT,
            credits TEXT,
            campus TEXT,
            school TEXT,
            career TEXT,
            description TEXT,
            topics TEXT,
            prerequisites TEXT,
            course_type TEXT
        )
    ''')
    for data in data_list:
        try:
            c.execute('''
                INSERT OR REPLACE INTO extracted_data (
                    course_id, course_code, title, semester, credits, campus, school, career, description, topics, prerequisites, course_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('course_id', ''),
                data.get('course_code', ''),
                data.get('title', ''),
                data.get('semester', ''),
                data.get('credits', ''),
                data.get('campus', ''),
                data.get('school', ''),
                data.get('career', ''),
                data.get('description', ''),
                json.dumps(data.get('topics', [])),
                json.dumps(data.get('prerequisites', [])),
                data.get('course_type', '')
            ))
        except sqlite3.Error as e:
            print(f"Failed to insert data for course_code {data.get('course_code', '')}: {e}")
    conn.commit()
    conn.close()

def run_extraction_with_filters(filter_keywords):
    sitemap_url = "https://www.rmit.edu.au/sitemap.xml"
    print(f"Downloading sitemap from {sitemap_url}...")
    sitemap_xml = download_sitemap(sitemap_url)
    print("Parsing sitemap...")
    urls = parse_sitemap(sitemap_xml)
    print(f"Found {len(urls)} URLs in sitemap.")

    # Filter URLs based on user-selected keywords
    filtered_urls = [url for url in urls if any(keyword in url for keyword in filter_keywords)]

    data_list = []

    for i, url in enumerate(filtered_urls, start=1):
        print(f"Processing ({i}/{len(filtered_urls)}): {url}")
        page_html = download_page(url)
        if page_html:
            data = parse_page(page_html)
            data_list.append(data)

    output_db = "extracted_data.db"
    save_data_to_db(output_db, data_list)
    print(f"Extraction complete. Data saved in database file '{output_db}'.")

def main():
    # Default main function calls extraction with default filters
    default_filters = [
        "apprenticeship",
        "traineeship",
        "certificate",
        "associate-degree",
        "bachelor-degree",
        "postgraduate-degree",
        "levels-of-study"
    ]
    run_extraction_with_filters(default_filters)

if __name__ == "__main__":
    main()
