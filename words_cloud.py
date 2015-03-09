# words_cloud.py
# C: Jul 18, 2014
# M: Mar  9, 2015
# A: Leandro Lima <llima@ime.usp.br>


from wordcloud import WordCloud # https://github.com/amueller/word_cloud
import matplotlib.pyplot as plt


# Read the abstracts.
text = open('abstracts.txt').read()

wordcloud = WordCloud(font_path='Verdana.ttf').generate(text)
plt.imshow(wordcloud)
plt.axis("off")
plt.savefig('abstracts.png')

