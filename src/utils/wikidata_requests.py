import enum
import requests

class WikidataActions(enum.Enum):
  BY_TEXT = 'wbsearchentities'
  BY_ID = 'wbgetentities'


def response_wrapper(response_content, response_error):
  return dict(response_content=response_content, response_error=response_error)


def requests_func(request_url, request_params, timeout=15):
  try:
    response = requests.get(url=request_url, params=request_params, timeout=timeout)
    response.raise_for_status()
    if response.status_code == 200:  # Successful request
      return response_wrapper(response_content=response, response_error=False)
    else:  # Request status code is not 200
      return response_wrapper(response_content='There was an error on Wikidata API request, request status code is not 200', response_error=False)
  except requests.exceptions.HTTPError as e:  # catch http errors
      return response_wrapper(response_content=f'There was an error on Wikidata API request, HTTP error: {e}', response_error=False)
  except requests.exceptions.RequestException as e:  # catch requests exceptions
      return response_wrapper(response_content=f'There was an error on Wikidata API request, request exception: {e}', response_error=False)


def parse_wikidata_wrapped_response(wrapped_response, parser_action):
  response_content, response_error = wrapped_response.values()
  if response_error:
    return wrapped_response
  else: # not response_error
    try:
      # transform response to JSON
      result = response_content.json()
      # Get the search result if action is "BY_TEXT"
      if parser_action == WikidataActions.BY_TEXT.value:
        result = result['search']
      return response_wrapper(response_content=result, response_error=False)
    except:
      return response_wrapper(response_content='There was an error on Wikidata API response, response has a invalid format' , response_error=True)


def fetch_wikidata(request_action, request):
    url = 'https://www.wikidata.org/w/api.php'
    wikidata_action = WikidataActions(request_action).value

    if wikidata_action == WikidataActions.BY_TEXT.value:
      params = {
        'action': f'{wikidata_action}',
        'search': request,
        'format': 'json',
        'language': 'es',
      }

    else:
      params = {
        'action': f'{wikidata_action}',
        'ids': request,
        'format': 'json',
        'language': 'es',
      }

    wrapped_response = requests_func(request_url=url, request_params=params)
    parsed_response = parse_wikidata_wrapped_response(wrapped_response=wrapped_response, parser_action=request_action)
    return parsed_response