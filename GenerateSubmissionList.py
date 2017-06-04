import praw
import re
import datetime

def getDate(submission):
    time = submission.created
    return datetime.date.fromtimestamp(time)

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

subreddit = reddit.subreddit('geoguessr')

#for submission in subreddit.new(limit = 3):
#	print(submission.title)
#	all_comments = submission.comments.list()

f = open("PostTitles.txt", 'w')

for submission in subreddit.submissions():
	print(str(getDate(submission)) + ' ' + submission.title + ' (ID=' + submission.id + ')', file=f)

f.close()