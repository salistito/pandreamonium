from nltk.tokenize import sent_tokenize, word_tokenize

def clean_text(text, punctuations="", stop_words=[]):
  if punctuations:
    text = text.translate(str.maketrans('','', punctuations)).strip()
  if stop_words:
    text = " ".join([word for word in text.split() if word.lower() not in stop_words]).strip()
  return " ".join(text.split()).strip()

def strip_punctuation(text):
  return " ".join(text).strip().replace(" ,", ",").replace(" .", ".")

# sent_tokenize Example:
# sent_tokenize(three_little_pigs_esp, language='spanish') -> ['sentence_1', 'sentence_2", ..., 'sentence_n']
# word_tokenize Example:
# word_tokenize("God is Great! I won a lottery.") -> ['God', 'is', 'Great', '!', 'I', 'won', 'a', 'lottery', '.']
def text_to_extracts(text, max_extract_length=100):
  text_sentences = sent_tokenize(text, language='spanish')
  extracts = [] # Extract length set to 100 "words" (See second example)
  current_extract = None
  current_extract_num_words = 0
  for sentence in text_sentences:
      sentence = clean_text(sentence)
      if current_extract is None:
          current_extract = sentence
      else:
          current_extract+=' '+sentence
      current_extract_num_words+=len(word_tokenize(sentence, language='spanish'))
      if current_extract_num_words > max_extract_length:
          extracts.append(current_extract)
          current_extract = None
          current_extract_num_words = 0

  # Append del extract rezagado
  if current_extract is not None:
      extracts.append(current_extract)
  return extracts


no_lemmatized_pos = ["PROPN", "PRON", "NUM"]
def lemmatize(nlp, text, split_return=True):
    text = nlp(text)
    # lemmatizing
    text = [word.text if word.pos_ in no_lemmatized_pos else word.lemma_.lower().strip() for word in text]        
    return text if split_return else " ".join(text).strip()