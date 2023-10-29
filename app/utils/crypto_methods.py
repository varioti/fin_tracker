from app.utils.api_methods import get_price
from datetime import datetime

def deposit_totals(transactions, index):
    """
    Computes the total of deposits, withdraw and the total balance

    Parameters:
    -----------
    - transactions (list) : list of all transactions (tuple)
    - index (int) : index where are the amount values in the tuples

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
        amount = round(tr[index],2)
        if amount < 0:
            total_deposit -= amount
        else:
            total_withdraw += amount

        total_balance += amount

    return round(total_deposit,2), round(total_withdraw,2), round(total_balance,2)

def deposit_evolution(transactions, index_date, index_amount):
    """
    Computes the total of deposits, withdraw and the total balance

    Parameters:
    -----------
    - transactions (list) : list of all transactions (tuple)
    - index_date (int) : index where are the date values in the tuples
    - index_amount (int) : index where are the amount values in the tuples
    - evo_pf (list) : list of dates and list of amounts

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
        date = str(tr[index_date])
        amount = round(tr[index_amount],2)
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

def pf_evolution(portfolio, index_date, index_amount):
    """
    Computes the total of deposits, withdraw and the total balance

    Parameters:
    -----------
    - portfolio (list) : portfolio table (date and amount)
    - index_date (int) : index where are the date values in the tuples
    - index_amount (int) : index where are the amount values in the tuples

    Returns:
    --------
    - dates (list) : date value for each value in the evolution list
    - evo_pf (list) : amount of portfolio at the correspondant date
    """
    pf_inverse = reversed(portfolio)
    dates = [x[1] for x in pf_inverse]
    pf_inverse = reversed(portfolio)
    evo_pf = [x[2] for x in pf_inverse]

    return dates, evo_pf

def earn_evolution(balance, portfolio):
    """
    Computes the total of deposits, withdraw and the total balance

    Parameters:
    -----------
    - balance (list) : dates and amount of the balance
    - portfolio (list) : portfolio table (date and amount)

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

    for i in range(len(portfolio)):
        line = portfolio[len(portfolio)-1-i]
        date = str(line[1])

        # Compute earning
        if str(balance[0][current_index])[:10] < date[:10] :
            while current_index < len(balance[1])-1 and str(balance[0][current_index+1])[:10] <= date:
                current_index += 1

        dates.append(date)
        evo_pf.append(line[2])
        evo_earn.append(line[2]+balance[1][current_index])

    return dates, evo_pf, evo_earn

def get_track_balances(dico, asset="USD"):
    new_dico = {}
    totals = {}
    for name, table in dico.items():
        totals[name] = 0
        new_dico[name] = {}

        for row in table :
            tot = get_price(row[1],asset)*float(row[2])
            new_dico[name][row[1]] = {"asset":row[1],"amount":float(row[2]),"usd":tot}
            totals[name] += tot

    print(dico)
    return new_dico, totals








