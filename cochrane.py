#!/usr/bin/python
# -*- coding: utf-8 -*-
#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
import string
import sys
import codecs


def test_response(status_code):

	if status_code != requests.codes.ok:
		print "Error ", status_code
		sys.exit(1)



def print_data_Cochrane(data, outfile):

	outfile.write('Title: ')
	outfile.write(data['Title'])

	del data['Title']

	if len(data['Authors']) > 0:
		outfile.write('\tAuthors: ')
		outfile.write(data['Authors'][0])

		for author in data['Authors'][1:]:
			outfile.write(', ')
			outfile.write(author)

	del data['Authors']

	for key in sorted(data.keys()):
		if key != 'Type' or (key == 'Type' and len(data['Type']) > 0):
			outfile.write('\t')
			outfile.write(key)
			outfile.write(': ')
			outfile.write(data[key])

	outfile.write('\n')



def extract_data_Cochrane(paper, outfile):
	
	fields = paper.split('\t')
	paper_dict = ({'Authors': [], 'Database': 'Cochrane Library'})
	for item in fields:
		if item[:3] == 'AU:':
			paper_dict['Authors'].append(item[4:].strip())#.decode('utf-8'))
		elif item[:3] == 'TI:':
			paper_dict['Title'] = item[4:].strip()#.decode('utf-8')
		elif item[:3] == 'YR:':
			paper_dict['Year'] = item[4:].strip()#.decode('utf-8')
		elif item[:3] == 'VL:':
			paper_dict['Publication Volume'] = item[4:].strip()
		elif item[:3] == 'NO:':
			paper_dict['Publication Issue'] = item[4:].strip()
		elif item[:3] == 'PG:':
			paper_dict['Pages'] = item[4:].strip()
		elif item[:3] == 'SO:':
			paper_dict['Periodical'] = item[4:].strip()#.decode('utf-8')
		elif item[:3] == 'PT:':
			if re.search('Journal:? Article', item[4:].strip(), re.IGNORECASE) is not None:
				paper_dict['Type'] = 'Journal Articles'
			elif re.search('Article', item[4:].strip(), re.IGNORECASE) is not None:
				paper_dict['Type'] = 'Article'
			elif re.search('Editorial', item[4:].strip(), re.IGNORECASE) is not None:
				paper_dict['Type'] = 'Editorial'
			elif re.search('Letter', item[4:].strip(), re.IGNORECASE) is not None:
				paper_dict['Type'] = 'Letter'
			elif ':' in item[4:].strip():
				paper_dict['Type'] = item[4:].strip().split(':')[1][1:]
			else:
				type_ = item[4:].strip().replace('.', '').replace("'", '')
				paper_dict['Type'] = re.split('[;,]', type_)[0]

			paper_dict['Type'] = paper_dict['Type'].title()

	print >> outfile, paper_dict
	del paper_dict




def get_papers_Cochrane(query, type_):

	head = ({'host': 'onlinelibrary.wiley.com', 'referer': 'http://onlinelibrary.wiley.com/cochranelibrary/search'})

	query = ({'targetPlatform':'linux', \
			'resultDetailFormat': 'exportCitation3g', \
			'exportAll': 'Export Citation',  \
			'sortBy': 'most_relevance', \
			'searchRow.ordinal': '0', \
			'hiddenFields.currentPage': '1', \
			'searchRow.searchCriterias[0].term': query, \
			'searchRow.searchCriterias[0].fieldRestriction': '', \
			'searchRow.searchOptions.searchType': 'All', \
			'searchRow.searchOptions.onlinePublicationStartMonth': '0', \
			'searchRow.searchOptions.onlinePublicationEndMonth': '0', \
			'searchRow.searchOptions.disableAutoStemming': 'true', \
			'searchRow.searchOptions.dateType': 'pubAllYears', \
			'searchRow.searchOptions.onlinePublicationLastNoOfMonths': '0', \
			'hiddenFields.sortBy': 'most_relevance', \
			'hiddenFields.searchFilters.filterByIssue': 'all', \
			'hiddenFields.searchFilters.filterByProduct': type_, \
			'hiddenFields.searchFilters.filterByType': 'All', \
			'hiddenFields.searchFilters.displayIssuesAndTypesFilters': 'false'})

	r = requests.post('http://onlinelibrary.wiley.com/cochranelibrary/search/citation/export', data=query, headers=head)
	test_response(r.status_code)

	return r.content



def get_data_Cochrane(query):

	outfile = codecs.open('temp_cochrane.csv', 'w', encoding='utf-8')

	for type_ in ['clinicalTrialsDoi', 'cochraneReviewsDoi', 'otherReviewsDoi', \
				 'methodStudiesDoi', 'techAssessmentsDoi', 'economicEvaluationsDoi']:
		content = get_papers_Cochrane(query, type_)

		if len(content) > 1:
			papers = content.replace('\n\n\n', '\t\n').replace('\n', '\t').replace('\t\t', '\n')
			papers_lines = papers.strip().split('\n')

			if len(papers_lines) > 10000:
				print 'Warning: more than 10000 results. Obtained:', len(papers_lines)
				num_matches = 10000
			else:
				num_matches = len(papers_lines)

			for i in range(num_matches):
				extract_data_Cochrane(papers_lines[i], outfile)
		
	
	outfile.close()





