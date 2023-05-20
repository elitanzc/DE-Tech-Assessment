# Standard library imports
from datetime import datetime
import hashlib
import logging
import os
import re

# 3rd library imports
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pandas as pd


RAW_DATASETS_PATH = os.path.abspath("../raw-datasets")
PROCESSED_DATASETS_PATH = os.path.abspath("../processed-datasets")
FAULTY_DATASETS_PATH = os.path.abspath("../faulty-datasets")
MOBILE_NUMBER_LENGTH = 8

logger = logging.getLogger()


def reformat_date_of_birth(date_of_birth):
    year, month, day = None, None, None
    try:
        if re.match(r"\d\d\d\d[-/](0[1-9]|1[012])[-/]\d\d", date_of_birth):
            # case 1: YYYY[-/]MM[-/]DD
            year, month, day = re.split(r"-|/", date_of_birth)
        elif re.match(r"\d\d-(0[1-9]|1[012])-\d\d\d\d", date_of_birth):
            # case 2: DD-MM-YYY
            day, month, year = date_of_birth.split("-")
        elif re.match(r"(0[1-9]|1[012])/\d\d/\d\d\d\d", date_of_birth):
            # case 2: MM/DD/YYY
            month, day, year = date_of_birth.split("/")
        else:
            raise Exception("date format not one of: YYYY/MM/DD, YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY")
    except Exception as e:
        logger.error(f"An error occured when processing the date_of_birth {date_of_birth}: {e}")
        raise
    else:
        return f"{year}{month}{day}"

def is_valid_mobile(mobile_no):
    return len(mobile_no) == MOBILE_NUMBER_LENGTH

def is_valid_email(email):
    if re.match(r"[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.(?:com|net)$", email):
        return True
    else:
        return False
    
def process_name(name):
    # remove salutations and other titles
    return " ".join(re.findall(r"\b(?!Miss)[A-Z][a-z]*[a-z](?!\.)\b", name))
    
def get_membership_id(last_name, date_of_birth):
    hashed_dof = hashlib.sha256(date_of_birth.encode('utf-8')).hexdigest()[:5]
    return f"{last_name}_{hashed_dof}"


# Main function to process datasets
def _process_applications():
    # Ingest raw csv from raw-datasets folder
    filenames = os.listdir(RAW_DATASETS_PATH)
    try:
        df = pd.concat(
            [pd.read_csv(f"{RAW_DATASETS_PATH}/{filename}") for filename in filenames], 
            ignore_index=True
        )
    except Exception as e:
        logger.error(f"Error reading csv files from {filenames}: {e}")
        raise
    
    df_invalid = pd.DataFrame()

    # Process `birthday` field
    df['date_of_birth'] = df['date_of_birth'].apply(reformat_date_of_birth)
    # Add `above_18` field (>18 yrs old on 1 jan 2022 ==> born on/before 1 jan 2004)
    df['above_18'] = df.apply(
        lambda row: row['date_of_birth'] <= "20040101", 
        axis=1
    )

    # Validity checks
    is_valid = df.apply(lambda row: 
                            row['above_18'] 
                            & is_valid_mobile(row['mobile_no']) 
                            & is_valid_email(row['email'])
                            & (row['name'] != None),
                        axis=1)
    df_invalid = df.loc[~is_valid]
    df = df.loc[is_valid]

    # Process `name` field for valid df
    df['name'] = df['name'].apply(process_name)
    df['first_name'], df['last_name'] = zip(*df['name'].apply(lambda name: name.split(" ")))
    # Add `membershipID` field for valid df
    df['membership_id'] = df.apply(lambda row: get_membership_id(row['last_name'], row['date_of_birth']), 
                                   axis=1)

    # Write to destination folders as csv
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    try:
        df.to_csv(f"{PROCESSED_DATASETS_PATH}/{timestamp}-applications_dataset.csv", index=False)
        df_invalid.to_csv(f"{FAULTY_DATASETS_PATH}/{timestamp}-applications_dataset.csv", index=False)
    except Exception as e:
        logger.error(f"Error writing files to destination folders: {e}")


# Scheduling
dag = DAG(
    dag_id="schedule",
    start_date=datetime(2023, 5, 10),
    schedule='0 * * * *'
)

fetch_events = BashOperator(
    task_id="pull_applications",
    bash_command=(
        f"curl -o {RAW_DATASETS_PATH}/applications_dataset_1.csv "
        "https://raw.githubusercontent.com/ameeraadam/DETechAssessment-23/main/applications_dataset_1.csv && "
        f"curl -o {RAW_DATASETS_PATH}/applications_dataset_2.csv "
        "https://raw.githubusercontent.com/ameeraadam/DETechAssessment-23/main/applications_dataset_2.csv"
    ),
    dag=dag
)

process_applications = PythonOperator(
    task_id="process_applications",
    python_callable=_process_applications,
    dag=dag
)

fetch_events >> process_applications