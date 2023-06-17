import gradio as gr
from src.models import *
from src.pipelines.words_cloud import *
from src.pipelines.key_concepts import *
from src.pipelines.ner_and_nel import *
from src.pipelines.stable_diffusion import *

def gradio_wrapper_word_cloud_pipeline(text):
  if not text:
    raise gr.Error(pandreamonium_texts['no_text_error'])
  word_cloud, lemmatized_word_cloud, filtered_text_lemmas_top_words = word_cloud_pipeline(text, verbose=False)
  top_words_html = generate_html_list(pandreamonium_texts['word_cloud_top_words_label'].format(len(filtered_text_lemmas_top_words)), filtered_text_lemmas_top_words)
  return word_cloud, top_words_html

# Interface Labels and Examples:
word_cloud_pipeline_title=pandreamonium_texts['word_cloud_pipeline_title']
word_cloud_pipeline_description=pandreamonium_texts['word_cloud_pipeline_description']

# Reset Func
def word_cloud_pipeline_reset_btn_fn(*args):
    return [None for _ in args]

def gradio_wrapper_key_concepts_pipeline(text, max_extract_length, n_key_concepts):
  # Lenght Conditions
  len_text = len(text)
  max_extract_length = int(max_extract_length)# if len_text > int(max_extract_length)*4 else 
  n_key_concepts = int(n_key_concepts)
  # Translated Extracts
  english_extracts = get_translated_extracts(text, max_extract_length=max_extract_length, source="es", target="en", verbose=False)
  # Extract Key Concepts (Extractos en ingles e, internamente, la union de ellos -> texto original completo en ingles -> 1°)
  english_consolidated_key_concepts, spanish_consolidated_key_concepts = key_concepts_extractor(english_extracts, n=n_key_concepts, verbose=False)
  consolidated_key_concepts =  english_consolidated_key_concepts if False else spanish_consolidated_key_concepts  # Quizás dar a elegir que spacy model usar
  consolidated_key_concepts_html = generate_html_list(pandreamonium_texts['key_concepts_label'], consolidated_key_concepts)
  return consolidated_key_concepts_html

# Interface Labels and Examples:
key_concepts_pipeline_title=pandreamonium_texts['key_concepts_pipeline_title']
key_concepts_pipeline_description=pandreamonium_texts['key_concepts_pipeline_description']
max_extract_length_default = 100
n_key_concepts_default = 15

# Reset Func
def key_concepts_pipeline_reset_btn_fn(text, max_extract_length, n_key_concepts, key_concepts):
    return None, max_extract_length_default, n_key_concepts_default, None

properties_names = pandreamonium_texts['ner_pipeline_properties_names']
properties_names_list = list(properties_names.keys()) #['Instances of', 'Part of', 'Countries', 'Founded by', 'Occupations', 'Sex or Gender', 'Fields of Work', 'Awards Received', 'Countries of Citizenship', 'Places of Birth', 'Places of Education']
selected_props_default = [properties_names_list[0]] # ['Instances of'] or ['Instancias de']
ner_pipeline_html_headers = pandreamonium_texts['ner_pipeline_html_headers']

def gradio_wrapper_ner_pipeline(text, selected_props, properties_per_category, result_limit, query_timeout, max_extract_length=100, n_key_concepts=15):
  # User generate entity data params
  translated_selected_props = [properties_names[prop] for prop in selected_props]
  user_generate_entity_data_params = {
      "props_to_remove": [prop for prop in all_properties if (prop=="image_url") or (prop not in translated_selected_props)],
      "properties_per_category": int(properties_per_category),
      "result_limit": int(result_limit),
      "query_tiemout": int(query_timeout),
  }

  # TODO: Detect execution language
  source_language = "es" if True else "en"
  
  # Summarize Pipeline
  english_extracts, english_extracts_summaries, spanish_extracts_summaries = summarize_pipeline(text, max_extract_length=max_extract_length, verbose=False)
  # Select right summaries
  ner_extracts_summaries = english_extracts_summaries

  # Consolidated Key Concepts (Again)
  #----------------------------------
  # Translated Extracts
  english_extracts = get_translated_extracts(text, max_extract_length=max_extract_length, source=source_language, target="en", verbose=False)
  # Extract Key Concepts (Extractos en ingles e, internamente, la union de ellos -> texto original completo en ingles -> 1°)
  english_consolidated_key_concepts, spanish_consolidated_key_concepts = key_concepts_extractor(english_extracts, n=n_key_concepts, verbose=True)
  # Select right consolidated key concepts
  consolidated_key_concepts = spanish_consolidated_key_concepts if source_language == "es" else english_consolidated_key_concepts
  #----------------------------------
  
  # Detect Entities
  complete_text_entities, extracts_entities, consolidated_entities = ner_pipeline(es_nlp, text, ner_extracts_summaries, user_generate_entity_data_params, verbose=False)

  # Consolidate entities with key concepts
  #consolidated_key_concepts_and_no_processed_entities = consolidate_key_concepts_and_no_processed_entities(consolidated_key_concepts, extracts_entities)
  consolidated_key_concepts_and_no_processed_entities = consolidate_key_concepts_and_no_processed_entities(consolidated_key_concepts, complete_text_entities)

  return generate_entities_html(consolidated_key_concepts_and_no_processed_entities, ner_pipeline_html_headers), ner_extracts_summaries

# 
# Interface Labels and Examples:
ner_pipeline_title=pandreamonium_texts['ner_pipeline_title']
ner_pipeline_description=pandreamonium_texts['ner_pipeline_description']
properties_per_category_default = "1"
result_limit_default = "3"
query_timeout_default = 15

# Reset Func
def ner_pipeline_reset_btn_fn(text, selected_props, properties_per_category, result_limit, query_timeout, entities_html, ner_extracts_summaries):
    return None, selected_props_default, properties_per_category_default, result_limit_default, query_timeout_default, None, None

# Update extracts summaries value
def update_extracts_summaries(extracts_summaries):
    print("UPDATED TO:", extracts_summaries)
    return extracts_summaries

# Reset extracts summaries value
def reset_extracts_summaries(extracts_summaries):
    print(extracts_summaries, "RESTED TO: None")
    return None


import random

def gradio_wrapper_stable_diffusion_pipeline(text, prompt_style, custome_prompt_style, n_rows=1, n_cols=3, ner_extracts_summaries=[], max_extract_length=100):
  prompt_engineering_styles = {
      "Fantasy": "fantasy art, landscape art, environment art, in the style of greg rutkowski, illustration, epic, fantasy, artstation, trending in artstation.",
      "Realistic": "Hyperrealistic image, stunning 3 d render, unreal engine, perfect symmetry, dim volumetric cinematic lighting, 8 k octane comprehensive render, extremely hyper - detailed, incredibly lifelike attributes, real flesh texture, masterpiece, artstation, stunning", # hyper-realistic, still-life, textured
      "Epic": "fantasy art, landscape art, environment art, in the style of greg rutkowski, illustration, epic, fantasy, artstation, trending in artstation.",
  }
  # Get prompt engineering styles
  try:
    prompt_engineering_style = prompt_engineering_styles[prompt_style]
  except:
    if prompt_style=="Random":
      prompt_engineering_style = random.choice(list(prompt_engineering_styles.values()))
    elif prompt_style=="Custome":
      prompt_engineering_style = custome_prompt_style
  # NER stage has been executed or SD update ner_extracts_summaries
  if ner_extracts_summaries and ner_extracts_summaries!=[['']]:
    sd_extracts_summaries = ["".join(extract) for extract in ner_extracts_summaries]

  # If NER stage has not been executed and there are no summarized extracts
  else:
    print("Volviendo a calcular extract_summaries (No habían)")
    # Get extracts summaries
    # Summarize Pipeline
    english_extracts, english_extracts_summaries, spanish_extracts_summaries = summarize_pipeline(text, max_extract_length=max_extract_length, verbose=False)
    # Select english_extracts_summaries because stable diffusion works better on english
    sd_extracts_summaries = english_extracts_summaries

  images_story_line, consolidated_translated_extracts = stable_diffusion_dream(sd_extracts_summaries, prompt_engineering_style, consolidate_extracts=False, rows=int(n_rows), cols=int(n_cols), verbose=True)
  return images_story_line, sd_extracts_summaries

# Interface Labels and Examples:
stable_diffusion_pipeline_title=pandreamonium_texts['stable_diffusion_pipeline_title']
stable_diffusion_pipeline_description=pandreamonium_texts['stable_diffusion_pipeline_description']
prompt_style_default = "Random"
n_rows_default = "1"
n_cols_default = "3"

# Reset Func
def stable_diffusion_pipeline_reset_btn_fn(text, prompt_style, custome_prompt_style, n_rows, n_cols, images_story_line, sd_extracts_summaries):
    return None, prompt_style_default, None, n_rows_default, n_cols_default, None, None


def prompt_style_listener(choice):
    if choice == "Custome":
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)
    



pandreamonium_title = pandreamonium_texts['pandreamonium_title']
pandreamonium_description = pandreamonium_texts['pandreamonium_description']

with gr.Blocks() as pandreamonium_demo:
    gr.Markdown(generate_pipeline_title_and_description(pandreamonium_title, pandreamonium_description))
    text = gr.Textbox(label=pandreamonium_texts['text_label'], info=pandreamonium_texts['text_info'], lines=5, max_lines=100, placeholder=pandreamonium_texts['text_placeholder'])
    
    # Word Cloud: Quizás agregar la opción de generar más nubes con lemmas y sin lemmas
    with gr.Tab(word_cloud_pipeline_title):
        gr.Markdown(generate_pipeline_title_and_description(word_cloud_pipeline_title, word_cloud_pipeline_description))
        with gr.Row():
            with gr.Column():
                #text = gr.Textbox(label=pandreamonium_texts['text_label'], info=pandreamonium_texts['text_info'], lines=5, max_lines=100, placeholder=pandreamonium_texts['text_placeholder'])
                with gr.Row():
                    reset_btn = gr.Button(value=pandreamonium_texts['reset_btn_value'])
                    submit_btn = gr.Button(value=pandreamonium_texts['submit_btn_value'], variant="primary")
                    cancel_btn = gr.Button(value=pandreamonium_texts['cancel_btn_value'])
            with gr.Column():
                word_cloud =  gr.Image(label=pandreamonium_texts['word_cloud_image_label'], interactive=False)
                text_top_n_words = gr.HTML()

        inputs = [text]
        outputs = [word_cloud, text_top_n_words]
        reset_btn_items = inputs + outputs

        reset_btn.click(fn=word_cloud_pipeline_reset_btn_fn, inputs=reset_btn_items, outputs=reset_btn_items)
        submit_click_event = submit_btn.click(gradio_wrapper_word_cloud_pipeline, inputs=inputs, outputs=outputs, api_name="word_cloud_pipeline")
        cancel_btn.click(fn=None, inputs=None, outputs=None, cancels=[submit_click_event])
        
        examples = gr.Dataset(samples=gradio_examples, components=[text], type="index")
        examples.click(load_example, inputs=[examples], outputs=[text])

    # Key Concepts
    with gr.Tab(key_concepts_pipeline_title):
        gr.Markdown(generate_pipeline_title_and_description(key_concepts_pipeline_title, key_concepts_pipeline_description))
        with gr.Row():
            with gr.Column():
                #text = gr.Textbox(label=pandreamonium_texts['text_label'], info=pandreamonium_texts['text_info'], lines=5, max_lines=100, placeholder=pandreamonium_texts['text_placeholder'])
                max_extract_length = gr.Slider(minimum=1, maximum=150, value=max_extract_length_default, step=1, label=pandreamonium_texts['max_extract_length_label'], info=pandreamonium_texts['max_extract_length_info'])
                n_key_concepts = gr.Slider(minimum=1, maximum=15, value=n_key_concepts_default, step=1, label=pandreamonium_texts['n_key_concepts_label'], info=pandreamonium_texts['n_key_concepts_info'])
                with gr.Row():
                    reset_btn = gr.Button(value=pandreamonium_texts['reset_btn_value'])
                    submit_btn = gr.Button(value=pandreamonium_texts['submit_btn_value'], variant="primary")
                    cancel_btn = gr.Button(value=pandreamonium_texts['cancel_btn_value'])
            with gr.Column():
                key_concepts = gr.HTML()

        inputs = [text, max_extract_length, n_key_concepts]
        outputs = [key_concepts]
        reset_btn_items = inputs + outputs

        reset_btn.click(fn=key_concepts_pipeline_reset_btn_fn, inputs=reset_btn_items, outputs=reset_btn_items)
        submit_click_event = submit_btn.click(gradio_wrapper_key_concepts_pipeline, inputs=inputs, outputs=outputs, api_name="key_concepts_pipeline")
        cancel_btn.click(fn=None, inputs=None, outputs=None, cancels=[submit_click_event])
        
        examples = gr.Dataset(samples=gradio_examples, components=[text], type="index")
        examples.click(load_example, inputs=[examples], outputs=[text])

    # NER
    with gr.Tab(ner_pipeline_title):
        gr.Markdown(generate_pipeline_title_and_description(ner_pipeline_title, ner_pipeline_description))
        with gr.Row():
            with gr.Column():
                #text = gr.Textbox(label=pandreamonium_texts['text_label'], info=pandreamonium_texts['text_info'], lines=5, max_lines=100, placeholder=pandreamonium_texts['text_placeholder'])
                selected_props = gr.CheckboxGroup(choices=properties_names_list, value=selected_props_default, label=pandreamonium_texts['selected_props_label'], info=pandreamonium_texts['selected_props_info'])
                properties_per_category = gr.Radio(choices=["1", "2", "3"], value=properties_per_category_default, label=pandreamonium_texts['properties_per_category_label'], info=pandreamonium_texts['properties_per_category_info'])
                result_limit = gr.Radio(choices=["1", "2", "3", "4", "5"], value=result_limit_default, label=pandreamonium_texts['result_limit_label'], info=pandreamonium_texts['result_limit_info'])
                query_timeout = gr.Slider(minimum=15, maximum=60, value=query_timeout_default, step=1, label=pandreamonium_texts['query_timeout_label'], info=pandreamonium_texts['query_timeout_info'])
                with gr.Row():
                    reset_btn = gr.Button(value=pandreamonium_texts['reset_btn_value'])
                    submit_btn = gr.Button(value=pandreamonium_texts['submit_btn_value'], variant="primary")
                    cancel_btn = gr.Button(value=pandreamonium_texts['cancel_btn_value'])
            with gr.Column():
                entities_html = gr.HTML()
                ner_extracts_summaries = gr.Dataframe(type="array", col_count=1, interactive=False, visible=False)


        inputs = [text, selected_props, properties_per_category, result_limit, query_timeout]
        outputs = [entities_html, ner_extracts_summaries]
        reset_btn_items = inputs + outputs

        reset_btn.click(fn=ner_pipeline_reset_btn_fn, inputs=reset_btn_items, outputs=reset_btn_items)
        submit_click_event = submit_btn.click(gradio_wrapper_ner_pipeline, inputs=inputs, outputs=outputs, api_name="ner_pipeline")
        cancel_btn.click(fn=None, inputs=None, outputs=None, cancels=[submit_click_event])
        
        examples = gr.Dataset(samples=gradio_examples, components=[text], type="index")
        examples.click(load_example, inputs=[examples], outputs=[text])

    # Stable Diffusion
    with gr.Tab(stable_diffusion_pipeline_title):
        gr.Markdown(generate_pipeline_title_and_description(stable_diffusion_pipeline_title, stable_diffusion_pipeline_description))
        with gr.Row():
            with gr.Column():
                #text = gr.Textbox(label=pandreamonium_texts['text_label'], info=pandreamonium_texts['text_info'], lines=5, max_lines=100, placeholder=pandreamonium_texts['text_placeholder'])
                #ner_extracts_summaries=gr.Textbox()
                prompt_style = gr.Radio(choices=["Fantasy", "Realistic", "Epic", "Random", "Custome"], value=prompt_style_default, label=pandreamonium_texts['prompt_style_label'], info=pandreamonium_texts['prompt_style_info'])
                with gr.Row(visible=False) as customePromptStyleRow:
                    custome_prompt_style = gr.Textbox(label=pandreamonium_texts['custome_prompt_style_label'], info=pandreamonium_texts['custome_prompt_style_info'], lines=3, max_lines=10, placeholder=pandreamonium_texts['custome_prompt_style_placeholder'])  
                n_rows = gr.Radio(choices=["1", "2", "3", "4", "5"], value=n_rows_default, label=pandreamonium_texts['n_rows_label'], info=pandreamonium_texts['n_rows_info'])
                n_cols = gr.Radio(choices=["1", "2", "3", "4", "5"], value=n_cols_default, label=pandreamonium_texts['n_cols_label'], info=pandreamonium_texts['n_cols_info'])
                with gr.Row():
                    reset_btn = gr.Button(value=pandreamonium_texts['reset_btn_value'])
                    submit_btn = gr.Button(value=pandreamonium_texts['submit_btn_value'], variant="primary")
                    cancel_btn = gr.Button(value=pandreamonium_texts['cancel_btn_value'])
            with gr.Column():
                    images_story_line = gr.Gallery(label=pandreamonium_texts['stable_diffusion_images_label']).style(columns=[3], height='auto', object_fit="contain") # [n_cols.value]
                    sd_extracts_summaries = gr.Dataframe(type="array", col_count=1, interactive=False, visible=False)
        
        inputs = [text, prompt_style, custome_prompt_style, n_rows, n_cols, ner_extracts_summaries]
        outputs = [images_story_line, sd_extracts_summaries]
        reset_btn_items = [text, prompt_style, custome_prompt_style, n_rows, n_cols] + outputs

        prompt_style.change(prompt_style_listener, [prompt_style], [customePromptStyleRow]) # Open a textbox for custome prompt style
        sd_extracts_summaries.change(fn=update_extracts_summaries, inputs=[sd_extracts_summaries], outputs=[ner_extracts_summaries])
        text.change(fn=reset_extracts_summaries, inputs=[ner_extracts_summaries], outputs=[ner_extracts_summaries])

        reset_btn.click(fn=stable_diffusion_pipeline_reset_btn_fn, inputs=reset_btn_items, outputs=reset_btn_items)
        submit_click_event = submit_btn.click(gradio_wrapper_stable_diffusion_pipeline, inputs=inputs, outputs=outputs, api_name="stable_diffusion_pipeline")
        cancel_btn.click(fn=None, inputs=None, outputs=None, cancels=[submit_click_event])
        
        examples = gr.Dataset(samples=gradio_examples, components=[text], type="index")
        examples.click(load_example, inputs=[examples], outputs=[text])

pandreamonium_demo.queue()               
pandreamonium_demo.launch(share=True, inline=True, debug=True, show_error=True)
#pandreamonium_demo.launch(inline=True, debug=True, show_error=True)