from fastapi import FastAPI,Query,Depends
from pydantic import BaseModel
import random
from faker import Faker
from datetime import datetime
from typing import Optional
#from queries import Query

app = FastAPI()
fake = Faker()

class TradePagination(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    limit: int = Query(10, ge=1, le=100, description="Number of trades per page")

class TradeSort(BaseModel):
    field: str = Query(None, description="Field to sort the trades by")
    order: str = Query(None, description="Sort order (asc or desc)")

class Trade(BaseModel):
    asset_class: str
    counterparty: str
    instrument_id: str
    instrument_name: str
    trade_date_time: str
    trade_details: dict
    trade_id: str
    trader: str

trades = []
for _ in range(10):
    trade = Trade(
        asset_class=random.choice(["Bond", "Equity", "FX"]),
        counterparty=fake.company(),
        instrument_id=fake.word(),
        instrument_name=fake.company_suffix(),
        trade_date_time=fake.iso8601(),
        trade_details={"buySellIndicator": random.choice(["BUY", "SELL"]),
                       "price": random.uniform(1, 100),
                       "quantity": random.randint(1, 100)},
        trade_id=fake.uuid4(),
        trader=fake.name(),
    )
    trades.append(trade)

@app.get("/trades")
def get_trades(
    counterparty: Optional[str] = None,
    instrument_id: Optional[str] = None,
    instrument_name: Optional[str] = None,
    trader: Optional[str] = None,
    asset_class: Optional[str] = None,
    end: Optional[datetime] = None,
    max_price: Optional[float] = Query(None, ge=0),
    min_price: Optional[float] = Query(None, ge=0),
    start: Optional[datetime] = None,
    trade_type: Optional[str] = None,
    sort: Optional[TradeSort] = None,  # Add this line
    pagination: TradePagination = Depends(),
):
    filtered_trades = trades

    if counterparty:
        filtered_trades = [
            trade for trade in filtered_trades if trade.counterparty == counterparty
        ]
        #print('trades:', trades, 'type of data', type(trades))

    if instrument_id:
        filtered_trades = [
            trade for trade in filtered_trades if trade.instrument_id == instrument_id
        ]

    if instrument_name:
        filtered_trades = [
            trade for trade in filtered_trades if trade.instrument_name == instrument_name
        ]

    if trader:
        filtered_trades = [
            trade for trade in filtered_trades if trade.trader == trader
        ]

    if asset_class:
        filtered_trades = [
            trade for trade in filtered_trades if trade.asset_class == asset_class
        ]

    if end:
        filtered_trades = [
            trade for trade in filtered_trades if trade.trade_date_time <= end
        ]

    if max_price is not None:
        filtered_trades = [
            trade for trade in filtered_trades if trade.trade_details.price <= max_price
        ]

    if min_price is not None:
        filtered_trades = [
            trade for trade in filtered_trades if trade.trade_details.price >= min_price
        ]

    if start:
        filtered_trades = [
            trade for trade in filtered_trades if trade.trade_date_time >= start
        ]

    if trade_type:
        filtered_trades = [
            trade for trade in filtered_trades if trade.trade_details.buySellIndicator == trade_type
        ]
     # Apply sorting
    if sort and sort.field and sort.order:
        reverse = False
        if sort.order.lower() == "desc":
            reverse = True
        filtered_trades = sorted(filtered_trades, key=lambda trade: getattr(trade, sort.field), reverse=reverse)

    # Apply pagination
    start_idx = (pagination.page - 1) * pagination.limit
    end_idx = start_idx + pagination.limit
    paginated_trades = filtered_trades[start_idx:end_idx]

    return paginated_trades


    #return filtered_trades


@app.get("/trades/{trade_id}")
def get_trade_by_id(trade_id: str):
    for trade in trades:
        if trade.trade_id == trade_id:
            return trade
    return {"error": "Trade not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
