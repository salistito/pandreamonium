# pandreamonium

# Setup
- C:/ProgramData/anaconda3/Scripts/activate
- conda env create -f environment.yaml
- conda activate pandreamonium_app
- pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
- python -m spacy download es_core_news_lg
- python -m spacy download en_core_web_sm  # KeyphraseVectorizer dependency
- #python -m spacy download en_core_web_lg