import csv
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Union
import sys
from pathlib import Path

# 获取项目根目录的绝对路径（注意：这里是 parent.parent）
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

from spiders.spiderCard import XiaohongshuSearchScraper
from spiders.spiderAuthor import XiaohongshuAuthorScraper

# ===================== 通用工具函数 =====================
def save_to_csv(data: list, filename: str, fieldnames: list):
    file_exists = os.path.exists(filename)
    with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)


# ===================== 数据清洗辅助函数 =====================
def extract_note_id(url: str) -> str:
    match = re.search(r'/search_result/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else ''

def extract_user_id(url: str) -> str:
    match = re.search(r'/user/profile/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else ''

def parse_date(date_str: str) -> str:
    now = datetime.now()
    date_str = date_str.strip().replace('编辑于', '').strip()
    if '天前' in date_str:
        days = int(re.search(r'(\d+)', date_str).group(1))
        return (now - timedelta(days=days)).strftime('%Y-%m-%d')
    if '今天' in date_str:
        return now.strftime('%Y-%m-%d')
    if '昨天' in date_str:
        return (now - timedelta(days=1)).strftime('%Y-%m-%d')
    if '前天' in date_str:
        return (now - timedelta(days=2)).strftime('%Y-%m-%d')
    match_full = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
    if match_full:
        return match_full.group(1)
    match_md = re.search(r'(\d{1,2})-(\d{1,2})', date_str)
    if match_md:
        month, day = match_md.groups()
        return f"{now.year}-{int(month):02d}-{int(day):02d}"
    return date_str

def clean_number_str(s: Union[str, int, float]) -> str:
    if s is None:
        return '0'
    if isinstance(s, (int, float)):
        return str(s)
    return ''.join([c for c in str(s) if c.isdigit() or c in ('.', '万')])

def convert_to_int(num_str: Union[str, int, float]) -> int:
    clean_str = clean_number_str(num_str)
    try:
        if '万' in clean_str:
            num = float(clean_str.replace('万', ''))
            return int(num * 10000)
        elif '.' in clean_str:
            return int(float(clean_str))
        else:
            return int(clean_str) if clean_str else 0
    except (ValueError, AttributeError):
        return 0

def extract_pure_number(text: Union[str, int, float]) -> int:
    if text is None:
        return 0
    if isinstance(text, (int, float)):
        return int(text)
    text = str(text).replace(',', '')
    match = re.match(r'([\d\.]+)(万)?', text)
    if match:
        num, unit = match.groups()
        try:
            num = float(num)
            return int(num * 10000) if unit == '万' else int(num)
        except ValueError:
            return 0
    return 0

def clean_user_id(user_id_str: str) -> str:
    return user_id_str.replace("小红书号：", "").strip()

def clean_ip_location(ip_str: str) -> str:
    return ip_str.replace("IP属地：", "").strip()


# ===================== 数据处理函数 =====================
def process_and_save_data(notes_data, keyword,sort_by="综合"):
    authors, notes, comments = [], [], []
    for note in notes_data:
        author = {
            'author_url': note['author']['url'],
        }
        authors.append(author)

        note_data = {
            'note_id': extract_note_id(note['url']),
            'keyword': keyword,
            'sort_by': sort_by,
            'author_id': extract_user_id(note['author']['url']),
            'note_url': note['url'],
            'title': note['title'].strip(),
            'content': note['content'].replace('\n', ' ').strip(),
            'publish_date': parse_date(note['date']),
            'like_count': convert_to_int(note['interactions']['likes']),
            'comment_count': convert_to_int(note['interactions']['comments']),
            'share_count': convert_to_int(note['interactions']['shares']),
            'image_count': len(note['images']),
            'image_urls': '|'.join(note['images']),
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        notes.append(note_data)

        for comment in note['comments']:
            comment_data = {
                'comment_id': comment['comment_id'],
                'note_id': note_data['note_id'],
                'user_id': extract_user_id(comment['user_link']),
                'user_name': comment['user_name'].strip(),
                'user_url': comment['user_link'],
                'comment_content': comment['comment_content'].replace('\n', ' ').strip(),
                'comment_date': parse_date(comment['comment_date']),
                'comment_likes': convert_to_int(comment['comment_likes']),
                'comment_replies': convert_to_int(comment['comment_replies']),
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            comments.append(comment_data)

    save_to_csv(authors, 'authorsUrls.csv', fieldnames=['author_url'])
    save_to_csv(notes, 'notes.csv', fieldnames=[
        'note_id', 'keyword', 'sort_by', 'author_id', 'note_url', 'title', 'content',
        'publish_date', 'like_count', 'comment_count', 'share_count',
        'image_count', 'image_urls', 'crawl_time'
    ])
    save_to_csv(comments, 'comments.csv', fieldnames=[
        'comment_id', 'note_id', 'user_id', 'user_name', 'user_url',
        'comment_content', 'comment_date', 'comment_likes', 'comment_replies', 'crawl_time'
    ])

def save_author_detail_to_csv(author_data_list: List[Dict]):
    cleaned_data = []
    for author in author_data_list:
        cleaned = {
            "author_id": clean_user_id(author.get("user_id", "")),
            "author_url": author.get("author_url", ""),
            "author_name": author.get("nickname", ""),
            "fan_count": extract_pure_number(author.get("fans", 0)),
            "following_count": extract_pure_number(author.get("follows", 0)),
            "like_count": extract_pure_number(author.get("likes", 0)),
            "tags": author.get("tags", ""),
            "description": author.get("description", ""),
            "ip_location": clean_ip_location(author.get("ip_location", "")),
            "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        cleaned_data.append(cleaned)

    fieldnames = ["author_id", "author_url", "author_name", "fan_count", "following_count", "like_count", "tags", "description", "ip_location", "crawl_time"]
      
    save_to_csv(cleaned_data, 'authors_detail.csv', fieldnames)


# ===================== 主函数 =====================
if __name__ == "__main__":
    keyword = "印尼旅游"
    sort_by = "综合"
    search_scraper = XiaohongshuSearchScraper()
    author_scraper = XiaohongshuAuthorScraper()

    try:
        search_scraper.search_notes(keyword, note_type="image", sort_by=sort_by)
        notes_data = search_scraper.scrape_notes(scroll_times=10)
        process_and_save_data(notes_data, keyword, sort_by)

        # author_urls = list(set([note['author']['url'] for note in notes_data]))
        # author_urls = author_scraper.read_author_urls("/Users/azhan/Desktop/bigdata-project/data/authors.csv")[10:]
        # author_detail_data = author_scraper.scrape_all_authors(author_urls)
        # save_author_detail_to_csv(author_detail_data)

        # print("数据已保存到 authors.csv, notes.csv, comments.csv, authors_detail.csv")

    finally:
        search_scraper.close()
        # author_scraper.close()
