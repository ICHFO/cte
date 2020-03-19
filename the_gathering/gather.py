#!/usr/bin/python3
import scrapers
import yaml

config = None

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.Loader)

site = 'vdab'
s = scrapers.Scraper(site)
l = s.scrape_pages(init=True)

s.driver.close()

exit(0)
