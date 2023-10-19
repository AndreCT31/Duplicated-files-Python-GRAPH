import requests
import json
import urllib
import os
from getpass import getpass
import time
from datetime import datetime

#list files
def list_files():
    response = requests.get(URL + 'me/drive/root/children', headers=HEADERS)
    if response.status_code == 200:
        files = json.loads(response.text)['value']
        for file in files:
            print(file['name'])
    else:
        print('Error fetching file list.')

#delete a file
def delete_file(filename):
    response = requests.delete(URL + f'me/drive/root:/{filename}', headers=HEADERS)
    if response.status_code == 204:
        print(f'{filename} deleted successfully.')
    else:
        print(f'Error deleting {filename}.')



#delete files by a portion of their name
def delete_files_by_name_in_folder(folder_id, name_portion):
    response = requests.get(URL + f'me/drive/items/{folder_id}/children', headers=HEADERS)
    if response.status_code == 200:
        items = json.loads(response.text)['value']
        deleted_count = 0
        for item in items:
            if name_portion in item['name'] and item['file']:
                response = requests.delete(URL + f"me/drive/items/{item['id']}", headers=HEADERS)
                if response.status_code == 204:
                    print(f"{item['name']} deleted successfully.")
                    deleted_count += 1
                else:
                    print(f"Error deleting {item['name']}.")
            elif 'folder' in item:
                delete_files_by_name_in_folder(item['id'], name_portion)
        if deleted_count == 0:
            print(f"No files with '{name_portion}' in their name found in this folder.")
    else:
        print('Error fetching item list.')

# Get folder IDs and names within a specific folder
def get_folder_ids_and_names(folder_id):
    response = requests.get(URL + f'me/drive/items/{folder_id}/children', headers=HEADERS)
    if response.status_code == 200:
        items = json.loads(response.text)['value']
        folders = {}
        for item in items:
            if 'folder' in item:
                folders[item['name']] = item['id']
        return folders
    else:
        print('Error fetching folder list.')

# Delete files by a portion of their name
def delete_files_by_name(name_portion):
    response = requests.get(URL + 'me/drive/items/root/children', headers=HEADERS)
    if response.status_code == 200:
        items = json.loads(response.text)['value']
        deleted_count = 0
        for item in items:
            if name_portion in item['name'] and item['file']:
                response = requests.delete(URL + f"me/drive/items/{item['id']}", headers=HEADERS)
                if response.status_code == 204:
                    print(f"{item['name']} deleted successfully.")
                    deleted_count += 1
                else:
                    print(f"Error deleting {item['name']}.")
        if deleted_count == 0:
            print(f"No files with '{name_portion}' in their name found.")
    else:
        print('Error fetching item list.')        

# Call this function to start the process of deleting files within folders and subfolders based on name portion
def delete_files_in_all_folders():
    name_portion = input("Enter the portion of the filename to delete: ")
    
    root_folders = get_folder_ids_and_names('root')
    if root_folders:
        print("Available folders:")
        for name, folder_id in root_folders.items():
            print(f"{name}: {folder_id}")
        
        selected_folder_name = input("Enter the name of the folder to start deletion from: ")
        selected_folder_id = root_folders.get(selected_folder_name)
        if selected_folder_id:
            delete_files_by_name_in_folder(selected_folder_id, name_portion)
            print('Deletion process completed.')
        else:
            print("Invalid folder name.")
    else:
        print("No folders found.")

URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
client_id = "CLIENT_ID"
permissions = ['files.readwrite']
response_type = 'token'
redirect_uri = 'https://localhost:8000/'
scope = ''
for items in range(len(permissions)):
    scope = scope + permissions[items]
    if items < len(permissions)-1:
        scope = scope + '+'

print('Click over this link ' +URL + '?client_id=' + client_id + '&scope=' + scope + '&response_type=' + response_type+\
     '&redirect_uri=' + urllib.parse.quote(redirect_uri))
print('Sign in to your account, copy the whole redirected URL.')
code = input("Paste the URL here :")
token = code[(code.find('access_token') + len('access_token') + 1) : (code.find('&token_type'))]
URL = 'https://graph.microsoft.com/v1.0/'
HEADERS = {'Authorization': 'Bearer ' + token}
response = requests.get(URL + 'me/drive/', headers=HEADERS)
if response.status_code == 200:
    response = json.loads(response.text)
    print('Connected to the OneDrive of', response['owner']['user']['displayName']+' (',response['driveType']+' ).', \
         '\nConnection valid for one hour. Reauthenticate if required.')

    while True:
        print('\nCRUD Menu:')
        print('1. List Files')
        print('2. Delete File by Name')
        print('3. Delete Files by Name Portion')  
        print('4. Delete Files in All Folders')
        print('5. Exit')
        
        choice = input('Enter your choice: ')
        
        if choice == '1':
            list_files()
        elif choice == '2':
            filename = input('Enter the filename to delete: ')
            delete_file(filename)
        elif choice == '3':
            name_portion = input("Enter the portion of the filename to delete: ")
            delete_files_by_name(name_portion) 
        elif choice == '4':
            delete_files_in_all_folders()
        elif choice == '5':
            print('Exiting...')
            break
        else:
            print('Invalid choice. Please choose again.')

else:
    response_data = json.loads(response.text)
    print('API Error! : ', response_data['error']['code'],\
         '\nSee response for more details.')
