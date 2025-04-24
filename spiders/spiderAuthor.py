import pandas as pd
from DrissionPage import ChromiumPage
from time import sleep
import random
from typing import List, Dict

class XiaohongshuAuthorScraper:
    def __init__(self, headless: bool = False):
        self.page = ChromiumPage()
        self.results = []

    def login(self):
        """如果需要登录，这里实现登录逻辑"""
        self.page.get("https://www.xiaohongshu.com")
        sleep(10) #充足时间等待扫码登陆

    def read_author_urls(self, csv_path: str) -> List[str]:
        """读取 CSV 文件中的 author_url 列"""
        df = pd.read_csv(csv_path)
        urls = df['author_url'].dropna().tolist()
        return urls

    def scrape_single_author(self, url: str) -> Dict:
        """打开作者主页并提取相关数据"""
        self.page.get(url)
        self.page.wait.load_start()
        self._random_sleep(0.5, 1)

        def safe_get_text(selector, index=None):
            try:
                if index is not None:
                    return self.page.ele(selector).ele('.count', index=index).text.strip()
                return self.page.ele(selector).text.strip()
            except Exception:
                return ""

        nickname = safe_get_text('.user-name')
        user_id = safe_get_text('.user-redId')
        ip_location = safe_get_text('.user-IP')
        description = safe_get_text('.user-desc')
        tags = safe_get_text('.user-tags')
        follows = safe_get_text('.user-interactions', index=1)
        fans = safe_get_text('.user-interactions', index=2)
        likes = safe_get_text('.user-interactions', index=3)

        return {
            'author_url': url,
            'nickname': nickname,
            'user_id': user_id,
            'ip_location': ip_location,
            'description': description,
            'tags': tags,
            'follows': follows,
            'fans': fans,
            'likes': likes,
        }


    def scrape_all_authors(self, urls: List[str], output_path: str = 'scraped_authors.csv') -> None:
        """批量处理所有作者主页并写入新文件"""
        for idx, url in enumerate(urls):
            print(f"正在处理 {idx + 1}/{len(urls)}: {url}")
            try:
                info = self.scrape_single_author(url)
                self.results.append(info)
            except Exception as e:
                print(f"[错误] {url} 获取失败: {str(e)}")
                self.results.append({'author_url': url, 'error': str(e)})
        return self.results

    def close(self):
        """关闭浏览器"""
        self.page.close()

    def _random_sleep(self, min_sec: float, max_sec: float) -> None:
        sleep(random.uniform(min_sec, max_sec))

if __name__ == '__main__':
    urls = ['https://www.xiaohongshu.com/user/profile/642571c1000000001a021e93?xsec_token=ABtrYNr_YmMX5XI4NfY3vnAfz6hKEMf082OXP9-mrzK2A=&xsec_source=pc_search']
    scraper = XiaohongshuAuthorScraper()
    # scraper.login()
    results = scraper.scrape_all_authors(urls)
    print(results)
    scraper.close()