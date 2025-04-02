from DrissionPage import ChromiumPage
from time import sleep
import random

# 启动浏览器
page = ChromiumPage()

keyword = '口语'
# 打开网页
page.get(f'https://www.xiaohongshu.com/search_result?keyword={keyword}')
sleep(random.uniform(1, 2))
#点击“图文”，只看图文笔记
page.ele('xpath://*[@id="image"]').click()

# 点击触发下拉框
page.ele('xpath:.//*[@class="filter-box"]', timeout=2).click()
sleep(random.uniform(1, 2))

#点击最热排序
# page.ele('xpath:./html/body/div[5]/div/li[3]').click()
page.ele('text:最热').click()
sleep(random.uniform(1, 2))

for i in range(1, 2):
    # 获取所有卡片
    cards = page.eles('xpath://section[contains(@class, "note-item")]')
    print(f'共找到{len(cards)}个卡片')
    for card in cards[:3]:  
        try:       
            # --- 点击卡片 ---
            title_url = card.ele(".footer").ele('.title', timeout=2)
            title_url.click()
            
            # 等待内容加载
            page.wait.load_start()
            sleep(2)  # 适当等待
            #提取卡片信息
            #作者
            author_info = page.ele('.author-container', timeout=2).ele('.info')
            author_name = author_info.ele('xpath:.//*[contains(@class, "name")]').text
            author_url = author_info.eles('tag:a')[0].link            

            print(f'作者：{author_name}\n链接：{author_url}')
            #标题
            title = page.ele('#detail-title', timeout=2).text
            content = page.ele('#detail-desc', timeout=2).text
            date = page.ele('.bottom-container').text

          
            print(f'标题：{title}\n内容：{content}\n日期:{date}')
            #点赞、评论、分享
            interact_btn = page.ele('.buttons engage-bar-style', timeout=2)
            like = interact_btn.ele('xpath:.//*[contains(@class, "like-wrapper like-active")]', timeout=2).text
            comment = interact_btn.ele('xpath:.//*[contains(@class, "chat-wrapper")]', timeout=2).text
            share = interact_btn.ele('xpath:.//*[contains(@class, "collect-wrapper")]', timeout=2).text
            print(f'点赞：{like}\n评论：{comment}\n分享：{share}')

            for img in page.eles('xpath://.//img[contains(@class, "note-slider-img")]'):
                img_url = img.attr('src')
                print(f'图片：{img_url}')

            for comment in page.eles('xpath://.//div[contains(@class, "parent-comment")]'):
                comment_id = comment.ele('xpath:.//*[@class="comment-item"]').attr('id')
                comment_user_name = comment.ele('xpath:.//*[@class="name"]').text
                comment_user_link = comment.ele('xpath:.//*[@class="name"]').link 
                comment_content = comment.ele('xpath:.//*[@class="note-text"]').text
                comment_time = comment.ele('xpath:.//*[@class="date"]').text
                comment_like = comment.ele('xpath:.//*[@class="like"]').text
                comment_reply = comment.ele('xpath:.//*[@class="reply icon-container"]').text
           
            page.back()  # 返回上一页
            sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f'处理卡片时出错：{str(e)[:1000]}')  # 打印前100字符避免过长
            continue
    page.scroll.to_bottom()  # 向下滚动