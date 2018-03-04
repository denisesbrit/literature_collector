#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import bs4
import codecs
import requests

def test_response(status_code):

	if status_code != requests.codes.ok:
		print "Error ", status_code
		sys.exit(1)


def get_papers_Pubmed(query):

	base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

	query_dict = ({'db': 'pubmed', 'term': query, 'usehistory': 'y', 'retmax': '10000'})
	r = requests.get(base_url + 'esearch.fcgi', params=query_dict)
	test_response(r.status_code)	

	root = bs4.BeautifulSoup(r.content, 'lxml')
	webenv = root.find('webenv').text
	querykey = root.find('querykey').text
	num_matches = int(root.find('count').text)

	if num_matches > 10000:
		print "Warning: more than 10000 results. Obtained:", num_matches

	query_dict = ({'db': 'pubmed', 'WebEnv': webenv, 'query_key': querykey, 'retmax': '10000'})

	r = requests.get(base_url + 'esummary.fcgi', params=query_dict)
	test_response(r.status_code)

	return r.content


def extract_data_Pubmed(content, outfile):

	root = bs4.BeautifulSoup(content, 'lxml')

	for item in root.find_all('docsum'):
		published_date = item.select('item[name="PubDate"]')[0].text
		year = published_date.strip().split()[0]
		title = item.select('item[name="Title"]')[0].text
		volume = item.select('item[name="Volume"]')[0].text
		issue = item.select('item[name="Issue"]')[0].text
		pages = item.select('item[name="Pages"]')[0].text
		journal = item.select('item[name="FullJournalName"]')[0].text
		pubtype = item.select('item[name="PubType"]')

		type_ = ''

		for pub_type in pubtype:
			if pub_type.text == 'Journal Article':
				type_ = 'Journal Articles'
				break

		if type_ == '' and len(pubtype) > 0:
			type_ = pubtype[0].text			
			
		authors = item.select('item[name="Author"]')
		authors_list = []
		
		for author in authors:
			authors_list.append(author.text.strip())
	

		paper_dict = ({'Year': year, 'Title': title, 'Periodical': journal, 'Type': type_, 'Authors': authors_list, 'Database': 'PubMed'})
		if len(volume) > 0:
			paper_dict['Publication Volume'] = volume
		if len(issue) > 0:
			paper_dict['Publication Issue'] = issue
		if len(pages) > 0:
			paper_dict['Pages'] = pages

		print >> outfile, paper_dict
		del paper_dict
		




def print_data_Pubmed(item, outfile):


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
		if key != 'Type' or (key == 'Type' and len(item['Type']) > 0):
			outfile.write('\t')
			outfile.write(key)
			outfile.write(': ')
			outfile.write(item[key])

	outfile.write('\n')




def get_data_Pubmed(query):

	outfile = codecs.open('temp_pubmed.csv', 'w', encoding='utf-8')

	content = get_papers_Pubmed(query)
	extract_data_Pubmed(content, outfile)

	
	outfile.close()




