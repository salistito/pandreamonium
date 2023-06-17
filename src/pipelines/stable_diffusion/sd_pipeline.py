import textwrap
from src.pipelines.key_concepts.key_concepts_extractor import summarize
from src.models import StableDiffusionModel
model_id="runwayml/stable-diffusion-v1-5"
sd_model = StableDiffusionModel(model_id)
sd_model.disable_nsfw_checker()

def print_stable_diffusion_dream(extracts, consolidated_extract):
  print()
  for index, extract in enumerate(extracts):
    print('--------------------------------------------------------------------')
    print(f"extract_{index+1}:")
    print(textwrap.fill(extract, 150))
  print('--------------------------------------------------------------------')
  
  print()
  print('--------------------------------------------------------------------')
  print("consolidated_extract:")
  print(textwrap.fill(consolidated_extract, 150))
  print('--------------------------------------------------------------------')

def stable_diffusion_dream(extracts_summaries, prompt_engineering_style, consolidate_extracts=False, rows=1, cols=3, verbose=False):
  images_story_line = []
  consolidated_translated_extracts = []
  if consolidate_extracts and len(extracts_summaries)>2:
    for extract1, extract2 in zip(extracts_summaries, extracts_summaries[1:]):
      consolidated_extract, consolidated_translated_extract = summarize(extract1 + " " + extract2)#, max_length=44, min_length=20)
      #consolidated_extract = consolidated_extract.replace(",","").replace(".","")
      consolidated_translated_extracts.append(consolidated_translated_extract)
      if verbose:
        print_stable_diffusion_dream(extracts=[extract1, extract2], consolidated_extract=consolidated_extract)

      stable_diffusion_prompt = consolidated_extract + ' ' + prompt_engineering_style
      #image_grid, images_list = txt2grid(stable_diffusion_prompt, rows=rows, cols=cols)
      image_grid, images_list = sd_model.txt2grid(stable_diffusion_prompt, rows=rows, cols=cols)
      images_story_line.extend(images_list)
      #display(image_grid)
  else:
    for extract in extracts_summaries:
      consolidated_extract = extract
      #consolidated_extract, consolidated_translated_extract = summarize(extract)#, max_length=44, min_length=20)
      #consolidated_extract = consolidated_extract.replace(",","").replace(".","")
      #consolidated_translated_extracts.append(consolidated_translated_extract)
      if verbose:
        print_stable_diffusion_dream(extracts=[extract], consolidated_extract=consolidated_extract)

      stable_diffusion_prompt = consolidated_extract + ' ' + prompt_engineering_style
      #image_grid, images_list = txt2grid(stable_diffusion_prompt, rows=rows, cols=cols)
      image_grid, images_list = sd_model.txt2grid(stable_diffusion_prompt, rows=rows, cols=cols)
      images_story_line.extend(images_list)
      #display(image_grid)

  return images_story_line, consolidated_translated_extracts