# from __future__ import print_function
from RefreshSheet import runScript, get_credentials
import httplib2
import os
import time
from time import gmtime, strftime, localtime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'GeoGuessr Statistics Tracker'

print('Runnning script')

while True:
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
	               'version=v4')
	service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

	SHEET_ID = '1BTO3TI6GxiJmDvMqmafSk5UQs8YDvAafIAv0-h16MOw'
	RANGE_NEED_REFRESH = 'Overview!F11:F11'
	
	needToRefresh = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_NEED_REFRESH).execute().get('values', [])[0][0]

	f = open('log.txt', 'a')
	print("Checking: " + str(strftime("%Y-%m-%d %H:%M:%S", localtime())), file=f)
	f.close()

	if needToRefresh == 'TRUE':
		service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_NEED_REFRESH, body={'values': [['PARSING']]}, valueInputOption='USER_ENTERED').execute()
		runScript()
		service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_NEED_REFRESH, body={'values': [['FALSE']]}, valueInputOption='USER_ENTERED').execute()
	
	time.sleep(300)