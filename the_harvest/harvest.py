#!/usr/bin/python3
import sys, getopt
from harvesters import Harvester

sites = [ 'amon','careerjet','indeed','jobat','vdab']

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
		Harvester(s).scrape_pages()
else:
	Harvester(site).scrape_pages()


sys.exit()
