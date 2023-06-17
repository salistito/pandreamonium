# import and initialize the tokenizer and model from the checkpoint
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification, AutoModelForSeq2SeqLM, AutoModel
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
#from flair.embeddings import TransformerDocumentEmbeddings
from deep_translator import GoogleTranslator
from src.utils.text_processing import clean_text, text_to_extracts
import textwrap
import time

es_en_translator_checkpoint = "Helsinki-NLP/opus-mt-es-en"
summarizer_checkpoint = "philschmid/bart-large-cnn-samsum" #"facebook/bart-large-cnn"
en_es_translator_checkpoint = "Helsinki-NLP/opus-mt-en-es"

#es_en_tokenizer = AutoTokenizer.from_pretrained(es_en_translator_checkpoint)
#es_en_model = AutoModelForSeq2SeqLM.from_pretrained(es_en_translator_checkpoint)
#es_en_translator = pipeline("translation", model=es_en_model, tokenizer=es_en_tokenizer)

summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_checkpoint)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(summarizer_checkpoint)
summarizer = pipeline("summarization", model=summarizer_model, tokenizer=summarizer_tokenizer)

#en_es_tokenizer = AutoTokenizer.from_pretrained(en_es_translator_checkpoint)
#en_es_model = AutoModelForSeq2SeqLM.from_pretrained(en_es_translator_checkpoint)
#en_es_translator = pipeline("translation", model=en_es_model, tokenizer=en_es_tokenizer)

# Create KeyBERT instance with default English model
keybert_model = KeyBERT()


def llm_translator(translator, text, translator_max_length):
  translated_text = clean_text(translator(text, max_length=translator_max_length)[0]['translation_text'])
  return translated_text

def google_translator(text, source, target):
  translated_text = clean_text(GoogleTranslator(source=source, target=target).translate(text))
  return translated_text

def llm_summarizer(summarizer, text, summary_max_length, summary_min_length):
  text_summary = clean_text(summarizer(text, max_length=summary_max_length, min_length=summary_min_length)[0]['summary_text'])
  return text_summary

def print_summarize_pipeline(translated_extract, translated_extract_summary, summary):
  print("--------------------------------------------------------------------")
  print(textwrap.fill(translated_extract, 150))
  print()
  print(textwrap.fill(translated_extract_summary, 150))
  print()
  print(textwrap.fill(summary, 150))
  print("--------------------------------------------------------------------")
  print()

# Translator: Google translate
def summarize(extract, summary_max_length=142, summary_min_length=56, translator_max_length=512, iterative_summary_length=False, verbose=False):
  # A helpful rule of thumb is that one token generally corresponds to ~4 characters of text for common English text. This translates to roughly ¾ of a word (so 100 tokens ~= 75 words) -> 4 chars are 1 token, so len//4
  translated_extract = google_translator(extract, source='es', target='en')
  if iterative_summary_length:
    summary_max_length=(len(translated_extract)//4)//2
    summary_min_length=int(summary_max_length*(2/5))
  translated_extract_summary = llm_summarizer(summarizer, translated_extract, summary_max_length, summary_min_length) 
  summary = google_translator(translated_extract_summary, source='en', target='es')
  if verbose:
    print_summarize_pipeline(translated_extract, translated_extract_summary, summary)
  return translated_extract, translated_extract_summary, summary


def get_translated_extracts(text, max_extract_length=100, source="es", target="en", verbose=False):
  extracts = text_to_extracts(text, max_extract_length)
  translated_extracts = []
  for extract in extracts:
    if source!=target:
      translated_extract = google_translator(extract, source=source, target=target)
    else:
      translated_extract = extract
    translated_extracts.append(translated_extract)
  if verbose:
    print("Original text length: ", len(text))
    print("Number of Extracts: ", len(translated_extracts))
  return translated_extracts


def summarize_pipeline(text, max_extract_length=100, verbose=False):
  dt_start = time.time()

  extracts = text_to_extracts(text, max_extract_length)
  english_extracts = []
  english_extracts_summaries = []
  summaries = []
  for extract in extracts:
    english_extract, english_extract_summary, summary = summarize(extract, verbose=verbose)
    english_extracts.append(english_extract)
    english_extracts_summaries.append(english_extract_summary)
    summaries.append(summary)

  dt_end = time.time()

  if verbose:
    print("Original text length: ", len(text))
    print("Number of Extracts: ", len(summaries))
    print("Execution Time: ", (dt_end-dt_start))

  return english_extracts, english_extracts_summaries, summaries

"""
import concurrent.futures
import time

def summarize_pipeline_parallel(text, max_extract_length=100, verbose=False):
    dt_start = time.time()

    extracts = text_to_extracts(text, max_extract_length)
    english_extracts = []
    english_extracts_summaries = []
    summaries = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Procesar los extractos en paralelo
        futures = [executor.submit(summarize, extract, verbose=verbose) for extract in extracts]

        # Obtener los resultados de cada tarea completada
        for future in concurrent.futures.as_completed(futures):
            english_extract, english_extract_summary, summary = future.result()
            english_extracts.append(english_extract)
            english_extracts_summaries.append(english_extract_summary)
            summaries.append(summary)

    dt_end = time.time()

    if verbose:
        print("Original text length: ", len(text))
        print("Number of Extracts: ", len(summaries))
        print("Execution Time: ", (dt_end - dt_start))

    return english_extracts, english_extracts_summaries, summaries


# Define la función para procesar un extracto y obtener el resumen
def process_extract(extract, verbose=False):
    english_extract, english_extract_summary, summary = summarize(extract, verbose=verbose)
    return english_extract, english_extract_summary, summary

def summarize_pipeline_parallel2(text, max_extract_length=100, verbose=False):
    dt_start = time.time()

    extracts = text_to_extracts(text, max_extract_length)
    english_extracts = []
    english_extracts_summaries = []
    summaries = []

    # Crea un ProcessPoolExecutor con el número máximo de procesos predeterminado
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    # Crea un ThreadPoolExecutor con el número máximo de hilos predeterminado
    #with concurrent.futures.ThreadPoolExecutor() as executor:
        # Crea una lista de Future objects para almacenar los resultados de la ejecución en paralelo
        futures = [executor.submit(process_extract, extract, verbose) for extract in extracts]

        # Espera a que se completen todos los Future objects y obtiene los resultados
        for future in concurrent.futures.as_completed(futures):
            english_extract, english_extract_summary, summary = future.result()
            english_extracts.append(english_extract)
            english_extracts_summaries.append(english_extract_summary)
            summaries.append(summary)

    dt_end = time.time()

    if verbose:
        print("Original text length: ", len(text))
        print("Number of Extracts: ", len(summaries))
        print("Execution Time: ", (dt_end - dt_start))

    return english_extracts, english_extracts_summaries, summaries
"""

def keybert_key_concepts(texts_array, n=15, distance_threshold=0.3, verbose=False):
  """
  # Create KeyBERT instance with Multilanguage (Spanish) model
  #keybert_model = KeyBERT(model='distiluse-base-multilingual-cased')
  #keybert_model = KeyBERT(model=TransformerDocumentEmbeddings('dbmdz/bert-base-german-uncased'))

  # Extract key phrases
  keywords = keybert_model.extract_keywords(text)
  keywords1 = keybert_model.extract_keywords(text, keyphrase_ngram_range=(1, 1), stop_words='spanish', top_n=n)  # n is the number of key phrases to select
  keywords2 = keybert_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='spanish', top_n=n)
  keywords3 = keybert_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words=custome_stop_words, top_n=n)
  keywords4 = keybert_model.extract_keywords(text, keyphrase_ngram_range=(1, 4), stop_words=custome_stop_words, top_n=n)

  # Init vectorizer for the Spanish language
  #vectorizer = KeyphraseCountVectorizer(spacy_pipeline='es_core_news_lg', pos_pattern='<ADJ.*>*<N.*>+', stop_words='spanish')  # default pos_patter: '<J.*>*<N.*>+')
  #vectorizer = KeyphraseCountVectorizer(spacy_pipeline='es_core_news_lg', pos_pattern='<ADJ.*>*<N.*>+')  # default pos_patter: '<J.*>*<N.*>+')
  #vectorizer = KeyphraseCountVectorizer(spacy_pipeline='es_core_news_lg', stop_words=custome_stop_words)  # default pos_patter: '<J.*>*<N.*>+')
  #vectorizer = KeyphraseCountVectorizer(spacy_pipeline='es_core_news_lg')  # default pos_patter: '<J.*>*<N.*>+')
  """

  # Clean and join text
  joined_text = " ".join(texts_array).strip()
  joined_text = clean_text(joined_text, stop_words=[])

  # Extract key concepts on joined text (returns The top n keywords for a document with their respective distances to the input document)
  joined_key_concepts = keybert_model.extract_keywords(docs=[joined_text], vectorizer=KeyphraseCountVectorizer(), top_n=n)

  # Extract key concepts on texts array (returns The top n keywords for a document with their respective distances to the input document)
  array_key_concepts = keybert_model.extract_keywords(docs=texts_array, vectorizer=KeyphraseCountVectorizer(), top_n=n)
  
  # Consolidate Key Concepts
  consolidated_key_concepts = {}
  unique_joined_key_concepts = set(joined_key_concepts)
  
  if verbose:
    for key_concept in joined_key_concepts:
        print("joined_key_concepts: ", key_concept)
    for key_concepts_array in array_key_concepts:
        print("array_key_concepts: ", key_concepts_array)

  [consolidated_key_concepts.update({key_concept: key_concept_distance}) for key_concept, key_concept_distance in unique_joined_key_concepts if key_concept_distance >= distance_threshold]

  if type(array_key_concepts[0])==list:
    [consolidated_key_concepts.update({key_concept: max(key_concept_distance, consolidated_key_concepts.get(key_concept, -1))}) for key_concepts_array in array_key_concepts for (key_concept, key_concept_distance) in key_concepts_array if key_concept_distance >= distance_threshold]
  else:
    [consolidated_key_concepts.update({key_concept: max(key_concept_distance, consolidated_key_concepts.get(key_concept, -1))}) for (key_concept, key_concept_distance) in array_key_concepts if key_concept_distance >= distance_threshold]


  sorted_consolidated_key_concepts = sorted(consolidated_key_concepts.items(), key=lambda x:x[1], reverse=True)
  return dict(sorted_consolidated_key_concepts)


def key_concepts_translator(consolidated_key_concepts):
  translations = GoogleTranslator(source='en', target='es').translate_batch(list(consolidated_key_concepts.keys()))
  translated_consolidated_key_concepts_list = translations #[translation.text.lower() for translation in translations]

  # New dict with translated keys
  translated_consolidated_key_concepts = {}
  for translated_key_concept, key_concept_distance in zip(translated_consolidated_key_concepts_list, consolidated_key_concepts.values()):
    if (translated_key_concept not in translated_consolidated_key_concepts) or (translated_consolidated_key_concepts[translated_key_concept] < key_concept_distance):
      translated_consolidated_key_concepts[translated_key_concept] = key_concept_distance

  return translated_consolidated_key_concepts

def key_concepts_extractor(extracts, n=15, verbose=False):
  consolidated_key_concepts = keybert_key_concepts(extracts, n=n, verbose=False)
  translated_consolidated_key_concepts = key_concepts_translator(consolidated_key_concepts)
  
  if verbose:
    print("Conceptos Claves Ingles:\n", consolidated_key_concepts)
    print("Conceptos Claves:\n", translated_consolidated_key_concepts)
    print("Cantidad de Conceptos Claves: ", len(translated_consolidated_key_concepts))

  return consolidated_key_concepts, translated_consolidated_key_concepts

# TODO: Consolidators file
from difflib import SequenceMatcher

def get_similarity(string1, string2):
  return SequenceMatcher(None, string1, string2).ratio()

def consolidate_key_concepts_and_no_processed_entities(key_concepts_dict, entities_dict, similarity_threshold=0.66):
  key_concepts_list = list(key_concepts_dict.keys())
  entities_list = list(entities_dict.keys())

  consolidation = {}
  for key_concept in key_concepts_list:
    for entity in entities_list:
      if get_similarity(key_concept, entity) >= similarity_threshold:
        consolidation[entity] = entities_dict[entity]

  return consolidation
