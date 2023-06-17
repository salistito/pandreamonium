import os
default_model_id = os.getenv("DEFAULT_MODEL_ID")
auth_token = os.getenv("AUTH_TOKEN")
nsfw_checker = os.getenv("NSFW_CHECKER") == "True"