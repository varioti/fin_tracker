import decouple as dc

SECRET_KEY=dc.config('SECRET_KEY')

# MySQL Database configuration ###################
DB_HOST=dc.config('DB_HOST')
DB_USER=dc.config('DB_USER')
DB_PASSWORD=dc.config('DB_PASSWORD')
DB_NAME=dc.config('DB_NAME')
DB_PORT=dc.config('DB_PORT')

# APIs ############################################
## BINANCE
BINANCE_API_KEY=dc.config('BINANCE_API_KEY')
BINANCE_API_SECRET=dc.config('BINANCE_API_SECRET')

## ETHERSCAN
ETHERSCAN_API_KEY=dc.config('ETHERSCAN_API_KEY')
ETHERSCAN_ADDRESS=dc.config('ETHERSCAN_ADDRESS')

## BLOCKCHAIN.COM
BTC_ADDRESS=dc.config('BTC_ADDRESS')