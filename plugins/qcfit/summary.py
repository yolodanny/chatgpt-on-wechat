import openai
import requests
from bs4 import BeautifulSoup
from config import conf
import asyncio 
from pyppeteer import launch

class QcSummary:
    def __init__(self):
        openai.api_key  = conf().get("open_ai_api_key")
        pass

    async def summary_url_with_browser(self, url: str):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(url)
        await page.waitForSelector('h1')
        content = await page.content()
        await browser.close()
        return content
    
    def run_summary_url_with_browser(self, url):
        content = asyncio.get_event_loop().run_until_complete(self.summary_url_with_browser(url))
        soup = BeautifulSoup(content, 'html.parser')

        webpage_text = soup.get_text().replace(" ", "").replace("\t", "").replace("\n", "")
        print(webpage_text)
        return webpage_text

    def summary_url(self, url: str):
        if self.check_browser_url(url):
            webpage_text = self.run_summary_url_with_browser(url)
        else:
            webpage_text = self.get_webpage_text(url)

        max_chunk_length = 2048  # 根据ChatGPT模型的最大长度来设置
        text_chunks = self.split_text_into_chunks(webpage_text, max_chunk_length)
        simplify_chunks = []

        if len(text_chunks) == 1:
            print("====== 开始总结 ======")
            final_summary = self.summary_content(text_chunks[0].replace("\n", ""))
        else:
            for chunk in text_chunks:
                print("start simplify 1 chunk")
                simplify_chunks.append(self.simplify_content(chunk.replace("\n", "")))
        
            print("====== 开始总结 ======")
            final_summary = self.summary_content(" ".join(simplify_chunks))

        print("总结完成")
        print(final_summary)
        return final_summary   

    def get_completion(self, prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.6, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]

    def simplify_content(self, text):
        prompt = f"""
        保持内容含义以及书写风格不变的情况下，用不超过400个字简写```之间的内容
        ```{text}```
        """

        return self.get_completion(prompt)

    def summary_content(self, text):
        prompt = f"""
        请对```中的内容S，完成以下操作。
        第一步，从S的内容中提取最多5条关键内容，每个为一句话，存储为Y1,Y2...Yn
        第二步，根据第一步总结出来的关键内容，提炼出一个标题，存储为X
        第三步，从S的内容中提取做多3个标签，存储为T1,T2..Tn

        输出内容，输出格式为
        📖 一句话总结: X
        
        🔑 关键要点： 
            1.Y1
            ...
            n.Yn

        🏷 标签： #T1...#Tn
        ```{text}```
        """

        return self.get_completion(prompt)

    def split_text_into_chunks(self, text, max_chunk_length):
        chunks = []
        start = 0

        while start < len(text):
            end = start + max_chunk_length
            chunks.append(text[start:end])
            start = end

        return chunks

    def get_webpage_text(self, url: str):
      try:
          response = requests.get(url)
          response.raise_for_status()  # 检查是否发生错误

          soup = BeautifulSoup(response.content, 'html.parser')

          webpage_text = soup.get_text().replace(" ", "").replace("\t", "").replace("\n", "")
          return webpage_text
      except Exception as e:
          print(f"Error occurred while fetching the webpage: {e}")
          return None
      
    def check_browser_url(self, url: str):
        support_list = ["https://www.toutiao.com/"]

        for support_url in support_list:
            if url.strip().startswith(support_url):
                return True
        return False
