import torch
from diffusers import StableDiffusionPipeline, PNDMScheduler, DDIMScheduler, LMSDiscreteScheduler, EulerDiscreteScheduler
from src.config import default_model_id, auth_token, nsfw_checker
from src.utils import image_grid, save_image

default_scheduler = EulerDiscreteScheduler

# 1. Load Model
def createStableDiffusionPipeline(model_id=default_model_id, model_scheduler=default_scheduler):
    # Use custome scheduler (for example Euler scheduler)
    scheduler = model_scheduler.from_pretrained(model_id, subfolder="scheduler")
    # Make sure you're logged in with `huggingface-cli login`
    # or that you have put your access token in the .env file
    stable_diffusion_pipeline = StableDiffusionPipeline.from_pretrained(
        model_id,
        scheduler=scheduler,
        revision="fp16",
        torch_dtype=torch.float16,
        use_auth_token=auth_token
    )
    # Set the device
    device = ('cuda' if torch.cuda.is_available() else 'cpu')
    # Move the pipeline to the device:
    # If the device is cuda, it's means that the GPU will be used (faster inference).
    stable_diffusion_pipeline = stable_diffusion_pipeline.to(device)
    # GPU Optimizations
    if device == 'cuda':
        stable_diffusion_pipeline.enable_xformers_memory_efficient_attention()
    return stable_diffusion_pipeline

class StableDiffusionModel:
    def __init__(self, model_id=default_model_id, model_scheduler=default_scheduler):
        self.model_id = model_id
        self.model_scheduler = model_scheduler
        self.pipeline = createStableDiffusionPipeline(model_id, model_scheduler)

    # 2. Forward embeddings and negative embeddings through text encoder
    def encode_text_embeddings(self, prompt, negative_prompt=""):
        max_length = self.pipeline.tokenizer.model_max_length

        #input_ids = self.pipeline..tokenizer(prompt, return_tensors="pt").input_ids
        input_ids = self.pipeline.tokenizer(
            prompt,
            truncation=False,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt"
        ).input_ids
        input_ids = input_ids.to("cuda")

        negative_ids = self.pipeline.tokenizer(
            negative_prompt,
            truncation=False,
            padding="max_length",
            max_length=input_ids.shape[-1],
            return_tensors="pt"
        ).input_ids
        negative_ids = negative_ids.to("cuda")

        concat_embeds = []
        neg_embeds = []
        for i in range(0, input_ids.shape[-1], max_length):
            concat_embeds.append(self.pipeline.text_encoder(input_ids[:, i: i + max_length])[0])
            neg_embeds.append(self.pipeline.text_encoder(negative_ids[:, i: i + max_length])[0])

        prompt_embeds = torch.cat(concat_embeds, dim=1)
        negative_prompt_embeds = torch.cat(neg_embeds, dim=1)

        return prompt_embeds, negative_prompt_embeds
    
    # 3. Forward:
        # How to use:
        # 1) Direct Prompt:
        # image = stable_diffusion_pipeline(prompt, num_images_per_prompt=1, guidance_scale=7.5, num_inference_steps=75, height=512, width=512).images[0] # image here is in [PIL format](https://pillow.readthedocs.io/en/stable/)
        # images = stable_diffusion_pipeline(prompt, num_images_per_prompt=1, guidance_scale=8, num_inference_steps=50).images
        # 2) Prompt Embeddings
        # prompt_embeds, negative_prompt_embeds = encode_text_embeddings(prompt)
        # image = stable_diffusion_pipeline(prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, num_images_per_prompt=1, guidance_scale=7.5, num_inference_steps=75, height=512, width=512).images[0]
        # images = stable_diffusion_pipeline(prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, num_images_per_prompt=1, guidance_scale=7.5, num_inference_steps=75, height=512, width=512).images
        
        # TODO: Maybe use this
        # generator = torch.Generator("cuda").manual_seed(1024)
        # image = pipe(prompt, guidance_scale=7.5, num_inference_steps=15, generator=generator).images[0]
    
    def txt2img(self, prompt, save=False):
        prompt_embeds, negative_prompt_embeds = self.pipeline.encode_text_embeddings(prompt)
        image = self.pipeline(
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_prompt_embeds,
            num_images_per_prompt=1,
            guidance_scale=8,
            num_inference_steps=50
        ).images[0]
        if save:
            save_image(image, prompt)
        return image

    def txt2grid(self, prompt, rows=1, cols=3, save=False):
        all_images = []
        for _ in range(rows):
            prompt_embeds, negative_prompt_embeds = self.encode_text_embeddings(prompt)
            images = self.pipeline(
                prompt_embeds=prompt_embeds,
                negative_prompt_embeds=negative_prompt_embeds,
                num_images_per_prompt=cols,
                guidance_scale=8,
                num_inference_steps=50
            ).images
            all_images.extend(images)
        grid = image_grid(all_images, rows=rows, cols=cols)
        if save:
            save_image(grid, prompt)
        return grid, all_images
    
    def enable_nsfw_checker(self):
        # Enable safety checker
        # TODO: Define custome safety_checker
        # self.pipeline.safety_checker = None
        self.pipeline.requires_safety_checker = True

    def disable_nsfw_checker(self):
        # Disable safety checker only if the configurations allow it
        if not nsfw_checker:
           # sd_pipeline.nsfw_checker = lambda images, clip_input: (images, False)
           self.pipeline.safety_checker = None
           self.pipeline.requires_safety_checker = False

    def reload(self, model_id=default_model_id, model_scheduler=default_scheduler):
        self.__init__(model_id, model_scheduler)
        self.enable_nsfw_checker() if nsfw_checker else self.disable_nsfw_checker()

    def execute(self, prompt, rows=1, cols=3, save=False):
        grid, all_images = self.txt2grid(prompt, rows, cols, save)
        return grid, all_images
