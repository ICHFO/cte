#!/usr/bin/python3
import scrapers, sys, getopt

site = ''

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

s = scrapers.Scraper(site)
s.scrape_pages()

sys.exit()
