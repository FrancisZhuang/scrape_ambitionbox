"""retrieve data"""
import re


def retrieve_post_date(data):
    """Match data behind posted on text"""
    if isinstance(data, str):
        post_date = re.search(r'(?<=posted\ on\ ).*', data)
        return post_date.group(0)
    return None


def retrieve_job_title(data):
    """Match data before For or In text"""
    if isinstance(data, str):
        title = re.search(r'.*(?= For)', data)
        if not title:
            title = re.search(r'.*(?= In)', data)
        return title.group(0)
    return None


def retrieve_location(data):
    """Match data behind In text"""
    if isinstance(data, str):
        location = re.search(r'(?<=In ).*', data)
        return location.group(0)
    return None


def detect_job_status(data):
    expect_statuses = ['Current Employee', 'Former Employee']
    for status in expect_statuses:
        if status in data:
            return status
    return 'Anonymous'


def retrieve_company(data):
    """Match last text behind ·"""
    if isinstance(data, str):
        company = re.search(r'(?!.*·)\w+', data)
        return company.group(0)
    return None


def generate_url_review(review_id):
    id = re.search(r'(?<=review-).*', review_id).group(0)
    return 'https://www.ambitionbox.com/reviews/amazon-reviews?rid=' + id
