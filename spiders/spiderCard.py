from DrissionPage import ChromiumPage
from time import sleep
import random
from typing import List, Dict, Optional

class XiaohongshuScraper:
    def __init__(self, headless: bool = False):
        """初始化小红书爬虫
        
        Args:
            headless: 是否无头模式
        """
        self.page = ChromiumPage()
        
    def search_notes(self, keyword: str, note_type: str = "image", sort_by: str = "hot") -> None:
        """搜索小红书笔记，可以选择笔记类型和排序方式
        
        Args:
            keyword: 搜索关键词
            note_type: 笔记类型，image(图文)或video(视频)
            sort_by: 排序方式，hot(最热)或time(最新)
        """
        # 打开搜索页面
        self.page.get(f'https://www.xiaohongshu.com/search_result?keyword={keyword}')
        self._random_sleep(1, 2)
        
        # 选择笔记类型
        if note_type == "image":
            self.page.ele('xpath://*[@id="image"]').click()
        elif note_type == "video":
            self.page.ele('xpath://*[@id="video"]').click()
            
        # 设置排序方式
        self._set_sort_method(sort_by)
        
    def _set_sort_method(self, sort_by: str) -> None:
        """设置排序方式"""
        self.page.ele('xpath:.//*[@class="filter-box"]', timeout=2).click()
        self._random_sleep(2, 3)
        
        if sort_by == "hot":
            self.page.ele('text:最热').click()
        elif sort_by == "time":
            self.page.ele('text:最新').click()
        self._random_sleep(2, 3)
        
    def scrape_notes(self, max_notes: int = 3, scroll_times: int = 1) -> List[Dict]:
        """爬取笔记数据
        
        Args:
            max_notes: 最大爬取笔记数量
            scroll_times: 滚动加载次数
            
        Returns:
            笔记数据列表
        """
        notes_data = []
        
        for _ in range(scroll_times):
            cards = self.page.eles('xpath://section[contains(@class, "note-item")]')
            print(f'共找到{len(cards)}个卡片')
            
            for card in cards[:max_notes]:
                try:
                    note_data = self._process_note_card(card)
                    notes_data.append(note_data)
                except Exception as e:
                    print(f'处理卡片时出错：{str(e)[:200]}')
                    continue
                    
            self.page.scroll.to_bottom()
            self._random_sleep(2, 3)
            
        return notes_data
    
    def _process_note_card(self, card) -> Dict:
        """处理单个笔记卡片"""
        # 点击卡片
        title_url = card.ele(".footer").ele('.title', timeout=2)
        title_url.click()
        self.page.wait.load_start()
        self._random_sleep(1, 2)
        
        # 提取笔记数据
        note_data = {
            "author": self._get_author_info(),
            "title": self._get_note_title(),
            "content": self._get_note_content(),
            "date": self._get_note_date(),
            "interactions": self._get_interaction_data(),
            "images": self._get_note_images(),
            "comments": self._get_note_comments()
        }
        
        # 返回搜索结果页
        self.page.back()
        self._random_sleep(1, 2)
        
        return note_data
    
    def _get_author_info(self) -> Dict:
        """获取作者信息"""
        author_info = self.page.ele('.author-container', timeout=2).ele('.info')
        return {
            "name": author_info.ele('xpath:.//*[contains(@class, "name")]').text,
            "url": author_info.eles('tag:a')[0].link
        }
    
    def _get_note_title(self) -> str:
        """获取笔记标题"""
        return self.page.ele('#detail-title', timeout=2).text
    
    def _get_note_content(self) -> str:
        """获取笔记内容"""
        return self.page.ele('#detail-desc', timeout=2).text
    
    def _get_note_date(self) -> str:
        """获取笔记日期"""
        return self.page.ele('.bottom-container').text
    
    def _get_interaction_data(self) -> Dict:
        """获取互动数据(点赞、评论、分享)"""
        interact_btn = self.page.ele('.buttons engage-bar-style', timeout=2)
        return {
            "likes": interact_btn.ele('xpath:.//*[contains(@class, "like-wrapper like-active")]', timeout=2).text,
            "comments": interact_btn.ele('xpath:.//*[contains(@class, "chat-wrapper")]', timeout=2).text,
            "shares": interact_btn.ele('xpath:.//*[contains(@class, "collect-wrapper")]', timeout=2).text
        }
    
    def _get_note_images(self) -> List[str]:
        """获取笔记图片"""
        return [img.attr('src') for img in self.page.eles('xpath://.//img[contains(@class, "note-slider-img")]')]
    
    def _get_note_comments(self) -> List[Dict]:
        """获取笔记评论"""
        comments = []
        for comment in self.page.eles('xpath://.//div[contains(@class, "parent-comment")]'):
            comments.append({
                "id": comment.ele('xpath:.//*[@class="comment-item"]').attr('id'),
                "user_name": comment.ele('xpath:.//*[@class="name"]').text,
                "user_link": comment.ele('xpath:.//*[@class="name"]').link,
                "content": comment.ele('xpath:.//*[@class="note-text"]').text,
                "time": comment.ele('xpath:.//*[@class="date"]').text,
                "likes": comment.ele('xpath:.//*[@class="like"]').text,
                "replies": comment.ele('xpath:.//*[@class="reply icon-container"]').text
            })
        return comments
    
    def _random_sleep(self, min_sec: float, max_sec: float) -> None:
        """随机睡眠"""
        sleep(random.uniform(min_sec, max_sec))
        
    def close(self):
        """关闭浏览器"""
        self.page.close()

# 使用示例
if __name__ == "__main__":
    scraper = XiaohongshuScraper()
    try:
        scraper.search_notes(keyword="英语口语", note_type="image", sort_by="hot")
        notes_data = scraper.scrape_notes(max_notes=10, scroll_times=1)
        
        # 打印结果
        for i, note in enumerate(notes_data, 1):
            print(f"\n=== 笔记 {i} ===")
            print(f"作者: {note['author']['name']} \n(作者主页: {note['author']['url']})")
            print(f"标题: {note['title']}")
            print(f"内容: {note['content'][:1000]}...")  # 只打印前1000字符
            print(f"日期: {note['date']}")
            print(f"点赞: {note['interactions']['likes']}, 评论: {note['interactions']['comments']}, 分享: {note['interactions']['shares']}")
            print(f"图片数量: {len(note['images'])}")
            print(f"评论数量: {len(note['comments'])}")
            for j, comment in enumerate(note['comments'], 1):
                print(f"  评论 {j}: {comment['user_name']} \n(评论者主页: {comment['user_link']}): {comment['content']}")
    finally:
        scraper.close()