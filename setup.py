from configupdater import ConfigUpdater

configfile = "config0.ini"

updater = ConfigUpdater()
updater.read(configfile)


def setupReddit():
	while True:
		print("Input the client id for Reddit that you received at https://www.reddit.com/prefs/apps/. It is the second line below the below the name of your app.")
		client_id = input()
		print("Input the client secret for Reddit that you received at https://www.reddit.com/prefs/apps/.")
		client_secret = input()
		print("Input the username of the Reddit account you will be posting clips with.")
		username = input()
		print("Input the password of the Reddit account you will be posting clips with.")
		password = input()
		print("Input a user agent for the Reddit script. This can be anything you want, but it is good practice to use [nameOfScript] vX.x, or something along those lines.")
		user_agent = input()

		print(f"""Are these values correct?
		Client ID: {client_id}
		Client Secret: {client_secret}
		Reddit Username: {username}
		Reddit Password: {password}
		Reddit User Agent: {user_agent}
		If these values are correct, reply with Y:""")
		response = input()

		if response.upper() == "Y":
			(updater["FAVSUB"].add_before
			 .comment("Options for the Reddit Bot")
			 .section("REDDIT")
			 .space(2))
			updater["REDDIT"]["client_id"] = client_id
			updater["REDDIT"]["client_secret"] = client_secret
			updater["REDDIT"]["username"] = username
			updater["REDDIT"]["password"] = password
			updater["REDDIT"]["user_agent"] = user_agent
			break


def setupStreamable():
	print("What is the email used for your Streamable account? ")
	streamableUsername = input()
	print("What is the password used for your Streamable account? ")
	streamablePassword = input()

	print(f"""Are these values correct?
			Streamable Username: {streamableUsername}
			Streamable Password: {streamablePassword}
			If these values are correct, reply with Y:""")
	response = input()

	if response.upper() == "Y":
		updater["STREAMABLE"]["username"].value = streamableUsername
		updater["STREAMABLE"]["password"].value = streamablePassword


def setupFileStructure():
	print("Where does OBS save your clips?")
	path = input()
	print("Where do you want to script to save your sorted clips?")
	sortedPath = input()


	print(f"""Are these values correct?
			OBS Save Path: {path}
			Sorted Clips Path: {sortedPath}
			If these values are correct, reply with Y:""")
	response = input()

	if response.upper() == "Y":
		path = path.replace("/", "//")
		sortedPath = sortedPath.replace("/", "//")
		updater["FILES"]["path"].value = path
		updater["FILES"]["sortedPath"].value = sortedPath

def addSubreddits():
	(updater["FAVSUB"].add_after
	 .space(2)
	 .comment("Subreddits of NHL Teams")
	 .section("SUBREDDITS")
	 .space(2))
	updater["SUBREDDITS"]["BOS"] = "BostonBruins"
	updater["SUBREDDITS"]["BUF"] = "sabres"
	updater["SUBREDDITS"]["DET"] = "DetroitRedWings"
	updater["SUBREDDITS"]["FLA"] = "FloridaPanthers"
	updater["SUBREDDITS"]["MTL"] = "Habs"
	updater["SUBREDDITS"]["OTT"] = "OttawaSenators"
	updater["SUBREDDITS"]["TBL"] = "TampaBayLightning"
	updater["SUBREDDITS"]["TOR"] = "leafs"

	updater["SUBREDDITS"]["CAR"] = "canes"
	updater["SUBREDDITS"]["CBJ"] = "BlueJackets"
	updater["SUBREDDITS"]["NJD"] = "devils"
	updater["SUBREDDITS"]["NYI"] = "NewYorkIslanders"
	updater["SUBREDDITS"]["NYR"] = "rangers"
	updater["SUBREDDITS"]["PHI"] = "Flyers"
	updater["SUBREDDITS"]["PIT"] = "penguins"
	updater["SUBREDDITS"]["WSH"] = "caps"

	updater["SUBREDDITS"]["ARI"] = "Coyotes"
	updater["SUBREDDITS"]["CHI"] = "hawks"
	updater["SUBREDDITS"]["COL"] = "ColoradoAvalanche"
	updater["SUBREDDITS"]["DAL"] = "DallasStars"
	updater["SUBREDDITS"]["MIN"] = "wildhockey"
	updater["SUBREDDITS"]["NSH"] = "Predators"
	updater["SUBREDDITS"]["STL"] = "stlouisblues"
	updater["SUBREDDITS"]["WPG"] = "winnipegjets"

	updater["SUBREDDITS"]["ANA"] = "AnaheimDucks"
	updater["SUBREDDITS"]["CGY"] = "CalgaryFlames"
	updater["SUBREDDITS"]["EDM"] = "EdmontonOilers"
	updater["SUBREDDITS"]["LAK"] = "losangeleskings"
	updater["SUBREDDITS"]["SJS"] = "SanJoseSharks"
	updater["SUBREDDITS"]["SEA"] = "SeattleKraken"
	updater["SUBREDDITS"]["VAN"] = "canucks"
	updater["SUBREDDITS"]["VGK"] = "goldenknights"


def main():
	reddit = input("Do you want to set up the Reddit bot? ")
	if reddit.upper() == "Y":
		setupReddit()
	streamable = input("Do you want to set up Streamable? ")
	if streamable.upper() == "Y":
		setupStreamable()
	fileStructure = input("Do you want to set up your file structure? ")
	if fileStructure.upper() == "Y":
		setupFileStructure()
	while True:
		oldReddit = input(" Do you prefer old or new reddit? (1 - Old, 2 - New)")
		if int(oldReddit) == 1:
			redditBase = "https://old.reddit.com/r/"
			updater["REDDIT"]["redditBase"] = redditBase
			break
		elif int(oldReddit) == 2:
			redditBase = "https://new.reddit.com/r/"
			updater["REDDIT"]["redditBase"] = redditBase
			break
		else:
			print("Invalid value inputted. Please try again.")
	addSubreddits()
	with open(configfile, 'w') as configPush:
		updater.write(configPush)





if __name__ == "__main__":
	main()