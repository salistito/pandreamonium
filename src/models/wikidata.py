# Define global variables

# Propiedades Generales de todo tipo de Entidad
general_properties = {
    "title": "labels",
    "description": "descriptions",
    "aliases": "aliases"
    }

# Propiedades Especificas (Decidir orden de prioridad, y cantidad de propiedades por tipo)
specific_properties = {
    "image_url": "P18",
    "instances_of": "P31",
    "part_of": "P361",
    "countries": "P17",
    "founded_by": "P112",
    "occupations": "P106",
    "sex_or_gender": "P21",
    "work_fields" :"P101",
    "awards_received": "P166",
    "countries_of_citizenship": "P27",
    "places_of_birth": "P19",
    "educated_at": "P69",

}
# Universo de propiedades
all_properties = list(specific_properties.keys()) # ["image_url", "instances_of", "part_of", "countries", "founded_by", "occupations", "sex_or_gender", "work_fields", "awards_received", "countries_of_citizenship", "places_of_birth", "educated_at"]

# Propiedades en que NO interesa conocer sus valores en lenguaje natural, pero si en IDs de Wikidata 
no_search_name_properties = ["P18", "P21", "P166", "P27", "P19", "P69"]

# Parámetros estandar para la búsqueda de entidades en wikidata:
generate_entity_data_standar_params={
        "props_to_remove": all_properties,
        "properties_per_category": 1,
        "result_limit": 3,
        "query_timeout": 15,
    }