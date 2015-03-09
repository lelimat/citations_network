# pubmed_networks.py
# C: Jul 24, 2013
# M: Mar  9, 2015
# Leandro Lima <llima@ime.usp.br>

import sys
#from os import getenv
import twill
from twill.commands import *
from StringIO import StringIO
twill.set_output(StringIO())
from Bio import Entrez
from Bio import Medline
emails = ["llima@ime.usp.br", "lelimaufc@gmail.com", "limal1@email.chop.edu"]
from lxml.html import parse, document_fromstring
import networkx as nx
from random import sample
from time import sleep


def get_references(pmid):
    pmc = articles_dic[pmid]['pmc']
    references = []
    if not pmc == '?':
        print 'trying', pmid, pmc
        try:
            go('http://www.ncbi.nlm.nih.gov/pmc/articles/'+pmc+'/')
            text = show()
            page = document_fromstring(text)
            refs = page.find_class('nowrap ref pubmed')
            for ref in refs:
                href = ref.getchildren()[0].get('href')
                references.append(href.replace('/pubmed/', ''))
        except:
            pass
    return references


def get_citations(pmid):
    citations = []
    try:
        res = Entrez.elink(db="pubmed", LinkName="pubmed_pubmed_citedin", from_uid=pmid, rettype='text')
        text = ''
        for r in res:
            text += r
        page = document_fromstring(text)
        links = page.cssselect('linksetdb')[0].getchildren()
        for l in links:
            if l.tag == 'id':
                citations.append(l.text)
    except:
        pass
    return citations



articles_dic = {}


def main():
    retmax = int(sys.argv[1])
    abstracts_file = open('abstracts.txt', 'w')
    
    distance = 2
    d = 0
    searched_pmids = {}
    net = nx.DiGraph()
    Entrez.email = sample(emails, 1)
    h = Entrez.esearch(db='pubmed', term='Pico AR[last author]', retmax=retmax)
    record = Entrez.read(h)
    pmids = record['IdList']
    print pmids
    medline = Entrez.efetch(db='pubmed', id=pmids, rettype='medline', retmode='text')
    recs_medline = Medline.parse(medline)
    for rec_medline in recs_medline:
        pmid = rec_medline.get('PMID', '?')
        if not articles_dic.has_key(pmid):
            title   = rec_medline.get('TI', '?')
            year    = rec_medline.get('DP', '?')[:4]
            pmc     = rec_medline.get('PMC', '?')
            journal = rec_medline.get('JT', '?')
            short   = rec_medline.get('FAU', '?')[0].split(',')[0] + ' et al. (' + year + ')'
            articles_dic[pmid] = {'short':short, 'year':year, 'title':title, 'pmc':pmc, 'journal':journal, 'is_seed':'yes'}
            print short, ':::', title
            abstract = rec_medline.get('AB', '?')
            abstracts_file.write(abstract + '\n')
    
    for pmid in pmids:
        searched_pmids[pmid] = 0
    
    while d < distance:
        d += 1
        pmids = []
        for pmid in searched_pmids.keys():
            if searched_pmids[pmid] == 0:
                pmids.append(pmid)
                searched_pmids[pmid] = 1

        i = 0
        for pmid in pmids:
            i += 1
            sleep(1)
            print 'distance =',d,'| pmid',i,'of',len(pmids)
            Entrez.email = sample(emails, 1)
            # Getting citations
            citations = get_citations(pmid)
            if len(citations) > 0:
                medline = Entrez.efetch(db='pubmed', id=citations, rettype='medline', retmode='text')
                recs_medline = Medline.parse(medline)
                for rec_medline in recs_medline:
                    pmid = rec_medline.get('PMID', '?')
                    if not articles_dic.has_key(pmid):
                        title   = rec_medline.get('TI', '?')
                        year    = rec_medline.get('DP', '?')[:4]
                        pmc     = rec_medline.get('PMC', '?')
                        journal = rec_medline.get('JT', '?')
                        short   = rec_medline.get('FAU', '?')[0].split(',')[0] + ' et al. (' + year + ')'
                        articles_dic[pmid] = {'short':short, 'year':year, 'title':title, 'pmc':pmc, 'journal':journal, 'is_seed':'no'}
                for citation in citations:
                    if not net.has_edge(citation, pmid) and citation != pmid:
                        net.add_edge(citation, pmid)
                    if not searched_pmids.has_key(citation):
                        searched_pmids[citation] = 0

            # Getting references
            references = get_references(pmid)
            if len(references) > 0:
                medline = Entrez.efetch(db='pubmed', id=references, rettype='medline', retmode='text')
                recs_medline = Medline.parse(medline)
                for rec_medline in recs_medline:
                    pmid = rec_medline.get('PMID', '?')
                    if not articles_dic.has_key(pmid):
                        title   = rec_medline.get('TI', '?')
                        year    = rec_medline.get('DP', '?')[:4]
                        pmc     = rec_medline.get('PMC', '?')
                        journal = rec_medline.get('JT', '?')
                        short   = rec_medline.get('FAU', '?')[0].split(',')[0] + ' et al. (' + year + ')'
                        articles_dic[pmid] = {'short':short, 'year':year, 'title':title, 'pmc':pmc, 'journal':journal, 'is_seed':'no'}
                for reference in references:
                    if not net.has_edge(pmid, reference) and pmid != reference:
                        net.add_edge(pmid, reference)
                    if not searched_pmids.has_key(reference):
                        searched_pmids[reference] = 0  
    
    betweenness = nx.betweenness_centrality(net)
    pagerank = nx.pagerank(net)

    # Writing edges
    print 'Writing edges'
    edges_files = open('citations_edges.txt', 'w')
    edges_files.write('paper\treference\n')
    for edge in net.edges():
        edges_files.write('%s\t%s\n' % (edge[0], edge[1]))
    edges_files.close()

    # Writing nodes
    print 'Writing nodes'
    nodes_file = open('citations_nodes.txt', 'w')
    nodes_file.write('pmid\tshort\tis_seed\tbetweenness\tpagerank\tin_degree\tout_degree\tyear\ttitle\n')
    nodes = net.nodes()
    for pmid in nodes: #articles_dic.keys():
        print pmid, net.in_degree(pmid), net.out_degree(pmid)
        nodes_file.write('%s\t%s\t%s\t%f\t%f\t%d\t%d\t%s\t%s\n' % \
            (pmid, articles_dic[pmid]['short'], articles_dic[pmid]['is_seed'], betweenness[pmid], pagerank[pmid], net.in_degree(pmid), net.out_degree(pmid), articles_dic[pmid]['year'], articles_dic[pmid]['title']))
    nodes_file.close()


if __name__ == '__main__':
    main()

