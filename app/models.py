from app import db
from app.utils.api_methods import get_price

class BaseModel(db.Model):
    __abstract__ = True

    @classmethod
    def create(cls, **kwargs):
        record = cls(**kwargs)
        db.session.add(record)
        db.session.commit()
        return record

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Coin(BaseModel):
    __tablename__ = 'crypto_historic'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    coin = db.Column(db.String(255), nullable=False)
    total_bought = db.Column(db.Float)
    mean_bought = db.Column(db.Float)
    total_sold = db.Column(db.Float)
    mean_sold = db.Column(db.Float)
    last_tr_total = db.Column(db.Float)
    last_tr_mean = db.Column(db.Float)

    def getBuyTotal(self):
        return round(self.total_bought,2)

    def getBuyMean(self):
        return round(self.mean_bought,4)

    def getSellTotal(self):
        return round(self.total_sold,2)

    def getSellMean(self):
        return round(self.mean_sold,4)

    def getLastTransaction(self):
        return (str(self.last_tr_total) + " @ " + str(self.last_tr_mean))

    def getPrice(self):
        return get_price(self.coin)

    def getBuyMargin(self):
        buy_margin = (self.getPrice() - self.mean_bought)/self.mean_bought*100
        return round(buy_margin,2)

    def getSellMargin(self):
        sell_margin = (self.getPrice() - self.mean_sold)/self.mean_sold*100
        return round(sell_margin,2)

class CryptoPortfolio(BaseModel):
    __tablename__ = 'crypto_portfolio'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    pf_date = db.Column(db.Date)
    amount = db.Column(db.Float)

class CryptoTrackerBinanceManual(BaseModel):
    __tablename__ = 'crypto_tracker_binancemanual'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    asset = db.Column(db.String(5))
    amount = db.Column(db.Float)

class CryptoTrackerSocios(BaseModel):
    __tablename__ = 'crypto_tracker_socios'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    asset = db.Column(db.String(5))
    amount = db.Column(db.Float)

class CryptoTransactions(BaseModel):
    __tablename__ = 'crypto_transactions'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float)
    deposit_date = db.Column(db.Date)
    exchange = db.Column(db.String(255))