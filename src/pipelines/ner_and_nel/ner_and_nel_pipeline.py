from spacy import displacy
from src.models.wikidata import all_properties, generate_entity_data_standar_params
from src.pipelines.ner_and_nel import get_wikidata_entity_info_in_NL, get_similar_entity

def get_wikidata_url(kb_id):
  return f'https://www.wikidata.org/wiki/{kb_id}' if kb_id else ''

def add_entity(entities_dict, new_entity, new_entity_data):
  if new_entity in entities_dict:
      entities_dict[new_entity]['sentences'].append(new_entity_data["sentences"][0])
  else:
      entities_dict[new_entity] = new_entity_data
  return entities_dict

def generate_entity_data(entity, props_to_remove=all_properties, properties_per_category=1, result_limit=3, query_timeout=15, verbose=False):
    entity_data = {
        #"start": entity.start_char,
        #"end": entity.end_char,
        "entity_label": entity.label_,
        "sentences": [entity.sent.text]
    }

    if entity.label_ != "MISC":
        try:
          # json with properties (On Error: str or empty list)
            entity_properties = get_wikidata_entity_info_in_NL(entity.text, properties_per_category)
            entity_id = entity_properties.pop("id")
            parsed_instance_similar_entities, parsed_specific_similar_entities = get_similar_entity(
                entity.text,
                props_to_remove,
                properties_per_category,
                result_limit,
                query_timeout,
                verbose
            )
            entity_data.update({
                #"kb_id": entity.kb_id_,
                #"wikidata_url": get_wikidata_url(entity.kb_id_),
                "entity_id": entity_id,
                "entity_wikidata_url": get_wikidata_url(entity_id),
                "entity_properties": entity_properties,
                "related_entities": {
                    "instance_similar_entities": parsed_instance_similar_entities,
                    "specific_similar_entities": parsed_specific_similar_entities,
                },
            })
        except:
            entity_data["entity_label"] = "MISC"
    
    return entity_data

def detect_entities(nlp, text="", extracts=[], generate_entity_data_params=generate_entity_data_standar_params, verbose=False):
  """
  Two modes of execution
  """
  # MISC: Miscellaneous entities, e.g., events, nationalities, products, or works of art.
  complete_text_entities = {}
  extracts_entities = {}
  # Parámetros a definir (Slider with options )
  props_to_remove, properties_per_category, result_limit, query_timeout = tuple(generate_entity_data_params.values())
  complete_text = nlp(text)
  for entity in complete_text.ents:
    #print(entity.text, '|', entity.label_, '|', entity.kb_id_, '|', entity.sent)
    entity_data = generate_entity_data(entity, props_to_remove, properties_per_category, result_limit, query_timeout, verbose=verbose)
    complete_text_entities = add_entity(
        entities_dict=complete_text_entities,
        new_entity=entity.text,
        new_entity_data=entity_data)

  for extract in extracts:
    extract = nlp(extract)
    for entity in extract.ents:
      #print(entity.text, '|', entity.label_, '|', entity.kb_id_, '|', entity.sent)
      entity_data = generate_entity_data(entity, props_to_remove, properties_per_category, result_limit, query_timeout, verbose=verbose)    
      extracts_entities = add_entity(
          entities_dict=extracts_entities,
          new_entity=entity.text,
          new_entity_data=entity_data
          )

  return complete_text_entities, extracts_entities

def consolidate_entities(entities_dict1, entities_dict2):
  consolidated_entities = {}
  for entity in entities_dict1.keys():
    if entity in entities_dict2.keys():
      consolidated_entities = add_entity(
          entities_dict=consolidated_entities,
          new_entity=entity,
          new_entity_data=entities_dict1[entity]
          )
  return consolidated_entities

def displacy_entities(nlp, text):
  doc = nlp(text)
  # Se supone que esto pinta en colores las entidades encontradas
  #displacy.render(doc, style='ent', jupyter=True)

def ner_pipeline(nlp, text, summaries, generate_entity_data_params, verbose=False):
  complete_text_entities, extracts_entities = detect_entities(nlp, text, summaries, generate_entity_data_params, verbose=verbose)
  
  consolidated_entities = consolidate_entities(complete_text_entities, extracts_entities)

  if verbose:
    print("Complete Text Entities: ", list(complete_text_entities.keys()))
    print("Extracts Entities: ", list(extracts_entities.keys()))
    print("Consolidated Entities: ", list(consolidated_entities.keys()))
    print()

    displacy_entities(nlp, text)
  return complete_text_entities, extracts_entities, consolidated_entities