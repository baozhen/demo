# Scrapy settings for yirendai project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'yirendai'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['yirendai.spiders']
NEWSPIDER_MODULE = 'yirendai.spiders'
DEFAULT_ITEM_CLASS = 'yirendai.items.YirendaiItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

