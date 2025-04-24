from spiders.spiderCard import XiaohongshuSearchScraper
from spiders.spiderAuthor import XiaohongshuAuthorScraper
from dataIO.data2csv import process_and_save_data, save_author_detail_to_csv



# keyword = "印尼旅游"
# sort_by = "最多评论"
# search_scraper = XiaohongshuSearchScraper()

# search_scraper.search_notes(keyword, note_type="image", sort_by=sort_by)
# notes_data = search_scraper.scrape_notes(scroll_times=10)
# search_scraper.close()
# process_and_save_data(notes_data, keyword, sort_by)
# print("笔记文件保存成功")



author_scraper = XiaohongshuAuthorScraper()
author_urls = author_scraper.read_author_urls("/Users/azhan/Desktop/bigdata-project/data/authorsUrls.csv")
author_detail_data = author_scraper.scrape_all_authors(author_urls)
author_scraper.close()
save_author_detail_to_csv(author_detail_data)
print("作者文件保存成功")


