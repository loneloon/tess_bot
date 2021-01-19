# Tess Bot

## Intro
	
	Tess Bot is a testing chat bot based on Telegram API.
	Its main function is to perform a testing sequence in a chat form. Test is initiated by calling an assigned command.

## HOWTO

	You may require to run Tess as a background daemon on your linux server like your ordinary web server.
	For general convenience i have included a deploy script which is located in /deploy package.
	Ubuntu 18 and above recommended.

	Modify settings up to your needs:
		1. Create your bot account in Telegram via @BotFather
		2. Insert your unique Telegram bot token 
		*(if you have any troubles with the above, check [Creating a new bot](https://core.telegram.org/bots#6-botfather))*
		3. Add custom questions (settings contain format commentary)
		4. Modify custom replies such as greeting
		5. At the end of the test, Tess will provide a special invitation link to a telegram group or channel. 
		Be sure to add the correct group/channel @name and promote your bot to an admin role of a channel/group.

	How to deploy:
		1. Git clone the repository to any convenient location on your server: sudo git clone https://github.com/loneloon/tess_bot
		2. Install requirements from /deploy: sudo python3 -m pip install -r requirements.txt
		3. Launch create_service.py as root (if the service was created successfully you will recieve no output): sudo python3 create_service.py
		4. Start the service: sudo systemctl tess_bot

## What's under the hood?

	-Tess is based on pyTelegramBotAPI by [eternnoir](https://github.com/eternnoir/pyTelegramBotAPI), 
	which is quite a handy implementation of the official Telegram Bot API.

	-Tess stores user data in sqlite type db, using a DB module written with SQLAlchemy assets and supplied db-object models (read more on how the data mapper operates inside the script itself: /db_assets/db.py).

	-Tess is always logging function calls decorated with Log() on a daily rotation (new day - new log file).

	-Tess can be modified to your liking, for instance you can supply a number of input string cases and bot replies 
	(empty methods for that purpose can be found at the bottom of the TestingBot class).

*Please get in touch, if anything remains unclear.*