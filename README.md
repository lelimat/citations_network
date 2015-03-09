# citations_network

Using BioPython/PubMed API, I'm constructing a network of citations (http://nrnb.org/images/lima.png). The nodes are papers, retrieved by a search term (and have: pubmed ID, year, title, page rank measure, etc.). The edges are citations, retrieved by the API. With these measures, it's possible to see most cited papers, organize them by year or by page rank measure, as well as highlight nodes/papers with specific keywords, using the search box.

