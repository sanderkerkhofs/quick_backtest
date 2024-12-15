from flask import Flask, render_template, request, jsonify
from sqlmodel import SQLModel, Field, create_engine, Session
import uuid
import hashlib

# Define the model
class TradeData(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    uuid: str
    hash: str = Field(unique=True)  # Add unique constraint
    exchange: str
    asset: str
    strategy_name: str
    timeframe: str
    time_period: str

app = Flask(__name__)

# Database setup
DATABASE_URL = "sqlite:///trade_data.db"
engine = create_engine(DATABASE_URL)

# Create the database tables
SQLModel.metadata.create_all(engine)

@app.route('/')
def home():
    return render_template('single_asset.html')

@app.route('/process/single', methods=['POST'])
def process_single():
    unique_id = uuid.uuid4().hex[:16]
    exchange = request.form.get('exchange')
    asset = request.form.get('asset')
    strategy_name = request.form.get('strategy_name')
    timeframe = request.form.get('timeframe')
    time_period = request.form.get('time_period')

    data_string = f"{exchange}-{asset}-{strategy_name}-{timeframe}-{time_period}"
    data_hash = hashlib.md5(data_string.encode()).hexdigest()

    # Check if the hash already exists in the database
    with Session(engine) as session:
        existing_trade = session.query(TradeData).filter(TradeData.hash == data_hash).first()
        if existing_trade:
            return jsonify({"error": "Duplicate entry. This hash already exists."}), 400

        # Create an instance of the TradeData model
        trade_data = TradeData(
            uuid=unique_id,
            hash=data_hash,
            exchange=exchange,
            asset=asset,
            strategy_name=strategy_name,
            timeframe=timeframe,
            time_period=time_period
        )

        # Save the data to the database
        session.add(trade_data)
        session.commit()

    data = {
        'uuid': unique_id,
        'hash': data_hash,
        'exchange': exchange,
        'asset': asset,
        'strategy_name': strategy_name,
        'timeframe': timeframe,
        'time_period': time_period
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)