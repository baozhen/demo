# Scrapy settings for dianrong project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'dianrong'

SPIDER_MODULES = ['dianrong.spiders']
NEWSPIDER_MODULE = 'dianrong.spiders'

DOWNLOAD_DELAY = 2 
RANDOMIZE_DOWNLOAD_DELAY = True
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'
# COOKIES_ENABLED = True
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'dianrong (+http://www.yourdomain.com)'
