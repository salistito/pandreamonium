import io
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
from src.models.text_processing import consolidated_stop_words, consolidated_punctuation, es_nlp
from src.utils.text_processing import clean_text, lemmatize

from collections import Counter

def top_n_words(text="", n=10):
  # Count the frequency of words in the text
  words = text.split()
  frequency = Counter(words)

  # Select the most frequent words
  top_n_words = [word for word, freq in frequency.most_common() if word.lower() not in consolidated_stop_words][:n]  # n=10 is the number of keywords you want to select
  return top_n_words

def plot_word_cloud(cloud_text):
  # Crear la words cloud
  wordcloud = WordCloud(width=800, height=400, background_color='white').generate(cloud_text)

  # Graficar la words cloud
  plt.figure(figsize=(10, 5))
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
  plt.tight_layout()
  plt.show()

  # Convert the plot to an image
  buffer = io.BytesIO()
  plt.savefig(buffer, format="png")
  buffer.seek(0)
  image = Image.open(buffer)

  return image

def word_cloud_pipeline(text, verbose=False):
  # Filtrar stop words y puntuaciones para words cloud
  cloud_filtered_text = clean_text(text, punctuations=consolidated_punctuation, stop_words=consolidated_stop_words)

  # Lemmatizer
  cloud_filtered_text_lemmas = lemmatize(es_nlp, cloud_filtered_text, split_return=False)

  # Plot word cloud
  word_cloud = plot_word_cloud(cloud_filtered_text)

  # Plot word cloud lemmatized
  lemmatized_word_cloud = plot_word_cloud(cloud_filtered_text_lemmas)

  # Top n frequent words
  #filtered_text_top_words = top_n_words(text=cloud_filtered_text, n=10)
  filtered_text_lemmas_top_words = top_n_words(text=cloud_filtered_text_lemmas, n=10)

  if verbose:
    print(cloud_filtered_text)
    print(cloud_filtered_text_lemmas)
    print()
    print("Word Cloud")
    print("\nTop 10 filtered_text_lemmas_top_words:\n", filtered_text_lemmas_top_words)

  return word_cloud, lemmatized_word_cloud, filtered_text_lemmas_top_words