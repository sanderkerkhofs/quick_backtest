from flask import Flask, render_template, request, jsonify
from sqlmodel import SQLModel, Field, create_engine, Session
import uuid
import hashlib
from module import check_timeframe, list_strategy_folder, download_data, run_backtest, read_latest_backtest
from models import TradeData, BacktestData
from config import *
import plotly.express as px
import plotly.io as pio


app = Flask(__name__)

# Database setup
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

    # Check if the timeframe is "strategy_default" or regular timeframe like 5m etc
    timeframe = check_timeframe(strategy_file=f"{LOCAL_STRATEGY_DIR}{strategy_name}.py", timeframe=timeframe)    

    # Create a list of trading pairs (assuming asset is a single pair like "BTC/USDT")
    pair_list = [asset]

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

    # Read latest backtest
    backtest_data = read_latest_backtest(results_dir=LOCAL_RESULTS_DIR, backtest_uuid=unique_id, backtest_hash=data_hash)

    # Create a BacktestData instance
    backtest_instance = BacktestData(**backtest_data)

    # Insert the data into the database
    with Session(engine) as session:
        session.add(backtest_instance)
        session.commit()

    # Return the data as a JSON response
    return jsonify(backtest_data)

@app.route('/plotly')
def plotly():
    # Create a Plotly figure
    df = px.data.gapminder()  # Example data
    fig = px.scatter(df, x='gdpPercap', y='lifeExp', color='continent', size='pop', hover_name='country', log_x=True, size_max=60)
    
    # Convert the Plotly figure to HTML
    graph_html = pio.to_html(fig, full_html=False)
    
    # Render the graph in a template
    return render_template('plotly_page.html', graph_html=graph_html)

  

if __name__ == '__main__':
    app.run(debug=True)