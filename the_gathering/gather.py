#!/usr/bin/python3
import sys, getopt
from scrapers import Scraper

sites = [ 'amon','indeed','vdab']

site = 'all'

opt_str="hs:"
try:
	opts, args = getopt.getopt(sys.argv[1:],opt_str,["site="])
except getopt.GetoptError:
	print('gather -s site')
	sys.exit(2)

for opt, arg in opts:
	if opt == '-h':
		print('gather -s site')
		sys.exit()
	elif opt in ('-s','--site'):
		site = arg

if site == 'all':
	for s in sites:
		Scraper(s).scrape_pages()
else:
	Scraper(site).scapre_pages()


sys.exit()
