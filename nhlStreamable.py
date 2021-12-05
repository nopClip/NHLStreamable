import operator
from stat import ST_CTIME
import os, sys, time
import glob
from datetime import date
from pathlib import Path
from streampy import *
import time
import sigfig
import praw
import ffmpeg
import subprocess
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

reddit = praw.Reddit('bot1')
reddit.validate_on_submit = True

redditBot = True # Set this value to True if you are planning on using this script to post to Reddit
redditBase = "https://old.reddit.com/r/" # Remove "old." from the string if you prefer new Reddit

sortedPath = config['FILES']['sortedPath']
path = config['FILES']['path']
files = os.listdir(path); # Get the files in the path
games = {}
teams = {}
favSub = config['FAVSUB']['favSub']

s = Streamable()



def mostRecentFile(path):
    folder_path = path

    #Note: I haven't tested this with anything other than mp4 as that is what I use. These are the recording outputs that OBS supports, however.
    #file_type = '\*flv'
    file_type = '\*mp4'
    #file_type = '\*mov'
    #file_type = '\*mkv'
    #file_type = '\*ts'
    #file_type = '\*m3u8'

    files = glob.glob(folder_path + file_type)
    max_file = max(files, key=os.path.getctime)

    return max_file

def newDay():
    today = date.today()

    #Get the list of teams and IDs from the NHL API
    nhlTeams = "https://records.nhl.com/site/api/franchise?include=teams.id&include=teams.active&include=teams.triCode&include=teams.placeName&include=teams.commonName&include=teams.fullName&include=teams.logos&include=teams.conference.name&include=teams.division.name&include=teams.franchiseTeam.firstSeason.id&include=teams.franchiseTeam.lastSeason.id&include=teams.franchiseTeam.teamCommonName"
    response = requests.get(nhlTeams)
    jsonresp = response.json()

    count = 0
    for i in jsonresp['data']:
        try:
            id = i['mostRecentTeamId']
        except Exception:
            id = i['id']
        teams[count] = {
            'id': id,
            'fullName': i['fullName'],
            'triCode': i['teamAbbrev']
        }
        count += 1

    # Get the schedule from the NHL API
    schedule = "https://statsapi.web.nhl.com/api/v1/schedule"

    response = requests.get(schedule)
    jsonresp = response.json()

    gameCount = 0
    for game in jsonresp['dates'][0]['games']:
        home = game['teams']['home']['team']['id']
        away = game['teams']['away']['team']['id']
        for i in teams:
            if teams[i]['id'] == home:
                homeTri = teams[i]['triCode']
            if teams[i]['id'] == away:
                awayTri = teams[i]['triCode']

        games[gameCount] = {
            'home': homeTri,
            'away': awayTri,
            'clipCount': 0,
            'clips': {},
            'files': {}
        }
        gameCount += 1


def newCustomDay():
    game = {}
    game = input("How many games are we clipping today? ")
    for i in range(int(game)):
        home = input(f"Input the home team of game {i+1}: ")
        away = input(f"Input the away team of game {i+1}: ")
        games[i] = {
            'home': home,
            'away': away,
            'clipCount': 0,
            'clips': {},
            'files': {}
        }


def saveJSON(games, today):
    file_path = Path(f"{sortedPath}\{today.year}-{today.month}-{today.day}\{today.year}-{today.month}-{today.day} games.json")
    with file_path.open("w") as f:
        json.dump(games, f, indent=4, sort_keys=False, separators=(",", " : "))


def printClips():
    print('Print clips from which game?')
    for i in games:
        count = int(i)+1
        print(f"{count}. {games[i]['home']}-{games[i]['away']}")
    gamePicked = int(input()) - 1
    for i in games[gamePicked]['clips']:
        try:
            print(games[gamePicked]['clips'][i], f" [credit u/{games[gamePicked]['clips'][i]['credit']}]")
        except Exception:
            print(games[gamePicked]['clips'][i])
        print()

def removeClips():
    while True:
        #Identify which game to print clips from
        print('Print clips from which game?')
        for i in games:
            count = int(i)+1
            print(f"{count}. {games[i]['home']}-{games[i]['away']}")

        gamePicked = int(input()) - 1

        # Print out the clips from that game
        print()
        for i in games[gamePicked]['clips']:
            print(f"{i}. {games[gamePicked]['clips'][i]}")

        # Identify the clip to remove
        response = input("Which clip would you like to remove? ")
        # Remove the clip and file from the list
        games[gamePicked]['clips'].pop(int(response))
        games[gamePicked]['files'].pop(int(response))

        # Print out the remoaining clips
        print()
        for i in games[gamePicked]['clips']:
            print(f"{i}. {games[gamePicked]['clips'][i]}")

        done = input("Done removing clips? ")
        games[gamePicked]['clipCount'] -= 1
        if done.upper() == 'Y':
            break

def changeGames():
    # Define variables I need for this stupid function
    global games
    newGames = {}
    gameCount = 0

    # Iterate through the list of games in games and add them to newGames
    for game in games:
        newGames[gameCount] = games[game]
        gameCount += 1

    # Set games = newGames
    games = newGames

def removeGame():
    while True:
        #Identify which game to remove from the list
        print('Remove which game?')
        for i in games:
            count = int(i)+1
            print(f"{count}. {games[i]['home']}-{games[i]['away']}")

        # Select the game and remove it from the list
        gamePicked = int(input()) - 1
        del games[gamePicked]

        print()
        # I don't know why I have to call this function to make this work but when I don't it breaks so i give up
        changeGames()
        for i in games:
            count = int(i)+1
            print(f"{count}. {games[i]['home']}-{games[i]['away']}")

        done = input("Done removing games? ")
        if done.upper() == 'Y':
            break

def mergeClips():
    # Identify whether there are clips to remove from the list before merging
    remove = input("Do you want to remove any clips before making the merge? ")

    if remove.upper() == 'Y':
        removeClips()

    # Identify which game to merge clips from
    print('Merge clips from which game?')
    for i in games:
        count = int(i)+1
        print(f"{count}. {games[i]['home']}-{games[i]['away']}")

    gamePicked = int(input()) - 1

    # Write the selected clips to a txt file for ffmpeg
    today = date.today()
    with open("files.txt", 'w') as f:
        print(games[gamePicked])
        for i in games[gamePicked]['files']:
            f.write("file '")
            f.write(f"{games[gamePicked]['files'][i]}")
            f.write("'")
            f.write('\n')

    # Get the root directory for the clips
    root_dir = Path(f"{sortedPath}\{today.year}-{today.month}-{today.day}\{games[gamePicked]['home']}-{games[gamePicked]['away']}")

    # Identify an output file for the highlight pack
    output = f"{root_dir}\{games[gamePicked]['home']}-{games[gamePicked]['away']}.mp4"
    # Run the ffmpeg command to merge the clips NOTE: fading between clips doesn't currently work.
    # This requires the gltransition ffmpeg filter
    fade = input("Do you want to fade between clips? [NOT CURRENTLY WORKING]")
    if fade.upper() == "Y":
        os.system(f'ffmpeg -f concat -safe 0 -i files.txt -filter_complex "gltransition=duration=4:offset=1.5" -c copy {output}')
    else:
        other = input("Do you want to input your own ffmpeg command? ")
        if other.upper() == "Y":
            command = input("Input the command you want to use. ")
            os.system(command)
        else:
            os.system(f"ffmpeg -f concat -safe 0 -i files.txt -c copy {output}")

    upload = input("Do you want to upload this highlight pack to Streamable? ")
    if upload.upper() == 'Y':
        streamableUpload(Path(output))

def mergeSelectedClips():
    today = date.today()
    with open("files.txt", 'w') as f:
        while True:
            print('Select a clip from which game?')
            for i in games:
                count = int(i)+1
                print(f"{count}. {games[i]['home']}-{games[i]['away']}")

            gamePicked = int(input()) - 1

            print()
            print("Which clip do you want to add to the list?")
            for i in games[gamePicked]['clips']:
                print(f"{i+1}. {games[gamePicked]['clips'][i]}")

            clipPicked = int(input()) - 1

            f.write("file '")
            f.write(f"{games[gamePicked]['files'][clipPicked]}")
            f.write("'")
            f.write('\n')

            done = input("Done adding clips to the highlight pack? ")
            if done.upper() == "Y":
                break


    # Get the root directory for the clips

    root_dir = Path(f"{sortedPath}\{today.year}-{today.month}-{today.day}\selectedMerge")
    if not root_dir.is_dir():
        root_dir.mkdir(exist_ok=True, parents=True)

    title = input("What do you want to title the highlight pack? ")
    # Identify an output file for the highlight pack
    output = f"{root_dir}\{title}.mp4"

    # Run the ffmpeg command to merge the clips NOTE: fading between clips doesn't currently work.
    # This requires the gltransition ffmpeg filter
    fade = input("Do you want to fade between clips? [NOT CURRENTLY WORKING]")
    if fade.upper() == "Y":
        os.system(f'ffmpeg -f concat -safe 0 -i files.txt -filter_complex "gltransition=duration=4:offset=1.5" -c copy {output}')
    else:
        other = input("Do you want to input your own ffmpeg command? ")
        if other.upper() == "Y":
            command = input("Input the command you want to use. ")
            os.system(command)
        else:
            print(f"ffmpeg -f concat -safe 0 -i files.txt -c copy {output}")
            os.system(f"ffmpeg -f concat -safe 0 -i files.txt -c copy {output}")

    upload = input("Do you want to upload this highlight pack to Streamable? ")
    if upload.upper() == 'Y':
        streamableUpload(Path(output))

def downloadClip():
    today = date.today()
    url = input("Input the URL of the clip to download: ")
    output = input("What do you want to name the clip? ")
    credit = input("Who originally posted the clip? ")

    print('Which game is this clip from?')
    for i in games:
        # Iterate through the games and print them out
        count = int(i)+1
        print(f"{count}. {games[i]['home']}-{games[i]['away']}")
    gamePicked = int(input()) - 1

    try:
        root_dir = Path(f"{sortedPath}/{today.year}-{today.month}-{today.day}\{games[gamePicked]['home']}-{games[gamePicked]['away']}")
        if not root_dir.is_dir():
            root_dir.mkdir(exist_ok=True, parents=True)
    except Exception as e:
        print(e)
    try:
        subprocess.call(['youtube-dl', '-f', 'mp4', url, '-o', f"{sortedPath}/{today.year}-{today.month}-{today.day}\{games[gamePicked]['home']}-{games[gamePicked]['away']}\{output}.mp4"])
        # os.system(f"youtube-dl {url} -f mp4 -o C:/SortedStreamables/{today.year}-{today.month}-{today.day}\{games[gamePicked]['home']}-{games[gamePicked]['away']}\{output}.mp4")
    except Exception as e:
        print(e)
    try:
        clipCount = games[gamePicked]['clipCount']
        games[gamePicked]['clips'][clipCount] = f'[{output}]({url}) [credit u/{credit}]'
        games[gamePicked]['files'][clipCount] = f"{sortedPath}/{today.year}-{today.month}-{today.day}\{games[gamePicked]['home']}-{games[gamePicked]['away']}\{output}.mp4"
        games[gamePicked]['clipCount'] += 1
    except Exception as e:
        print(e)

def streamableUpload(file):
    #Identify which game the clip is from
    print('Which game is this clip from?')
    for i in games:
        # Iterate through the games and print them out
        count = int(i)+1
        print(f"{count}. {games[i]['home']}-{games[i]['away']}")
    gamePicked = int(input()) - 1

    # Add to the clipCount
    home = games[gamePicked]['home']
    away = games[gamePicked]['away']
    games[gamePicked]['clipCount'] += 1
    clipCount = games[gamePicked]['clipCount']


    # Get the title for Streamable
    title = input('Title for the video: ')

    # Get start time for reporting
    startTime = time.time()

    # Upload to Streamable
    uploadedFile = s.upload(file, title)

    # Printout with URL and Reddit comment formatting
    print("--- %s seconds ---" % (round((time.time() - startTime), 3)))
    # print(uploadedFile)
    print(f'''
    URL: https://streamable.com/{uploadedFile["shortcode"]}

    [{title}](https://streamable.com/{uploadedFile["shortcode"]})
    ''')

    # Add the clip to both the file list and the clip list
    games[gamePicked]['clips'][clipCount-1] = f'[{title}](https://streamable.com/{uploadedFile["shortcode"]})'

    rename = input('Move and rename the file? ')

    if rename.upper() == 'Y':
        #Get todays date
        today = date.today()
        # Set a root directory
        try:
            root_dir = Path(f"{sortedPath}\{today.year}-{today.month}-{today.day}\{home}-{away}")
        except Exception as e:
            print(e)
        # If the root directory doesn't exist, create it
        if not root_dir.is_dir():
            root_dir.mkdir(exist_ok=True, parents=True)

        # Put the file in the directory
        try:
            os.replace(file, f"{sortedPath}\{today.year}-{today.month}-{today.day}\{home}-{away}\{title}.mp4")
        except Exception as e:
            print(e)

        # Add the gile to the list of files
        games[gamePicked]['files'][clipCount-1] = f"{sortedPath}\{today.year}-{today.month}-{today.day}\{home}-{away}\{title}.mp4"

    elif rename.upper() == "N":
        games[gamePicked]['files'][clipCount-1] = "None"

    return uploadedFile, home, away, clipCount, title

def main():
    newDay()
    new_file = mostRecentFile(path)

    while True:
        try:
            upload = input("Would you like to upload the latest file? (y/n) Press 'm' for the menu: ")
            if upload.upper() == 'Y':
                file = mostRecentFile(path)
                uploadedFile, home, away, clipCount, title = streamableUpload(file)
                if redditBot == True:
                    toReddit = input("Post to reddit? ")
                    if toReddit.upper() == 'Y':
                        while True:
                            redditTitle = input("Input a title for Reddit: ")
                            done = input(f"Is this title good? {redditTitle} ")
                            if done.upper() == 'Y':
                                break
                        print(f'''
                        1. Upload to r/Hockey
                        2. Upload to r/{favSub}
                        3. Upload to a different subreddit
                        ''')

                        subToPost = input("Please Choose: ")
                        if subToPost == "1":
                            sub = "hockey"
                            print("Posting to r/Hockey")
                            input("Press enter to confirm ")
                            post = reddit.subreddit("hockey").submit(redditTitle, url=f"https://streamable.com/{uploadedFile['shortcode']}")
                        if subToPost == "2":
                            sub = favSub
                            print(f"Posting to r/{favSub}")
                            input("Press enter to confirm ")
                            post = reddit.subreddit(f"{favSub}").submit(redditTitle, url=f"https://streamable.com/{uploadedFile['shortcode']}")
                        if subToPost == "3":
                            sub = input("Which sub do you want to post to? ")
                            print(f"Posting to r/{sub}")
                            input("Press enter to confirm ")
                            post = reddit.subreddit(sub).submit(redditTitle, url=f"https://streamable.com/{uploadedFile['shortcode']}")

                        print(f"""

                        Link: {redditBase}{sub}/comments/{post}

                        """)


            if upload.upper() == 'M':
                print("--------------------------------------------------------------------------")
                print(""" Menu:
                1. Start a new day
                2. Start a new custom day
                3. Print the clip list from a game
                4. Remove a clip from the clip list
                5. Save the clipList
                6. Merge Clips
                7. Merge Specific Clips
                8. Download a clip
                9. Remove a game
                """)
                answer = input()
                if int(answer) == 1:
                    games = {}
                    newDay()
                elif int(answer) == 2:
                    games = {}
                    newCustomDay()
                elif int(answer) == 3:
                    printClips()
                elif int(answer) == 4:
                    removeClips()
                elif int(answer) == 5:
                    saveJSON(games, today)
                elif int(answer) == 6:
                    mergeClips()
                elif int(answer) == 7:
                    mergeSelectedClips()
                elif int(answer) == 8:
                    downloadClip()
                elif int(answer) == 9:
                    removeGame()
        except Exception:
            pass

if __name__ == "__main__":
    main()
