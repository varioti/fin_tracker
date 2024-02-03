import datetime
from models import CryptoManualPortfolio, CryptoPortfolioTimestamps
from utils.api_methods import get_global_balance, get_price

# Check if SUNDAY
today = datetime.date.today()
weekday = today.weekday()
if (weekday == 6):
    manual_coins = CryptoManualPortfolio.query.all()
    total_balance, _ = get_global_balance(manual_data=manual_coins)
    price_today = get_price("EUR")

    new_timestamp = CryptoPortfolioTimestamps.create(
        pf_date=today.date(),
        amount=total_balance/price_today
    )