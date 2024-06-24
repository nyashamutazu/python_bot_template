# Requirements 
## Strategy deployement
This folder contains the strategy implemented. The bot is designed to take in a dataframe of current prices ['Close', 'Open', 'High', 'Low'] which will be processed and return a trading decision, 1 = BUY, -1 = SELL, 0 = DO NOTHING. The bot will take an entry based on the previous candle high or low. 

## BUY Signals
Buy signals will be taken on the previous candle high in the form of a buy_stop

## SELL Signals
Sell signals will be taken on the previous candle low in the form of a sell_stop

