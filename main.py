from src.config import default_model_id
from src.models import StableDiffusionModel

sd_model = StableDiffusionModel(model_id=default_model_id)
# TODO: Test nsfw protection
sd_model.disable_nsfw_checker()

prompt_example = ""
sd_model.execute(prompt_example, rows=1, cols=3, save=True)