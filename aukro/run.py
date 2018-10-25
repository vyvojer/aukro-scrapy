import sys

from scrapy import cmdline

cmdline.execute(["scrapy"] + sys.argv[1:])