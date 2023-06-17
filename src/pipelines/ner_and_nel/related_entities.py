from src.utils.wikidata_requests import requests_func
from src.pipelines.ner_and_nel.wikidata_properties import get_wikidata_entity_info, parse_specific_properties
from src.utils.outputs import print_dict

def generate_sparql_query(entity_id, properties_dict, exact_properties_query, prop_idx_to_remove, result_limit=5):
  # prop idx
  absolute_prop_idx = -1

  # Exact query search
  if exact_properties_query:
      select_clause = """
      SELECT ?similarEntity ?similarEntityLabel WHERE {
      """
      where_clause = ""
      filter_clause = f"""
          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "es" .
          }}
          #FILTER(LANG(?similarEntityLabel) = "es")
          FILTER(?similarEntity != wd:{entity_id})
      }}
      LIMIT {result_limit}
      """
      for prop, vals in properties_dict.items():
        for val in vals:
          absolute_prop_idx+=1 
          # Si se llega al indice de la propiedad a remover, retornar tempranamente la query hasta ese momento generada
          if absolute_prop_idx == prop_idx_to_remove:
            query = select_clause + where_clause + filter_clause
            return query
          # Si aún no se llega al indice de la propiedad a remover, concatenar propiedades a la query
          else:
            where_clause += f"""
            ?similarEntity wdt:{prop} wd:{val}.   
            """
      query = select_clause + where_clause + filter_clause
      return query

  # Filter mode
  else:
    select_and_first_filter_clause = f"""
      SELECT DISTINCT ?similarEntity ?label WHERE {{
      wd:{entity_id} ?predicate ?object.
      ?similarEntity ?predicate ?object.
      ?similarEntity rdfs:label ?label.
      FILTER(LANG(?label) = "es")
      FILTER(?similarEntity != wd:{entity_id})
      FILTER EXISTS {{
    """
    properties_filter_clause = ""
    limit_clause = f"""
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "es" .
        }}
      }}
    }}
    LIMIT {result_limit}
    """
    for prop, vals in properties_dict.items():
      for val in vals:
        absolute_prop_idx+=1
        # Si se llega al indice de la propiedad a remover, retornar tempranamente la query hasta ese momento generada
        if absolute_prop_idx == prop_idx_to_remove:
          query = select_and_first_filter_clause + properties_filter_clause + limit_clause
          return query
        # Si aún no se llega al indice de la propiedad a remover, concatenar propiedades a la query
        else:
          properties_filter_clause += f"""
          ?similarEntity wdt:{prop} wd:{val}.   
          """
    query = select_and_first_filter_clause + properties_filter_clause + limit_clause
    return query

def get_wikidata_sparql_query_result(query, query_timeout):
  # URL de la API de Wikidata
  wikidata_api_url = 'https://query.wikidata.org/sparql'
  wikidata_response_content, wikidata_response_error = requests_func(
      request_url=wikidata_api_url,
      request_params={'query': query, 'format': 'json'},
      timeout=query_timeout
      ).values()
  try:
    parsed_response = wikidata_response_content.json()["results"]["bindings"]
  except:
    parsed_response = []
  return parsed_response

def execute_query_until_result(entity_id, query_properties_dict, exact_properties_query, result_limit, query_timeout, verbose=False):
  similar_entities = []
  prop_idx_to_remove = sum(len(properties_list) for properties_list in list(query_properties_dict.values()))  # Al comienzo no se elimina ninguna
  idx_to_remove_limit = 1 if exact_properties_query else 0 # Configurar si se quieren respuestas con 0 filtros (estas entregarían cualquier cosa)
  while not (similar_entities) and prop_idx_to_remove>=idx_to_remove_limit:
    # Generar consultas SPARQL para buscar entidades similares
    query = generate_sparql_query(entity_id, query_properties_dict, exact_properties_query, prop_idx_to_remove, result_limit)

    # Enviar la consulta a la API de Wikidata
    similar_entities = get_wikidata_sparql_query_result(query, query_timeout)
    
    # Aumentar cantidad de propiedades a remover para generar una siguiente consulta menos estricta
    prop_idx_to_remove-=1

    if verbose:
      print(f"query_{'exact' if exact_properties_query else 'filter'} prop_idx_to_remove: ", prop_idx_to_remove)
      print(f"query_{'exact' if exact_properties_query else 'filter'}:", query)
      #print(f"{'specific' if exact_properties_query else 'general'}_similar_entities:", similar_entities)

    """
    # Setear la consulta SPARQL para buscar entidades similares
    sparql.setQuery(query_exact)
    # Establece el formato de salida de la consulta como JSON y ejecuta la consulta
    sparql.setReturnFormat(JSON)
    response = sparql.query().convert()["results"]["bindings"]
    print(response)
    """
  return similar_entities

def parse_wikidata_sparql_query_result(result):
  parsed_result = {}
  for entity in result:
    try:
      parsed_result[entity["similarEntityLabel"]["value"]] = entity["similarEntity"]["value"]
    except:
      try:
        parsed_result[entity["label"]["value"]] = entity["similarEntity"]["value"]
      except:
        pass
  return parsed_result

# Crea una instancia del objeto SPARQLWrapper para consultar la API de Wikidata
#sparql = SPARQLWrapper(wikidat_api_url)
def get_similar_entity(entity, props_to_remove, properties_per_category, result_limit, query_timeout, verbose=False):
  try:
    # Get Wikidata Properties
    wikidata_result = get_wikidata_entity_info(entity=entity, properties_per_category=properties_per_category)
    entity_id = wikidata_result[0]["id"]
  except:
    # Error on the request, wikidata_result is a string error
    return wikidata_result
    

  # Definir que propiedades se ocuparán en la query SQL
  props_to_remove_on_query_filter = [prop for prop in props_to_remove if prop not in ["instances_of"]] # Remover todas excepto instances_of
  props_to_remove_on_query_exact = ["image_url"]
  # Obtener propiedades
  properties_dict_on_query_filter = parse_specific_properties(wikidata_result, props_to_remove=props_to_remove_on_query_filter)
  properties_dict_on_query_exact = parse_specific_properties(wikidata_result, props_to_remove=props_to_remove_on_query_exact)

  # Enviar la consulta a la API de Wikidata hasta obtener resultados
  # Top n=5 entidades con alguna relación en común pero que sean de las mismas "instances_of" de la propiedad buscada
  instance_similar_entities = execute_query_until_result(entity_id, properties_dict_on_query_filter, exact_properties_query=False, result_limit=result_limit, query_timeout=query_timeout, verbose=verbose)
  # Top n=5 entidades que compartan cierta cantidad de propiedades
  specific_similar_entities = execute_query_until_result(entity_id, properties_dict_on_query_exact, exact_properties_query=True, result_limit=result_limit, query_timeout=query_timeout, verbose=verbose)

  # Parse resuls to dict
  parsed_instance_similar_entities = parse_wikidata_sparql_query_result(instance_similar_entities)
  parsed_specific_similar_entities = parse_wikidata_sparql_query_result(specific_similar_entities)

  if verbose:
    # Wikidata Result
    print("wikidata_result: ", wikidata_result)
    # Properties dict
    print("properties_dict_on_query_filter: ", properties_dict_on_query_filter)
    print("properties_dict_on_query_exact: ", properties_dict_on_query_exact)
    print()
    # Similar Entities
    print(f"Original Entity: {entity}, Properties per Category {properties_per_category}")
    print("----------------------------------------------------")
    print(f"{len(parsed_instance_similar_entities.keys())} 'Same Instance' Similar Entities:")
    print_dict(parsed_instance_similar_entities)
    print("----------------------------------------------------")
    print(f"{len(parsed_specific_similar_entities.keys())} Specific Similar Entities")
    print_dict(parsed_specific_similar_entities)

  return parsed_instance_similar_entities, parsed_specific_similar_entities