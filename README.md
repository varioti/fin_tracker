# Crypto Tracker Web Application

The Crypto Tracker is a web application designed to help you manage your cryptocurrency investments. It allows you to track your cryptocurrency portfolio, record transactions, and monitor the performance of your investments over time.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)


## Features

- **Portfolio Management**: Keep track of your cryptocurrency holdings and view your portfolio's current value.

- **Transaction Recording**: Export and monitor your cryptocurrency buy and sell transactions from Binance, including transaction date, amount, and price.

- **Performance Monitoring**: Analyze the performance of your investments with detailed statistics, including the average buy price, total investment, and profit/loss.


## Getting Started

### Prerequisites

Before you can run this application, ensure you have the following prerequisites installed on your system:

- Python 3
- Flask
- MySQL (or other supported database)
- Any additional dependencies specified in the `requirements.txt` file.

### Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/crypto-tracker.git
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a MySQL database for your application.


5. Run the application:

   ```bash
   flask run
   ```

The application should now be running locally at http://127.0.0.1:5000.


## Configuration

### Environment Variables

Sensitive information such as database connection settings and API keys should be stored in a `.env` file. Create a `.env` file in the project directory and add the following variables:

```
# Flask Configuration ############################
SECRET_KEY=

# MySQL Database Configuration ###################
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_PORT=

# APIs ############################################
## BINANCE
BINANCE_API_KEY=
BINANCE_API_SECRET=

## ETHERSCAN
ETHERSCAN_API_KEY=
ETHERSCAN_ADDRESS=

## BLOCKCHAIN.COM
BTC_ADDRESS=
```
In order to use this app, an API key from Binance is needed (Binance is used to gather information like current prices). However, Etherscan and Blockchain variables can be left empty.

The `.env` file should not be shared or committed to version control to keep your sensitive information secure.