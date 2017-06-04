import praw
import re
import datetime

def getDate(submission):
    time = submission.created
    return datetime.date.fromtimestamp(time)

reddit = praw.Reddit(client_id='0hHzhJIBuAyRCQ', 
			  		 client_secret='M0tboDuq3tkG2ogH7ttu7aMnQio', 
			 		 user_agent='windows:geoguessr_comment_crawler:0.1 (by /u/LiquidProgrammer')

subreddit = reddit.subreddit('geoguessr')

#for submission in subreddit.new(limit = 3):
#	print(submission.title)
#	all_comments = submission.comments.list()

f = open("PostTitles.txt", 'w')

for submission in subreddit.submissions():
	print(str(getDate(submission)) + ' ' + submission.title + ' (ID=' + submission.id + ')', file=f)

f.close()