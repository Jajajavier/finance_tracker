# finance_tracker
Simple finance tracker with database in .txt and GitHub integration to save your transactions to a private repository

## How to use
1. Run the program with python 3.8 or higher
```bash
python finance_tracker.py
```
2. Start with your initial balance
3. Add income or expense

# How to use GitHub integration
1. Create a private repository on GitHub example: 'yourusername/myfinance'
2. Generate a personal access token with repo access under settings, save it in a safe place
3. When running the program, when selecting the option to save to GitHub, enter your repository name and personal access token when requested, those will be saved to a file in the same directory as the program
### Note: The program will not save your personal access token in the file
### Note: When using in multiple devices you might end overwriting changes to your transactions repository, you can delete the transactions file and just hit the Sync option to get the latest transactions from the repository


## Features
- Add income
- Add expense
- Show balance at any date
- Edit income/expense
- Duplicate income/expense
- Sort entries by datetime on new line
- Save entries to plain text file
- GitHub integration to save your transactions to a private repository


# Feel free to contribute
