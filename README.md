# pandreamonium

# Setup
Create requirements.txt from pip:
- pip freeze > all_requirements.txt

Activate conda base:
- C:/ProgramData/anaconda3/Scripts/activate

Create conda env:
- conda env create -f environment.yaml

Activate new conda env:
- conda activate pandreamonium_app

Install Pytorch:
- pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

Download Spacy models:
- python -m spacy download es_core_news_lg
- python -m spacy download en_core_web_sm  # KeyphraseVectorizer dependency
- python -m spacy download en_core_web_lg  # This is no used