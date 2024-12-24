from flask import Flask, render_template, request, jsonify
from sqlmodel import SQLModel, Field, create_engine, Session
import uuid
import hashlib
from module import check_strategy_timeframe, list_strategy_folder
from config import *

# # Define file paths for configuration and data directories
# LOCAL_DATA_DIR = "/home/ubuntu/_DATA/"
# REMOTE_DATA_DIR = "/freqtrade/user_data/data/"
# LOCAL_STRATEGY_DIR = "C:\\_STRATEGIES\\TESTED\\"
# REMOTE_STRATEGY_DIR = "/freqtrade/user_data/strategies/"
# LOCAL_CONFIG_DIR = "/home/ubuntu/_CONFIGS/"
# REMOTE_CONFIG_DIR = "/freqtrade/user_data/config/"
# LOCAL_RESULTS_DIR = "/home/ubuntu/_BACKTEST_RESULTS/"
# REMOTE_RESULTS_DIR = "/freqtrade/user_data/backtest_results/"

# Define the model
class TradeData(SQLModel, table=True):
    """
    Define the TradeData model with the following columns:
    - id: int, primary key, auto-incrementing
    - uuid: str, unique identifier
    - hash: str, unique hash of the data string, with a unique constraint
    - exchange: str
    - asset: str
    - strategy_name: str
    - timeframe: str
    - time_period: str
    """
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
    """
    Render the single asset template
    """

    strategy_list = list_strategy_folder(LOCAL_STRATEGY_DIR)

    return render_template('single_asset.html', strategy_list=strategy_list, trading_pairs=TRADING_PAIRS)

@app.route('/process/single', methods=['POST'])
def process_single():
    """
    Process the single asset form submission
    """
    unique_id = uuid.uuid4().hex[:16]
    exchange = request.form.get('exchange')
    asset = request.form.get('asset')
    strategy_name = request.form.get('strategy_name')
    timeframe = request.form.get('timeframe')
    time_period = request.form.get('time_period')

    # Create a unique hash of the data string
    data_string = f"{exchange}-{asset}-{strategy_name}-{timeframe}-{time_period}"
    data_hash = hashlib.md5(data_string.encode()).hexdigest()

    
    # Check if the timeframe is "strategy_default" and if so, 
    # call the check_strategy_timeframe function
    if timeframe == "strategy_default":
        timeframe = check_strategy_timeframe(f"{LOCAL_STRATEGY_DIR}{strategy_name}.py")

    # Save the data to the database using INSERT OR IGNORE
    with Session(engine) as session:
        # Use the INSERT OR IGNORE statement to avoid duplicate entries
        session.execute(
            TradeData.__table__.insert().values(
                uuid=unique_id,
                hash=data_hash,
                exchange=exchange,
                asset=asset,
                strategy_name=strategy_name,
                timeframe=timeframe,
                time_period=time_period
            ).prefix_with('OR IGNORE')
        )
        session.commit()

    # Prepare data for json response
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