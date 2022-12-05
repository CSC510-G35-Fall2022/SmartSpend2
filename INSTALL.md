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
npm install standard --save-dev
```

2. Run
   
```
npm test
```

### Testing the commands:

1. Install jest:

```
npm install --save-dev jest
```

2. Run

```
npm run test_commands
```

### Running Syntax Checker

1. Install syntax checker

```
npm install syntax-checker -g
npm install uglifyjs -g
sudo npm install -g uglify-js
```

2. Run:

```
npm run syntax
```
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
