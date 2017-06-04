# from __future__ import print_function
import httplib2
import os
import pprint

import praw
import re
import datetime
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

def getDate(submission):
    time = datetime.date.fromtimestamp(submission.created)
    # return datetime.date.fromtimestamp(time)
    return time.strftime('%Y-%m-%d')

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def enoughGames(scoreList):
    gamesPlayed = 0
    for score in scoreList:
        if isNumber(score):
            gamesPlayed += 1
    if gamesPlayed > 3:
        return True
    else:
        return False

def runScript():
    """
    Link to sheet:
    https://docs.google.com/spreadsheets/d/1BTO3TI6GxiJmDvMqmafSk5UQs8YDvAafIAv0-h16MOw/edit?usp=sharing
    """
    # Get credentials to be able to access the google sheets API

    f = open('log.txt', 'a')
    print("Script run at: " + str(strftime("%Y-%m-%d %H:%M:%S", localtime())), file=f)
    print("Script run at: " + str(strftime("%Y-%m-%d %H:%M:%S", localtime())))

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    # Set basic info about the spreadsheet
    SHEET_ID = '1BTO3TI6GxiJmDvMqmafSk5UQs8YDvAafIAv0-h16MOw'
    RANGE_ENTRY = 'Entire Sub!'
    RANGE_STARTING_CELL = 'Overview!C7:C7'
    RANGE_CHALLENGE_COUNT = 'Overview!F7:F7'
    RANGE_POST_RULES = 'Overview!J5:J'
    RANGE_COMMENT_RULES = 'Overview!M5:M'
    RANGE_LAST_UPDATE = 'Overview!C9:C9'
    RANGE_CHALLENGES_PARSED = 'Overview!F9:F9'
    RANGE_OVERWRITE_SCORE = 'Overview!P4:R'
    RANGE_PLACES = 'Entire Sub!A32:D'
    
    # Read reddit client_id and client_secret from file (to avoid accidentally copying it)
    inputFile = open("RedditAPIAccess.txt")
    lines = []
    for line in inputFile:
        lines.append(line)
    client_id = lines[0]
    client_secret = lines[1]

    # Get reddit instance
    reddit = praw.Reddit(client_id=client_id.replace('\n', ''), 
                         client_secret=client_secret.replace('\n', ''), 
                         user_agent='windows:geoguessr_comment_crawler:0.1 (by /u/LiquidProgrammer')

    # print(client_id)
    # print(client_secret)
    # exit()

    # Get subreddit instance
    subreddit = reddit.subreddit('geoguessr')

    # Get starting cell for data entry
    RANGE_ENTRY = RANGE_ENTRY + service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_STARTING_CELL).execute().get('values', [])[0][0]

    # Get the submission count to be retrieved by the program
    submissionCount = int(service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_CHALLENGE_COUNT).execute().get('values', [])[0][0])

    # Clear preexisting data in the sheet
    print("Clearing preexisting data", file=f)
    service.spreadsheets().values().clear(spreadsheetId=SHEET_ID, range=RANGE_ENTRY + ':BXZ200', body={}).execute()
    service.spreadsheets().values().clear(spreadsheetId=SHEET_ID, range=RANGE_PLACES, body={}).execute()

    # Get comment and post ids which need be ignored
    postRulesInput = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_POST_RULES).execute()
    rules = postRulesInput.get('values', [])

    postRules = set(rule[0] for rule in rules)

    commentRulesInput = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_COMMENT_RULES).execute()
    rules = commentRulesInput.get('values', [])

    commentRules = set('t1_' + rule[0] for rule in rules)

    print("Found these rules from the overview sheet:", file=f)
    print("Post rules: ", file=f)
    print(postRules, file=f)
    print("Comment rules: ", file=f)
    print(commentRules, file=f)


    # Generate submission list which shall be used in the rest of the file
    # Necessary so that certain posts could be consistently ignored
    # Rules for ignoring post are described in the overview sheet
    submissionList = [submission for submission in subreddit.submissions() if submission.id not in postRules and ('[1' in submission.title or '[2' in submission.title or '[3' in submission.title or '[4' in submission.title or '[5' in submission.title) ]
    """subreddit.new(limit = 10)"""

    # print(submissionList)
    print("Will print to this sheet and cell: " + RANGE_ENTRY, file=f)
    print("Read " + str(submissionCount) + " submissions. " + str(len(submissionList)) + " out if which counted as challenges.", file=f)

    # Create a set with all the names
    names = set([comment.author.name for submission in submissionList for comment in submission.comments if comment is not None and comment.author is not None])

    # Generate a date list which contains the date and the post title
    dates = ["=HYPERLINK(\"" + 'https://www.reddit.com/r/geoguessr/comments/' + submission.id + '", "' + getDate(submission) + ': ' + submission.title + "\")" for submission in submissionList]
    cornerValue = 'Player\Challenge'

    # Add the the value in the starting cell to the date list
    dates.insert(0, cornerValue)

    # Create a new list, this will be the list we will use to create the data list 
    scores = []

    # Add empty values for every name and every submission
    for name in names:
        scores.append(['' for i in range(0, len(submissionList))])

    # Convert the set to a list so that we could sort it alphabetically
    nameList = list(names)
    nameList.sort(key=str.lower)

    # Insert the names at the start of the score list
    for index, scoreLine in enumerate(scores):
        scoreLine.insert(0, nameList[index])


    # Might be necessary if there is a post which has a lot of comments
    # submission.comments.replace_more(limit=0)

    # Get top level comments from submissions and get their first numbers with regular expressions
    for index, submission in enumerate(submissionList):
        for topLevelComment in submission.comments:
            if topLevelComment.fullname not in commentRules and 'Previous win:' not in topLevelComment.body and 'for winning yesterday' not in topLevelComment.body and '|' not in topLevelComment.body and topLevelComment is not None and topLevelComment.author is not None:
                try:
                    number = max([int(number.replace(',', '')) for number in re.findall('(?<!round )(?<!~~)(?<!\w)\d+\,?\d+', topLevelComment.body)])
                except (IndexError, ValueError) as e:
                    number = -1
                    break
                if 0 <= number <= 32395:
                    scores[nameList.index(topLevelComment.author.name)][index + 1] = number

    # Read challenge overwrites
    overwrites = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_OVERWRITE_SCORE).execute().get('values', [])

    # Overwrite in scores
    for overwrite in overwrites:
        for index, submission in enumerate(submissionList):
            try:
                if submission.id == overwrite[2]:
                    scores[nameList.index(overwrite[0]) + 1][index + 1] = int(overwrite[1])
            except IndexError:
                pass

    # Remove players who have very few games
    scores[:] = [scoreList for scoreList in scores if enoughGames(scoreList)]
    nameList[:] = [scoreList[0] for scoreList in scores]

    # Insert the dates on the top of the scores 2D list
    scores.insert(0, dates)

    firstPlaces = {name:[0, 0, 0, 0] for name in nameList}

    # Calculate first/second/third places
    for i in range(1, len(scores[0])):
        currScores = [-1, -2, -3]
        for j in range(1, len(scores)):
            try:
                currScores.append(int(scores[j][i]))
            except ValueError:
                pass
        currScores.sort(reverse = True)
        while currScores[0] == currScores[1]:
            del currScores[1]
        while currScores[1] == currScores[2]:
            del currScores[2]
        # print(currScores)
        for place in range(0, 3):
            for j in range(1, len(scores)):
                if scores[j][i] == currScores[place]:
                    firstPlaces[nameList[j - 1]][place] += 1

    # Calculate games played
    for scoreList in scores:
        for score in scoreList:
            try:
                if isNumber(score):
                    firstPlaces[scoreList[0]][3] += 1
            except (IndexError, ValueError) as e:
                pass

    # Create the places things
    places = [[] for i in range(0, len(nameList))]

    for key, value in firstPlaces.items():
        places[nameList.index(key)] = value


    places = {'values': places[:]}
    # print(places)

    data = {'values': [scoreList[:] for scoreList in scores]}
    # print(data)

    # Write data to sheet
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_ENTRY, body=data, valueInputOption='USER_ENTERED').execute()

    # Write places to sheet
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_PLACES, body=places, valueInputOption='USER_ENTERED').execute()

    # Update "Last Update" value
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_LAST_UPDATE, body={'values': [[strftime("%Y-%m-%d\n%H:%M:%S", localtime())]]}, valueInputOption='USER_ENTERED').execute()    

    # Update "Challenges parsed" value
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_CHALLENGES_PARSED, body={'values': [[len(submissionList)]]}, valueInputOption='USER_ENTERED').execute()    

    print('Successfully entered data.', file=f)
    f.close()

if __name__ == '__main__':
    runScript()
