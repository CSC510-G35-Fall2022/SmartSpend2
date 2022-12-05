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


### <u>Additions:</u>
- Fixed several bugs related to parsing and tracking.
- Refactored old code to suit updated structure.
- - Previously all of the code was in a single file with around 650 lines. This appeared messy and was hard to edit parts of the program.
- - Attempted one refactor method which can be seen in [this branch](https://github.com/CSC510-G35-Fall2022/SmartSpend2/tree/refactor). This method was too time consuming and required more of the codebase to be refactored.
- - Tried another refactor method, much faster, worked simpler, did not need to update more of the code base. This has been merged to main.
- Moved away from Travis to GitHub actions for rolling builds.
- <u>Feature</u> -> Add 'limit_category' feature to work as an alarm when spending exceed preset limits.
- - Users can create limits on the existing categories, food, groceries, utilities, ...
- - When user adds an expense, limit categories, and all all three existing limits are checked.
- - Ability to view limits for categories.
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

## Installation guide

See [INSTALL.md](https://github.com/CSC510-G35-Fall2022/SmartSpend2/blob/main/INSTALL.md)

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


