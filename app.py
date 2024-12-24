from flask import Flask, render_template, request, jsonify
from sqlmodel import SQLModel, Field, create_engine, Session
import uuid
import hashlib
from module import check_strategy_timeframe, list_strategy_folder, download_data, run_backtest
from config import *

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
    - timerange: str
    """
    id: int = Field(default=None, primary_key=True)
    uuid: str
    hash: str = Field(unique=True)  # Add unique constraint
    exchange: str
    asset: str
    strategy_name: str
    timeframe: str
    timerange: str

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
    timerange = request.form.get('timerange')

    # Create a unique hash of the data string
    data_string = f"{exchange}-{asset}-{strategy_name}-{timeframe}-{timerange}"
    data_hash = hashlib.md5(data_string.encode()).hexdigest()

    # Create a list of trading pairs (assuming asset is a single pair like "BTC/USDT")
    pair_list = [asset]
    
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
                timerange=timerange
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
        'timerange': timerange
    }

    # Download market data
    try:
        download_logs = download_data(pair_list, exchange, data_format="json", timeframe=timeframe, timerange=timerange)
    except RuntimeError as e:
        return jsonify(error=f"Error during data download: {str(e)}"), 500

    # Run backtest
    try:
        backtest_logs = run_backtest(pair_list, strategy_name, data_format="json", timerange=timerange, timeframe=timeframe, max_open_trades=3)
    except RuntimeError as e:
        return jsonify(error=f"Error during backtest: {str(e)}"), 500

    # # Redirect to results
    # return redirect(url_for("results"))

    # Return the data as a JSON response
    return jsonify(data)

  

if __name__ == '__main__':
    app.run(debug=True)