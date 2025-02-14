import pandas as pd
import requests
import random
import string
from tqdm import tqdm
from dotenv import load_dotenv
import os

# Define the API endpoint
SIGNUP_URL = "http://192.168.1.18:8000/api/v1/auth/signup/"  # Change to your actual API URL
load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
if not AUTH_TOKEN:
    raise ValueError("No token found in the environment variables.")

# Function to generate a secure random password
def generate_password(length=8):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    while True:
        password = ''.join(random.choices(chars, k=length))
        if (any(c.isupper() for c in password) and  # At least one uppercase
            any(c.islower() for c in password) and  # At least one lowercase
            any(c.isdigit() for c in password) and  # At least one number
            any(c in "!@#$%^&*()-_=+" for c in password)):  # At least one special char
            return password

def bulk_signup(csv_file):
    # Read CSV file
    df = pd.read_csv(csv_file)

    # Ensure required columns exist
    required_columns = {"first_name", "last_name", "email"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_columns}")

    # Generate passwords for users
    df["password"] = df.apply(lambda _: generate_password(10), axis=1)  # Generating 10-char passwords

    # Save the updated CSV with passwords
    updated_csv_file = "updated_" + csv_file
    df.to_csv(updated_csv_file, index=False)
    print(f"Updated CSV with passwords saved as: {updated_csv_file}")

    # Set authorization headers
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    # Iterate over each row and send signup request
    success_count = 0
    failed_count = 0

    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Signups"):
        payload = {
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "email": row["email"],
            "password": row["password"]
        }

        response = requests.post(SIGNUP_URL, json=payload, headers=headers)

        if response.status_code == 201:  # Adjust based on your API response
            success_count += 1
        else:
            failed_count += 1
            print(f"Failed: {row['email']} - {response.status_code} - {response.text}")

    print(f"Signup Completed: {success_count} Success, {failed_count} Failed")

# Usage example:
bulk_signup("GE103_students.csv")  # Provide the correct CSV file path