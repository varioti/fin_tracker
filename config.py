from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

SECRET_KEY=os.getenv('SECRET_KEY')

# MySQL Database configuration ###################
DB_HOST=os.getenv('DB_HOST')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')
DB_PORT=os.getenv('DB_PORT')

# APIs ############################################
## BINANCE
BINANCE_API_KEY=os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET=os.getenv('BINANCE_API_SECRET')

## ETHERSCAN
ETHERSCAN_API_KEY=os.getenv('ETHERSCAN_API_KEY')
ETHERSCAN_ADDRESS=os.getenv('ETHERSCAN_ADDRESS')

## BLOCKCHAIN.COM
BTC_ADDRESS=os.getenv('BTC_ADDRESS')