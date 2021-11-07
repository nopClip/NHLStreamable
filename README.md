# NHLStreamable: A Python Script to semi-automate clipping games and uploading to Streamable and Reddit

When clipping games during the 2020-21 playoffs, I found that most of my time was spent accessing Streamable and Reddit, so I began to develop a python script that semi-automates the process.  



## So what does this thing even do?

- Automatically grabs the day's schedule from the NHL API.
- Upload a clip using streampy to Streamable
- Select a subreddit, and post a clip with a title of your choosing using PRAW
- Download clips using youtube-dl
- Merge clips using ffmpeg to create "highlight packs"



## Requirements

To run this project you will need:

- [Python 3](https://www.python.org/downloads/)
- [streampy 1.2](https://pypi.org/project/streampy/) - For interacting with the Streamable API
- [PRAW](https://praw.readthedocs.io/en/stable/) - For posting to Reddit
- [ffmpeg](https://www.ffmpeg.org/) - For creating "Highlight packs"
- [youtube-dl](https://youtube-dl.org/) - For downloading clips others have posted
- 



## OBS Settings

For setting up OBS and titling your posts, you can mostly follow the how-to I provided [last year](https://www.reddit.com/r/hockey/comments/et3hlw/howto_so_you_wanna_make_clips_for_rhockey_heres/). [These are my new settings under Output>Recording in OBS](https://i.imgur.com/86SgrV9.png). In order for the script to work, the only thing you need to have set the same is the recording format, MP4. MP4 was chosen as Vegas Pro 16, the editing software I use to create [SensWin](https://streamable.com/fkbrja) hates MKV with a passion and refuses to open MKV files. Make sure to note down your Recording Path, as it will be needed later.



Tip: If you're having an issue where the first ~10 seconds of your clip are frozen, like in this [clip](https://streamable.com/1ryajt) [TW: Oilers fans], then most likely the drive you're saving to is not fast enough for recording. My solution to this was to change the save folder to be on my SSD, and I havn't had the issue since.



## Setting up the Reddit Bot

Setting up the Reddit bot is reasonably straightforward.

On reddit, click "preferences" > "apps" > "create another app". Give your app a name and a description, classify it as a "script", and set your redirect uri to be http://127.0.0.1.



Next, if you have python 3 installed with pip, run the following command:

```
pip install praw
```

Once praw is installed, return to your nhlStreamable folder, where you should see a "praw.ini" file. Under [bot1], populate that area with your client id (the string under "personal use script" on the reddit apps page), client secret, password of the posting account, username of the posting account, and user agent. You can use anything as your user agent, but make sure it can be tied back in some way to the script itself. For example, if your username for the posting account is hockeyClip, your user agent could be hockeyClip v1. At this point your reddit poster should be ready to go, and you can test it by making a clip, and posting it to the test subreddit I created, /r/nhlStreamable.



## Setting up the Streamable API

In the nhlStreamable folder is streampy.py. The only lines you need to change in that file is lines 11 & 12:

```
USER = 'YOUR STREAMABLE EMAIL'
PASS = 'YOUR STREAMABLE PASSWORD'
```

Change those lines to be your email for streamable, and your password.

## Things you need to change in nhlStreamable.py

There are a few things you'll want to change in the nhlStreamable script, namely:

- Set redditBot (Line 17) to False if you are not using this script to post to reddit.
- Change redditBase (Line 18) if you don't want to use old reddit.
- Change sortedPath (Line 20) to where you want the script to save your sorted clips. It saves them in the format [root_dir]\[date]\[Home-Away]\[name].
- Change path (Line 21) to where OBS (or your recording software of choice) saves your recordings.
