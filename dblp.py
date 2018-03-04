#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs
import numpy as np
import requests
import re
import bs4

def get_page_DBLP(query):

	query_param = ({"q": query})

	r = requests.get("http://dblp.uni-trier.de/search/", params=query_param)

	if r.status_code != requests.codes.ok:
		print "Error ", r.status_code
		sys.exit(1)

	return r.content


def get_papers_DBLP(query, num_request):

	query_param = ({"q": query, "h": 30, "f": num_request, "s": "yvpc"})

	r = requests.get("http://dblp.uni-trier.de/search/publ/inc", params=query_param)

	if r.status_code != requests.codes.ok:
		print "Error ", r.status_code
		sys.exit(1)

	return r.content


def extract_data_DBLP(paper_tag, outfile):

	divs = paper_tag.find_all('div')
	fields = ({'Database': 'DBLP'})
	
	for div in divs:

		if div['class'][0] == 'data':
			authors = div.find_all("span", itemprop="author")
			pagination = div.find_all("span", itemprop="pagination")
			date = div.find_all("span", itemprop="datePublished")
			ispartof = div.find_all("span", itemprop="isPartOf")
			title = div.find_all("span", {"itemprop": "name", "class": "title"})

			fields['Authors'] = []

			for author in authors:
				fields['Authors'].append(author.a.span.text)

			if len(pagination) > 0:
				fields['Pages'] = pagination[0].text
			fields['Year'] = date[0].text
			fields['Title'] = title[0].text

			for item in ispartof:
				info_type = item['itemtype'].replace('http://schema.org/', '').replace('http://schema.org/', '')
				info_type = info_type.replace('Publication', 'Publication ').replace('Book', 'Book ')
				fields[info_type] = item.span.text

		elif div['class'][0] == 'box':
			fields['Type'] = div.img.attrs['title']
			
	print >> outfile, fields
	del fields



def print_data_DBLP(item, outfile):

	outfile.write('Title: ')
	outfile.write(item['Title'])
	del item['Title']

	if len(item['Authors']) > 0:
		outfile.write('\tAuthors: ')
		outfile.write(item['Authors'][0])

		for author in item['Authors'][1:]:
			outfile.write(', ')
			outfile.write(author)

	del item['Authors']

	for key in sorted(item.keys()):
		outfile.write('\t')
		outfile.write(key)
		outfile.write(': ')
		outfile.write(item[key])

	outfile.write('\n')
			



def get_data_DBLP(query):

	outfile = codecs.open('temp_dblp.csv', 'w', encoding='utf-8')
	content = get_page_DBLP(query)
	soup = bs4.BeautifulSoup(content)
	matches = soup.find(id="completesearch-info-matches")
	
	if matches is None:
		num_matches = 0
	else:
		num_matches = matches.text.strip().split()[1]
		if num_matches == 'one':
			num_matches = 1
		else:
			num_matches = int(num_matches.replace(',', ''))

	if num_matches > 10000:
		print "Warning: more than 10000 results. Obtained:", num_matches	

	if num_matches > 0:

		max_request = int(np.ceil(num_matches / float(30)))
		counter = 0

		for i in range(max_request + 1):
		
			if i > 0:
				content = get_papers_DBLP(query, i * 30)
				soup = bs4.BeautifulSoup(content)
		
			papers = soup.find_all('li')

			for item in papers:
				if 'class' in item.attrs and item['class'][0] == 'entry':
					counter += 1
					extract_data_DBLP(item, outfile)

					if counter == 10000:
						break
			
			if counter >= 10000:
				break


	outfile.close()



