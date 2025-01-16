import pandas as pd
import os
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
import logging
import json
import argparse

from load_data import load_texts
from annotator import summarize_with_mistral, annotate_with_mistral
from annotator import summarize_with_gemeni, annotate_with_gemeni, rate_with_gemeni
from parse_LLM_output import process_json_answer

load_dotenv()


parser = argparse.ArgumentParser()
parser.add_argument('--export', action='store_true', help="Skip csv creation, just export the existing one.")
parser.add_argument('--delay', type=int, help="Set the delay time in seconds.", default=6)
args = parser.parse_args()

delay = args.delay

column_names = ['full text', 'summary', 'LLM json', 'LLM summary json', 'score_reason', 'score', 'model', 'time']
output_file = "gliner.json"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a console handler and set the level to DEBUG
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)



def save_data_to_file(data, filepath):
    """Saves the processed data to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_texts_to_table(file_path = 'texts.csv'):
    # Check if the file exists
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
    else:
        existing_df = pd.DataFrame(columns=column_names)

    new_texts = (load_texts('data/2023.json'))

    # Filter out texts that are already in the DataFrame
    new_texts_to_add = [text for text in new_texts if text not in existing_df['full text'].values]

    # Create a DataFrame from the new texts to add
    new_df = pd.DataFrame({'full text': new_texts_to_add})

    # Append the new DataFrame to the existing DataFrame
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)

    # Save the updated DataFrame back to the CSV file
    updated_df.to_csv(file_path, index=False)


def fill_table(file_path='texts.csv'):
    df = pd.read_csv(file_path).astype(str)

    for index, row in df.iterrows():
        if (df.at[index, 'score_reason'] == 'nan'):
            score = rate_with_gemeni(df.at[index, 'full text'])
            score = json.loads(score)

            df.at[index, 'score_reason'] = score['reasoning_behind_score']
            df.at[index, 'score'] = score['score']
            sleep(delay)

        if (df.at[index, 'summary'] == 'nan'):
            # df.at[index, 'summary'] = summarize_with_mistral(df.at[index, 'full text'])
            df.at[index, 'summary'] = summarize_with_gemeni(df.at[index, 'full text'])
            logger.debug(df.at[index, 'summary'])
            sleep(delay)
        if (df.at[index, 'LLM json'] == 'nan'):
            # df.at[index, 'LLM json'] = annotate_with_mistral(df.at[index, 'full text'])
            df.at[index, 'LLM json'] = annotate_with_gemeni(df.at[index, 'full text'])
            sleep(delay)
        if (df.at[index, 'LLM summary json'] == 'nan'):
            # df.at[index, 'LLM summary json'] = annotate_with_mistral(df.at[index, 'summary'])
            df.at[index, 'LLM summary json'] = annotate_with_gemeni(df.at[index, 'summary'])
            sleep(delay)
        
        # add info about model and time
        if (df.at[index, 'model'] == 'nan'):
            # df.at[index, 'model'] = os.environ["MODEL"]
            df.at[index, 'model'] = os.environ["GOOGLE_MODEL"]
        if (df.at[index, 'time'] == 'nan'): 
            df.at[index, 'time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.to_csv('texts.csv', index=False)
            logger.info(f"Row number {index} processed...")
        # break


if not args.export:
    # создает таблицу с текстами, или добавлет те которых нет
    add_texts_to_table()
    logger.info("CSV file created...")
    while True: 
        try:
            fill_table()
        except Exception as e:
            logger.info(f"Got Exception: {e}")
        
df = pd.read_csv('texts.csv')

df.replace(['nan', 'NaN'], pd.NA, inplace=True)
df = df.dropna(how='any')
processed_output = []
for index, text in enumerate(df['LLM json']):
    result = (process_json_answer(text))
    if result:
        processed_output += result
    else:
        logger.error(f"Error processing text: {text} in row {index}")
for index, text in enumerate(df['LLM summary json']):
    result = (process_json_answer(text))
    if result:
        processed_output += result
    else:
        logger.error(f"Error processing summary text: {text} in row {index}")

save_data_to_file(processed_output, output_file)
logger.info(f"Saved data to {output_file}. Total rows: {len(processed_output)}, Full text rows: {len(processed_output) / 2}")