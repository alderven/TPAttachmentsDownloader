import os
import sys
import shutil
import argparse
import requests
import warnings
from requests.auth import HTTPBasicAuth

warnings.filterwarnings('ignore')


def main(login, password, bug_id):
    """ TargetProcess Attachments downloader
    :param login: TP Login
    :param password: TP Password
    :param bug_id: Bug Id """

    # 1. Get list of attachments
    r = requests.get(f'https://cloudpoint.tpondemand.com/api/v2/attachments?where=(general.id={bug_id})', verify=False, auth=HTTPBasicAuth(login, password), params={'format': 'json', 'take': 1000})
    if r.status_code == 401:
        print(f'Unable to authorize with provided credentials. Response code: "{r.status_code}". Response body: "{r.text}"')
        return

    # 2. Check if attachments exist
    items = r.json()['items']
    if not items:
        print(f'Attachments not found for Id: "{bug_id}"')
        return

    # 3. Create output folder
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    output_dir = os.path.join(application_path, str(bug_id))
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # 4. Download attachments
    for i, item in enumerate(items):
        name, extension = os.path.splitext(item['name'])
        file_path = os.path.join(output_dir, f"{name}_{item['id']}{extension}")
        print(f'{i+1}/{len(items)} - {file_path}')
        with requests.get(f'https://cloudpoint.tpondemand.com/Attachment.aspx', params={'AttachmentID': item['id']}, verify=False, auth=HTTPBasicAuth(login, password), stream=True) as r:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)


def entity_id(value):
    """ Check value for positive integer value
    https://stackoverflow.com/a/14117511/2255764
    :param value: input value
    """
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f'"{value}" is an invalid positive int value')
    return ivalue


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TargetProcess Attachments Downloader')
    parser.add_argument('-l', '--login', help='TP Login', required=True)
    parser.add_argument('-p', '--password', help='TP Password', required=True)
    parser.add_argument('-id', '--id', help='TP Entity Id', type=entity_id, required=True)
    args = parser.parse_args()
    main(args.login, args.password, args.id)
