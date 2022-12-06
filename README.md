# SmartSpend

![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![GitHub](https://img.shields.io/badge/Language-Python-blue.svg)
![GitHub contributors](https://img.shields.io/badge/Contributors-5-brightgreen)
[![DOI](https://zenodo.org/badge/562210446.svg)](https://zenodo.org/badge/latestdoi/562210446)
[![Platform](https://img.shields.io/badge/Platform-Telegram-blue)](https://desktop.telegram.org/)
![Python CI](https://github.com/kaushikjadhav01/SmartSpend/actions/workflows/build-test.yaml/badge.svg)

<hr>

## About SmartSpend

SmartSpend is an easy-to-use Telegram Bot that assists you in recording your daily expenses on a local system without any hassle.  
With simple commands, this bot allows you to:
- Add/Record a new spending
- Show the sum of your expenditure for the current day/month
- Display your spending history
- Clear/Erase all your records
- Edit/Change any spending details if you wish to
- Set limits for your daily/montly/yearly expenses
- Search the best deals for your purchase
- Share/Settle your expense with other users
- <img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/commands.png" alt="commands" width="500"/>


### <u>Additions:</u>
- Fixed several bugs related to parsing and tracking.
- Updated menu view to display slash commands when "/" is typed in telegram chat
- - <img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/updated_menu.png" alt="commands" width="500"/>
- Refactored old code to suit updated structure.
- - Previously all of the code was in a single file with around 650 lines. This appeared messy and was hard to edit parts of the program.
- - Attempted one refactor method which can be seen in [this branch](https://github.com/CSC510-G35-Fall2022/SmartSpend2/tree/refactor). This method was too time consuming and required more of the codebase to be refactored.
- - Tried another refactor method, much faster, worked simpler, did not need to update more of the code base. This has been merged to main.
- Moved away from Travis to GitHub actions for rolling builds.
- Also added cancel feature, to abort an 'add' transaction at any point.
- <u>Feature</u> -> Add 'limit_category' feature to work as an alarm when spending exceed preset limits.
- - Users can create limits on the existing categories, food, groceries, utilities, ...
- - <img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/limit1.png" alt="commands" width="500"/>
- - <img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/limit2.png" alt="commands" width="500"/>
- - When user adds an expense, limit categories, and all all three existing limits are checked.
- - <img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/exceedlim.png" alt="commands" width="500"/>
- - Ability to view limits for categories.
- - <img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/viewlmt.png" alt="commands" width="500"/>
- <u> Updated Feature display </u> -> Graphics
- - Added matplotlib graphs to display to view individual categories spendings on a pie chart.
- - ![Graph](https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/graph.png)
- <u> Updated Feature History </u> -> Graphics
- - Added matplotlib graphs to let user see a bar graph of spending vs month.
- - ![Graph](https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/history%20command.png)
- <u> Feature</u> -> Add 'website' feature to give the user a link to a personalized website. 
- - Created a website for the user to manage their expenses. The Telegram bot and the website work simultaneously and update in real time.
- - Website can add a new expense
- - Website can view all expense and filter/sort them
- - Website can view current limits and view accurate progress meters for category limits

Website: 

<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/Screen%20Shot%202022-12-05%20at%2011.43.37%20AM.png" width=1200>
## Demo
https://user-images.githubusercontent.com/15325746/135395315-e234dc5e-d891-470a-b3f4-04aa1d11ed45.mp4

## New Functionality
https://user-images.githubusercontent.com/95981350/194871840-4b8816b7-a634-4c4f-b247-293cedb932c8.mp4

## Scalability Design
The following image shows a scalability Design described in detail, and a scalability diagram to visualize how the detail would work.
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/scalability.png" width=1000> 

## Installation guide

See [INSTALL.md](https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/INSTALL.md)

## Mini tutorial
1. <u>Menu: </u> This command can be used by typing '/menu'. The bot will then display list of all commands.<br>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/menu_command.png" alt="commands" width="350"/>

2. <u>Add: </u> This command is used by typing '/add'. This command is used to add a spending record.<br>
 Once the /add command is used, the bot gives various categories, like 'Food','Groceries','Miscellaneous' and so on, to choose from. Futheromore, the bot allows user to add a personalized category if it is not present in the options. Once the category is selected, then the bot asks the user to enter the amount to be recorded. After this the Bot gives an option to split with any other user, if 'Yes' is selected the other user will be informed and the transaction would be recorded, if 'No' is selected the transaction is recorded for the current user.<br>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/add_command.png" alt="commands" width="350"/>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/add_command_1.png" alt="commands" width="350"/>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/add_command_2.png" alt="commands" width="350"/>

3. <u>Display: </u> This command is used by typing '/display'. This command is used to display the spending records for day.month or all spendings. Futhermore, the bot displays a Pie chart showing the spendings so that user can get a visual look at the spendings numbers.<br>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/display_1.png" alt="commands" width="350"/>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/display_2.png" alt="commands" width="350"/>

4. <u>History: </u> This command is used by typing '/history'. This command is used to display history of all the spending records. Futhermore, the bot displays a Bar graph showing the spendings over all the months, so that user can analyze the spendings.<br>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/history%20command.png" alt="commands" width="350"/>

5. <u>Limits: </u> This command is used by typing '/limit'. This command is used to set daily, monthly, yearly limits for user. Futhermore, this command also has a view limits feature that allows user to view limits.
- Add a limit:
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/tlimit1.png" alt="commands" width="350"/>
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/tlimit2.png" alt="commands" width="350"/>

- View limits:
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/tviewlims.png" alt="commands" width="350"/>

6. <u>Categorical Limits: </u> This command is used by typing '/limitcategory'. This command is used to set monthly categorical limits for user. Furthermore, this command also has a view limits feature that allows user to see their monthly categorical limits.
- Add a categorical limit:
<img src="https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/images/tlimc1.png" alt="commands" width="350"/>


## Case Studies
1) Tested smart spend bot code individually with all five of our members. Member 1 tested the following functionalities: add, delete, display . All of the functionalities work as intended. Last updated Dec 05 2022.
2) Tested smart spend bot code individually with all five of our members. Member 2 tested the following functionalities: edit, history, limit. All of the functionalities work as intended. Last updated Dec 05 2022.
3) Tested smart spend bot code individually with all five of our members. Member 3 tested the following functionalities: limit_cat, search. All of the functionalities work as intended. Last updated Dec 05 2022.
4) Tested smart spend bot code individually with all five of our members. Member 4 tested the following functionalities: settle. All of the functionalities work as intended. Last updated Dec 05 2022.
5) Tested smart spend bot code individually with all five of our members. Member 5 tested the following functionalities: start, website. All of the functionalities work as intended. Last updated Dec 05 2022.

## 

## Funding 
Not a funded project, nor is funding necessary.

## Contributors

This project has the following contributors:

|     | Contributor            | GitHub ID       |
| --- | ---------------------- | --------------- |
| 1   | Cheerla, Sanjana       | Stoir           |
| 2   | Ganesh, Saail Gurunath | SaailGanesh     |
| 3   | Pardeshi, Sourabh      | SourabhPardeshi |
| 4   | Patel, Maya            | maya-dc-patel   |
| 5   | Xin, Vincent           | Culcheese       |


## Contact Form and Bug Report Form
[click here](https://docs.google.com/forms/d/1cii1C1p-kijd8usQc4runQk88uT9rD750SH_IcEMuy8/edit)


