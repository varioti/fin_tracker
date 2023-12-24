from app.utils.api_methods import get_price
from datetime import datetime

def deposit_totals(transactions):
    """
    Computes the total of deposits, withdraw and the total balance

    Parameters:
    -----------
    - transactions (list) : list of all transactions (Type: CryptoTransactions)

    Returns:
    --------
    - total_deposit (float) : positive value
    - total_withdraw (float) : positive value
    - total_balance (float) : positive or negative value (W - D)
    """
    total_deposit = 0
    total_withdraw = 0
    total_balance = 0
    for tr in transactions:
        amount = round(tr.amount ,2)
        if amount < 0:
            total_deposit -= amount
        else:
            total_withdraw += amount

        total_balance += amount

    return round(total_deposit,2), round(total_withdraw,2), round(total_balance,2)

def deposit_evolution(transactions):
    """
    Computes the total of deposits, withdraw and the total balance

    Parameters:
    -----------
    - transactions (list) : list of all transactions (tuple)

    Returns:
    --------
    - dates (list) : date value for each value in the evolution list
    - evolution (list) : amount at the correspondant date
    """
    evolution = [0]
    dates = ["2020-12-15"]
    cumul_amount = 0

    for i in range(len(transactions)):
        tr = transactions[len(transactions)-1-i]
        date = str(tr.deposit_date)
        amount = round(tr.amount ,2)
        cumul_amount += amount


        size_list = len(dates)
        if size_list != 0 and date == dates[size_list - 1]:
            evolution[size_list-1] = cumul_amount
        else:
            evolution.append(cumul_amount)
            dates.append(date)

    dates.append(datetime.today())
    evolution.append(cumul_amount)

    return dates,evolution

def earn_evolution(balance, portfolio):
    """
    Computes the total of deposits, withdraw and the total balance

    Parameters:
    -----------
    - balance (list) : dates and amount of the balance
    - portfolio (list) : portfolio table (CryptoPortfolioTimestamps)
    - starting_date (str) : date of the first deposit

    Returns:
    --------
    - dates (list) : date value for each value in the evolution list
    - evo_pf (list) : amount of portfolio at the correspondant date
    - evo_earn (list) : amount of earning at the correspondant date
    """
    evo_pf = []
    evo_earn = []
    dates = []
    current_index = 0

    portfolio = sorted(portfolio, key=lambda x: x.pf_date)
    nb_timestamps = len(portfolio)

    for i in range(nb_timestamps):
        timestamp = portfolio[i]
        date = str(timestamp.pf_date)

        # Compute earning
        if str(balance[0][current_index])[:10] < date[:10] :
            while current_index < len(balance[1])-1 and str(balance[0][current_index+1])[:10] <= date:
                current_index += 1

        dates.append(date)
        evo_pf.append(timestamp.amount)
        evo_earn.append(timestamp.amount + balance[1][current_index])

    return dates, evo_pf, evo_earn








