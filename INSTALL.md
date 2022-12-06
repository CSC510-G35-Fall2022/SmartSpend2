# Install and Setup
The below instructions can be followed in order to set-up this bot at your end in a span of few minutes! Let's get started:

1. This installation guide assumes that you have already installed Python (Python3 would be preferred)

2. Clone this repository to your local system at a suitable directory/location of your choice

3. Start a terminal session, and navigate to the directory where the repo has been cloned

4. Run the following command to install the required dependencies:
```
  pip install -r requirements.txt
```
5. Download and install the Telegram desktop application for your system from the following site: https://desktop.telegram.org/

6. Once you login to your Telegram account, search for "BotFather" in Telegram. Click on "Start" --> enter the following command:
```
  /newbot
```
7. Follow the instructions on screen and choose a name for your bot. Post this, select a username for your bot that ends with "bot" (as per the instructions on your Telegram screen)

8. BotFather will now confirm the creation of your bot and provide a TOKEN to access the HTTP API - copy this token for future use.

9. Create a new collection in MongoDB Cloud Atlas. In the directory where this repo has been cloned, create a .env file with format like .env.sample in this repo and replace XXXX with the actual bot name, tokens and api hash and MongoDB URLs:

10. In the Telegram app, search for your newly created bot by entering the username and open the same. Once this is done, go back to the terminal session. Navigate to the directory containing the "code.py" file and run the following command:
```
  python code.py
```
11. A successful run will generate a message on your terminal that says "TeleBot: Started polling." 
12. Post this, navigate to your bot on Telegram, enter the "/start" or "/menu" command, and you are all set to track your expenses!

### Running the website
These are the install instructions for the website: 

`npm install -g @angular/cli`

angular material:

``ng add @angular/material``

installing tailwind: 

`npm install -D tailwindcss`

Now navigate to web/SmartSpend and type 
`npm start`

you should now be able to run the SmartSpend telegram bot and use the /website command to get your specific link for the website

### Run Style Check

1. For Style Checker (in local directory):

```
pip install pycodestyle
```

2. Run
   
```
pycodestyle --first <filepath>
```

### Testing the commands:

1. Install pytest:

```
pip install pytest
```

2. Run

```
pytest test/test_start_and_menu_command.py 
```

### Running Syntax Checker

1. Install syntax checker through your choice of python IDEs

2. Run through your choice of python IDEs


### Running code formatter

1. Install prettier

```
npm install --save-dev --save-exact prettier
```

2.

```
npm run prettier
```

### Other automated tools: audit

1. Run:

```
npm run audit
```

# Dependencies
| dependency         | version   | more information                                       |
|--------------------|-----------|--------------------------------------------------------|
| attrs              | 22.1.0    | https://www.attrs.org/en/stable/                       |
| beautifulsoup4     | 4.11.1    | https://www.crummy.com/software/BeautifulSoup/bs4/doc/ |
| bs4                | 0.0.1     | https://www.crummy.com/software/BeautifulSoup/bs4/doc/ |
| certifi            | 2022.9.24 | https://pypi.org/project/certifi/                      |
| charset-normalizer | 2.1.1     | https://pypi.org/project/charset-normalizer/           |
| idna               | 3.4       | https://pypi.org/project/idna/                         |
| iniconfig          | 1.1.1     | https://pypi.org/project/iniconfig/                    |
| packaging          | 21.3      | https://packaging.python.org/en/latest/                |
| pluggy             | 1.0.0     | https://pluggy.readthedocs.io/en/stable/               |
| py                 | 1.11.0    | https://pypi.org/project/py/                           |
| pyaes              | 1.6.1     | https://pypi.org/project/pyaes/                        |
| pyasn1             | 0.4.8     | https://pypi.org/project/pyasn/                        |
| pymongo            | 4.2.0     | https://pymongo.readthedocs.io/en/stable/              |
| pyparsing          | 3.0.9     | https://pypi.org/project/pyparsing/                    |
| pyTelegramBotAPI   | 4.7.0     | https://pypi.org/project/pyTelegramBotAPI/             |
| pytest             | 7.1.3     | https://docs.pytest.org/en/7.2.x/                      |
| python-dotenv      | 0.21.0    | https://pypi.org/project/python-dotenv/                |
| requests           | 2.28.1    | https://requests.readthedocs.io/en/latest/             |
| dnspython          | 2.2.1     | https://www.dnspython.org/                             |
| rsa                | 4.9         | https://pypi.org/project/rsa/                              |
| soupsieve          | 2.3.2.post1 | https://pypi.org/project/soupsieve/                        |
| tabulate           | 0.9.0       | https://pypi.org/project/tabulate/                         |
| telethon           | 1.25.1      | https://docs.telethon.dev/en/stable/                       |
| tomli              | 2.0.1       | https://pypi.org/project/tomli/                            |
| urllib3            | 1.26.12     | https://urllib3.readthedocs.io/en/stable/                  |
| matplotlib         | 3.1.3       | https://matplotlib.org/                                    |
| bot-telegram-tools | 1.1.0       | https://github.com/python-telegram-bot/python-telegram-bot |
| Flask              | 2.2.2       | https://flask.palletsprojects.com/en/2.2.x/                |

# Troubleshooting Common Problems
Problem: Bot not running properly, having issues with client ID.

Solution:
1. Check if dependencies are set properly.
2. Follow install steps to get bot token.
3. Paste new token in .env file.

<hr>

Problem: Website not opening when I'm clicking on the website link in the command

Solution:
1. Since the website is not deployed right now, the website must also be run
2. follow steps to run the website in the install instructions
