from __future__ import unicode_literals
from builtins import open
from selenium.webdriver.common.keys import Keys

from .exceptions import RetryException
from .browser import Browser
from .utils import instagram_int
from .utils import retry
from .utils import randmized_sleep
from . import secret
import json
import time
from time import sleep
from tqdm import tqdm
import os
import glob
import urllib3
import requests
import re
import html
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Logging(object):
    PREFIX = 'instagram-crawler'

    def __init__(self):
        try:
            timestamp  = int(time.time())
            self.cleanup(timestamp)
            self.logger = open('/tmp/%s-%s.log' % (Logging.PREFIX, timestamp), 'w')
            self.log_disable = False
        except:
            self.log_disable = True

    def cleanup(self, timestamp):
        days = 86400 * 7
        days_ago_log = '/tmp/%s-%s.log' % (Logging.PREFIX, timestamp - days)
        for log in glob.glob("/tmp/instagram-crawler-*.log"):
            if log < days_ago_log:
                os.remove(log)

    def log(self, msg):
        if self.log_disable: return

        self.logger.write(msg + '\n')
        self.logger.flush()

    def __del__(self):
        if self.log_disable: return
        self.logger.close()


class InsCrawler(Logging):
    URL = 'https://www.instagram.com'
    RETRY_LIMIT = 10

    def __init__(self, has_screen=False):
        super(InsCrawler, self).__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0

    def _dismiss_login_prompt(self):
        ele_login = self.browser.find_one('.Ls00D .Szr5J')
        if ele_login:
            ele_login.click()

    def login(self):
        browser = self.browser
        url = '%s/accounts/login/' % (InsCrawler.URL)
        browser.get(url)
        u_input = browser.find_one('input[name="username"]')
        u_input.send_keys(secret.username)
        p_input = browser.find_one('input[name="password"]')
        p_input.send_keys(secret.password)

        login_btn = browser.find_one('.L3NKy')
        login_btn.click()

        @retry()
        def check_login():
            if browser.find_one('input[name="username"]'):
                raise RetryException()

        check_login()

    def get_user_profile(self, username):
        browser = self.browser
        url = '%s/%s/' % (InsCrawler.URL, username)
        browser.get(url)
        name = browser.find_one('.rhpdm')
        desc = browser.find_one('.-vDIg span')
        photo = browser.find_one('._6q-tv')
        statistics = [ele.text for ele in browser.find('.g47SY')]
        post_num, follower_num, following_num = statistics
        return {
            'name': name.text,
            'desc': desc.text if desc else None,
            'photo_url': photo.get_attribute('src'),
            'post_num': post_num,
            'follower_num': follower_num,
            'following_num': following_num
        }

    def get_user_posts(self, username, number=None, detail=False):
        user_profile = self.get_user_profile(username)
        if not number:
            number = instagram_int(user_profile['post_num'])

        self._dismiss_login_prompt()

        if detail:
            return self._get_posts_full(number)
        else:
            return self._get_posts(number)

    def get_latest_posts_by_tag(self, tag, num):
        url = '%s/explore/tags/%s/' % (InsCrawler.URL, tag)
        self.browser.get(url)
        return self._get_posts(num)

    def auto_like(self, tag='', maximum=1000):
        self.login()
        browser = self.browser
        if tag:
            url = '%s/explore/tags/%s/' % (InsCrawler.URL, tag)
        else:
            url = '%s/explore/' % (InsCrawler.URL)
        self.browser.get(url)

        ele_post = browser.find_one('.v1Nh3 a')
        ele_post.click()

        for _ in range(maximum):
            heart = browser.find_one('.coreSpriteHeartOpen')
            if heart:
                heart.click()
                randmized_sleep(2)

            left_arrow = browser.find_one('.HBoOv')
            if left_arrow:
                left_arrow.click()
                randmized_sleep(2)
            else:
                break

    def _get_posts_full(self, num):
        @retry()
        def clean_data(str1):
            result = ""
            str1 = str1.replace("\r\n","").replace("\n","")
            for e in str1:
                if (re.sub('[ -~]', '', e)) == "":
                    result += e 
            result = html.unescape(result)
            return result
        def check_next_post(cur_key):
            ele_a_datetime = browser.find_one('.eo2As .c-Yi7')
            next_key = ele_a_datetime.get_attribute('href')
            if cur_key == next_key:
                raise RetryException()

        browser = self.browser
        browser.implicitly_wait(1)
        ele_post = browser.find_one('.v1Nh3 a')
        ele_post.click()
        dict_posts = {}

        pbar = tqdm(total=num)
        pbar.set_description('fetching')
        cur_key = None

        # Fetching all posts
        for _ in range(num):
            check_next_post(cur_key)
            dict_post = {}

            # Fetching datetime and url as key
            ele_a_datetime = browser.find_one('.eo2As .c-Yi7')
            cur_key = ele_a_datetime.get_attribute('href')
            #dict_post['key'] = cur_key

            ele_datetime = browser.find_one('._1o9PC', ele_a_datetime)
            datetime = ele_datetime.get_attribute('datetime')
            dict_post['datetime'] = datetime[0:10]

            # Fetching all img
            content = None
            img_urls = set()
            while True:
                ele_imgs = browser.find('._97aPb img', waittime=10)
                for ele_img in ele_imgs:
                    #if content is None:
                    #    content = ele_img.get_attribute('alt')
                    img_urls.add(ele_img.get_attribute('src'))
                break
                #next_photo_btn = browser.find_one('._6CZji .coreSpriteRightChevron')
                
                #if next_photo_btn:
                #    next_photo_btn.click()
                #    sleep(1)
                #else:
                #    break

            #dict_post['content'] = content
            #dict_post['img_urls'] = list(img_urls)

            # Fetching title
            ele_comment = browser.find('.eo2As .gElp9')[0]
            title = browser.find_one('span', ele_comment).text
            title = clean_data(title)
            dict_post['title'] = title
            dict_post['post_url'] = cur_key
            dict_post['img_urls'] = list(img_urls)

            self.log(json.dumps(dict_post, ensure_ascii=False))
            dict_posts[browser.current_url] = dict_post

            pbar.update(1)
            left_arrow = browser.find_one('.HBoOv')
            if left_arrow:
                left_arrow.click()

        pbar.close()
        posts = list(dict_posts.values())
        posts.sort(key=lambda post: post['datetime'], reverse=True)
        return posts[:num]

    def _get_posts(self, num):
        '''
            To get posts, we have to click on the load more
            button and make the browser call post api.
        '''
        TIMEOUT = 6000
        browser = self.browser
        key_set = set()
        posts = []
        pre_post_num = 0
        wait_time = 1

        pbar = tqdm(total=num)

        def clean_data(str1):
            result = ""
            for e in str1:
                if (re.sub('[ -~]', '', e)) == "":
                    result += e 
            return result
        def request_data( url):
            date = ""
            caption = ""
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            #print(response.text)
            json_text = soup.select('script[type="application/ld+json"]')
            try:
                if json_text and len(json_text) > 0:
                    json_data = json_text[0].get_text()
                    json_list = json.loads(json_data)
                    date = json_list["uploadDate"][0:10]
                    caption = clean_data(json_list["caption"])
                    caption = html.unescape(caption)
            except:
                pass
            try:
                if date == "":
                    datetime = soup.find('time')
                    if datetime:
                        date = datetime.attrs["datetime"][0:10]
            except:
                pass
            try:
                if caption == "":
                    title = soup.find('span[title="Edited"]')
                    if title:
                        caption = title.get_text().replace("\r\n","").replace("\n","")
                        caption = clean_data(caption)
                        caption = html.unescape(caption)
            except:
                pass
            return date, caption
        def start_fetching(pre_post_num, wait_time):
            ele_posts = browser.find('.v1Nh3 a')
            for ele in ele_posts:
                key = ele.get_attribute('href')
                if key not in key_set:
                    ele_img = browser.find_one('.KL4Bh img', ele)
                    content = ele_img.get_attribute('alt')
                    img_url = ele_img.get_attribute('src')
                    key_set.add(key)
                    #try:
                    #    date, content = request_data(key)
                    #except:
                    #    pass
                    posts.append({
                        #'date': date,
                        #'content': content,
                        'post_url': key,
                        'img_url': img_url
                    })
                break
            if pre_post_num == len(posts):
                pbar.set_description('Wait for %s sec' % (wait_time))
                sleep(wait_time)
                pbar.set_description('fetching')

                wait_time += 2
                browser.scroll_up(300)
            else:
                wait_time = 1

            pre_post_num = len(posts)
            browser.scroll_down()

            return pre_post_num, wait_time

        pbar.set_description('fetching')
        while len(posts) < num:
            # and wait_time < TIMEOUT:
            post_num, wait_time = start_fetching(pre_post_num, wait_time)
            pbar.update(post_num - pre_post_num)
            pre_post_num = post_num

            loading = browser.find_one('.W1Bne')
            if (not loading and wait_time > TIMEOUT/2):
                break

        pbar.close()
        print('Done. Fetched %s posts.' % (min(len(posts), num)))
        return posts[:num]
