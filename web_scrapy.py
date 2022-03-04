import time
import json

from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

from db import Storage
from utils.validator import retrieve_post_date, retrieve_job_title, retrieve_location, detect_job_status, \
    retrieve_company, generate_url_review

BASE_URL = 'https://www.ambitionbox.com/reviews/amazon-reviews?sort_by=latest'
CONFIG = 'env.json'
EXPECT_MONTH = 2


class ScrapeWeb:
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    @staticmethod
    def load_config():
        with open(CONFIG, encoding='utf8') as json_file:
            config = json.load(json_file)

        return config

    def login(self):
        driver = self.driver
        config = self.load_config()

        url = config['ambition_login']
        driver.get(url)

        gmail_mail = driver.find_element(by=By.XPATH, value='//input[@id="identifierId"]')

        gmail_mail.send_keys(config['gmail']['email'])
        gmail_mail.send_keys(Keys.RETURN)

        gmail_pw = driver.find_element(by=By.CSS_SELECTOR, value='#password input')
        gmail_pw.send_keys(config['gmail']['password'])

        gmail_pw.send_keys(Keys.RETURN)

        time.sleep(5)

        driver.get(self.url)
        time.sleep(5)
        driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))
        continue_as = driver.find_element(by=By.CSS_SELECTOR, value='#continue-as .LgbsSe-bN97Pc')
        continue_as.click()
        time.sleep(5)

    def scrape(self):
        self.login()
        driver = self.driver
        PAGE = 1

        keep_exploring = False

        storge = Storage()

        while True:
            if keep_exploring:
                break
            next_page = f'https://www.ambitionbox.com/reviews/amazon-reviews?page={PAGE}&sort_by=latest'
            driver.get(next_page)
            time.sleep(10)
            comments = driver.find_elements(by=By.CSS_SELECTOR, value='#all-reviews-card div[itemprop="review"]')
            for comment in comments:
                post_date_raw = comment.find_element(by=By.CSS_SELECTOR, value='.status.caption-subdued').text
                post_date = retrieve_post_date(post_date_raw)
                date = datetime.strptime(post_date, '%d %b %Y')
                if date.month == EXPECT_MONTH - 1:
                    keep_exploring = True
                    break
                if date.month != EXPECT_MONTH:
                    continue
                else:
                    post_date = str(date.strftime('%d %m %Y'))
                review_id = comment.get_property('id')
                if storge.has_review_id(review_id):
                    continue

                comment_title = comment.find_element(by=By.CSS_SELECTOR, value='.bold-title-s.review-title').text
                job_title = retrieve_job_title(comment_title)
                location = retrieve_location(comment_title)
                description = comment.find_element(by=By.CSS_SELECTOR, value='.sbold-list-header').text
                description.replace("	", "")
                job_status = detect_job_status(description)
                company_name = retrieve_company(description)
                url_review = generate_url_review(review_id)

                try:
                    pros = comment.find_element(
                        by=By.XPATH,
                        value=f'//*[@id="{review_id}"]//h3[contains(text(), "Likes")]/following-sibling::p').text
                except:
                    pros = 'none'
                try:
                    cons = comment.find_element(
                        by=By.XPATH,
                        value=f'//*[@id="{review_id}"]//h3[contains(text(), "Dislikes")]/following-sibling::p').text
                except:
                    cons = 'none'
                storge.add_comment_data(review_id, company_name, post_date, job_title, location, pros, cons,
                                        url_review, job_status)
                print(post_date, job_title, location, job_status, company_name, review_id, url_review)
            PAGE += 1


if __name__ == '__main__':
    options = Options()
    options.add_argument(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/98.0.4758.109 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    chrome_driver = uc.Chrome(service=service, options=options, version_main=98)
    chrome_driver.implicitly_wait(15)

    web_scrape = ScrapeWeb(chrome_driver, BASE_URL)
    print(web_scrape.scrape())

    chrome_driver.close()
