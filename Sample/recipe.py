import pandas as pd
import fitz
import re
import nltk
from nltk.corpus import stopwords
import subprocess

# Function to use Ollama to search for recipes with specified ingredients
def search_recipes(ingredients):
    # Create a prompt for Ollama
    prompt = f"""
    hi. Generate me 3 edible recipes using some or all of these ingredients in pretty significant amounts. The ingredients are {', '.join(ingredients)}."""
    
    # Run Ollama command in CLI with the prompt as input
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],  # replace llama3.2 with the actual model you are using
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
            encoding='utf-8'
        )
        # Return the output of the Ollama command
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print("Error while calling Ollama:", e)
        return None

pdf_file_path = './Medical Reports/Medical Report 5.pdf'

with fitz.open(pdf_file_path) as pdf:
    text = ''
    for page in pdf:
        text += page.get_text()
text = text.lower()
text = re.sub(r'[^a-z\s]', '', text)
text = re.sub(r'\s+', ' ', text).strip()

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
text = ' '.join([word for word in text.split() if word not in stop_words])

file_path = "./Disease_Ingredients.csv"
try:
    df = pd.read_csv(file_path, encoding='ISO-8859-1')
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding='latin1')
df['Disease Name'] = df['Disease Name'].str.strip().str.lower()
diseases = df['Disease Name'].unique()
mentioned_diseases = []

for disease in diseases:
    if disease.lower() in text.lower():
        mentioned_diseases.append(disease)

#print("Mentioned Diseases/Deficiencies:", mentioned_diseases)

for disease in mentioned_diseases:
    filtered_df = df[df['Disease Name'] == disease.strip().lower()]

    counter = 1

    for index, row in filtered_df.iterrows():
        ingredients = row['Recommended Intake to Improve Deficiency']
        ingredients_list = ingredients.split(", ")

        if len(ingredients_list) == 4:
            ingredients = list(set(ingredients_list))
            print(f"{disease} : {ingredients}\n")
            recipes = search_recipes(ingredients)

            # Display the recipes if found
            if recipes:
                print("Recipes found:")
                print(recipes)
            else:
                print("No recipes found or there was an error.")