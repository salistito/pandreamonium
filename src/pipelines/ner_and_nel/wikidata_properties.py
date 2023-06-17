import hashlib
import urllib.parse
from src.models.wikidata import general_properties, specific_properties, no_search_name_properties
from src.utils.wikidata_requests import WikidataActions, fetch_wikidata

def get_general_property(data, entity_id, property_name, properties_per_category=1):
  try:
    # Consider only the first 3 values (Potencial refractor: Consider all but "translate" to natural language only 3)
    property_values = [v['value'] for v in data['entities'][entity_id][property_name]['en']][0:3]#[0:properties_per_category]
  except:
    try:
      property_values = data['entities'][entity_id][property_name]['en']['value']
    except:
      property_values = None
  return property_values

def parse_general_properties_to_NL(wikidata_result):
  return {
      prop: values
      for prop, values in wikidata_result[0].items()
      if (prop in general_properties.keys() or prop in ["id", "image_url"]) and values
  }

def get_entity_image_url(image_name):
  # The final image URL will be: https://upload.wikimedia.org/wikipedia/commons/a/ab/img_name.ext, where a and b are the first and the second chars of MD5 hashsum of the img_name.ext (with all whitespaces replaced by _)
  md5_hashsum_value = str(hashlib.md5(image_name.encode()).hexdigest())
  a,b = md5_hashsum_value[0], md5_hashsum_value[1]
  parsed_image_name = urllib.parse.quote(image_name)
  image_url = f"https://upload.wikimedia.org/wikipedia/commons/{a}/{a}{b}/{parsed_image_name}"
  return image_url

def get_specific_property(data, entity_id, property_id, properties_per_category=1):
  try:
    if property_id == "P18": # image property
      image_name = [v['mainsnak']['datavalue']['value'] for v in data['entities'][entity_id]['claims']["P18"]][0].replace(" ", "_")
      return get_entity_image_url(image_name)

    # All the others specifics properties
    # Consider only the first "properties_per_category" values (Potencial refractor: Consider all but "translate" to natural language only "properties_per_category")
    property_values = [v['mainsnak']['datavalue']['value']['id'] for v in data['entities'][entity_id]['claims'][property_id]][0:properties_per_category]
    property_values_tuples = []

    # Search by ID the responses of the specific property only if the specific property responses names are importan
    for id in property_values:
      
      # name is no important
      if property_id in no_search_name_properties:
        property_value = {id: None}
      
      # name is important
      else:
        wikidata_response_content, wikidata_response_error = fetch_wikidata(request_action=WikidataActions.BY_ID.value, request=id).values()

        if not wikidata_response_error:
          property_value = {id: wikidata_response_content['entities'][id]['labels']['en']['value']}
        else:
          property_value = {id: None}
      
      # Append the tuple on the final response list
      property_values_tuples.append(property_value)
    
    return property_values_tuples

  except:
    property_values = None
    return property_values

def parse_specific_properties(wikidata_result, props_to_remove=["image_url"]):
    return {
        specific_properties[prop]: [list(value.keys())[0] for value in values]
        for prop, values in wikidata_result[0].items()
        if prop in specific_properties.keys() and prop not in props_to_remove and values
    }

def parse_specific_properties_to_NL(wikidata_result, props_to_remove=["image_url"], remove_nulls=True):
  nl_specific_properties_dict = {
      prop: [list(value.values())[0] for value in values]
      for prop, values in wikidata_result[0].items()
      if prop in specific_properties.keys() and prop not in props_to_remove and values
  }
  if remove_nulls:
    nl_specific_properties_dict = {key: value for key, value in nl_specific_properties_dict.items() if None not in value}

  return nl_specific_properties_dict

  # input: str, bool -> str (error) or list of dicts with response
def get_wikidata_entity_info(entity: str, properties_per_category=1, exact_result=True):
  # Fetch BY_TEXT (get ID)
  wikidata_response_content, wikidata_response_error = fetch_wikidata(request_action=WikidataActions.BY_TEXT.value, request=entity).values()

  if exact_result and len(wikidata_response_content)>1:
    wikidata_response_content = [wikidata_response_content[0]]
  
  if wikidata_response_error:
    return wikidata_response_content

  wikidata_results = []
  for response_content in wikidata_response_content:
    entity_name = response_content["display"]["label"]["value"]
    entity_id = response_content["id"]
    entity_data = {"id": entity_id, }#"image_url": get_entity_image(entity_id)}

    # Fetch BY_ID (get properties)
    wikidata_response_content, wikidata_response_error = fetch_wikidata(request_action=WikidataActions.BY_ID.value, request=entity_id).values()

    # If there is an error, append the error type
    if wikidata_response_error:
      entity_data["error"] = wikidata_response_error
      wikidata_results.append(entity_data)
      continue
    
    # Parse properties
    for general_property, general_property_name in general_properties.items():
      entity_data[general_property] = get_general_property(wikidata_response_content, entity_id, general_property_name, properties_per_category)
    for specific_property, specific_property_id in specific_properties.items():
      entity_data[specific_property] = get_specific_property(wikidata_response_content, entity_id, specific_property_id, properties_per_category)

    # Append the result to the list of results
    wikidata_results.append(entity_data)

  return wikidata_results

# Returns a json wiht the info in NL (Error: str or empty list)
def get_wikidata_entity_info_in_NL(entity: str, properties_per_category=1, exact_result=True):
  wikidata_results = get_wikidata_entity_info(entity, properties_per_category, exact_result)
  # If there is an error
  if type(wikidata_results)!=list or len(wikidata_results)==0:
    return wikidata_results
  # Else: Get properties and returns in NL
  general_properties = parse_general_properties_to_NL(wikidata_results)
  specific_properties = parse_specific_properties_to_NL(wikidata_results, props_to_remove=["image_url"])
  all_properties = general_properties.copy()
  all_properties.update(specific_properties)
  return all_properties