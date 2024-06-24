# Free Metatrader 5 trading bot (Expert Advisor)
This respository contains python files for a free MetaTrader5(MT5) trading bot. This README file will help to set up the bot: I have listed all the commands, requirments and helpers to date that will help support the process. 

## Requirements 
- Windows 10 or above endpoint (for whatever reason, MetaTrader doesn't support their Python API on macOS or Linux)
- Access to a Online CFD Trading broker, with permission to trade
- MetaTrader 5 (note MetaTrader 4 doesn't have a Python API)
- A basic knowledge of Python, such as functions and variables
- Python 3 installed

## Getting started
- Download MetaTrader5
- Create a Demo trading account (Demo), else get Live trading account (Live)
- Create a virtual envrionment
- Update bot credentials
- Update bot settings
- Deploy strategy 

## Download MetaTrader5
1. [MetaTrater 5](https://www.metatrader5.com/en/download)
2. Update `./constants/defs.py` file with metatrader path

## Create a venv 
1. Create a virtual environment 
`python -m venv /path/to/new/virtual/environment`
2. Pull files from requirements 
`pip install -r requirements.txt`
3. Optionally install TA-Lib for pandas_ta
`pip install TA-Lib`
4. If attempted installing TA-Lib but failed download [Anaconda](https://www.anaconda.com/)

## Update bot credetials
1. Connect your broker, for example, [vantage](https://secure.vantagemarkets.com/login) and create an account 
2. Update `./constants/credentials.py` file 

## Update bot settings
1. Bot settings can be updated in `./bot/settings.json`

## Deploy strategy
1. Follow instructions `./strategy/README.md` to deploy strategy
2. You want to deploy your strategy into `./strategy/strategy.py`
