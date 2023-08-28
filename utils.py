import os
import sys
import requests
from zipfile import ZipFile


def replace_non_question(x):
    if str(x).endswith('?'):
        return str(x)
    else:
        return ""


def download_unzip_from_google_drive(id_, destination):
    URL = "https://docs.google.com/uc?export=download&confirm=1"
    temp = "file.zip"

    session = requests.Session()

    response = session.get(URL, params={"id": id_}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": id_, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, temp)
    with ZipFile(temp, 'r') as zObject:
        zObject.extractall(path=destination)
    os.remove(temp)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)