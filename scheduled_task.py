import datetime
from app.models import CryptoAutoPortfolio, CryptoManualPortfolio, CryptoPortfolioTimestamps
from app.utils.api_methods import get_global_balance, get_price

# Each day
_, assets = get_global_balance()

# Truncate CryptoAutoPortfolio in order to reload it
CryptoAutoPortfolio.query.delete()

# Fill CryptoAutoPortfolio with refreshed data
for asset, asset_data in assets.items():
    CryptoAutoPortfolio.create(
        asset=asset,
        amount=asset_data['amount'],
        platform=asset_data['platform'],
    )
    print(f"{asset} added")

# Check if SUNDAY
today = datetime.date.today()
weekday = today.weekday()
if (weekday == 6):
    manual_coins = CryptoManualPortfolio.query.all()
    total_balance, assets = get_global_balance(manual_data=manual_coins)
    price_today = get_price("EUR")

    new_timestamp = CryptoPortfolioTimestamps.create(
        pf_date=today,
        amount=total_balance/price_today
    )
