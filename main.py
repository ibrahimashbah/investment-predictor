from os import TMP_MAX, access, close, rename
from pandas.core.frame import DataFrame
import streamlit as st
from datetime import date
from traitlets.traitlets import Instance
import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import pandas as pd
from plotly import graph_objs as go
from collections import Counter
import time
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
import requests
import tickerfile

# Page configration details
st.set_page_config(
    page_title="Portfolio Forecast",
    page_icon="📊",
)

# Hiding uncessery streamlit elements
hide_st_style = """
            <style>
            # MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# nav bar
st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)
st.markdown("""
<nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #002D40;">
  <a class="navbar-brand" href="http://ibrahimashbah.de/" target="_blank">Ibrahim Ashbah</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
      <li class="nav-item active">
        <a class="nav-link" href="http://ibrahimashbah.de/" target="_blank">Home</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="https://www.linkedin.com/in/ibrahim-al-ashbah/" target="_blank">LinkedIn</a>
    </ul>
  </div>
</nav>
""", unsafe_allow_html=True)

html_card_header1 = """
    <div class="card">
    
    <div class="card-body" style="border-radius: 0px 0px 0px 0px; background:#1AA6B7; padding-top: 5px; width: 250px; height: 50px;">
        <h5 class="card-title" style="background-color:#1AA6B7; color:#ffffff; font-family:sans serif; text-align: center; padding: 8px 0;">Investment value</h5>
    </div>
    </div>
    """
html_card_header2 = """
    <div class="card">
    
    <div class="card-body" style="border-radius: 0px 0px 0px 0px; background:#1AA6B7; padding-top: 5px; width: 250px; height: 50px;">
        <h5 class="card-title" style="background-color:#1AA6B7; color:#ffffff; font-family:sans serif; text-align: center; padding: 8px 0;">Gains/Losses</h5>
    </div>
    </div>
    """


# Load Market Data
read_tickers = pd.read_csv(
    "https://raw.githubusercontent.com/ibrahimashbah/stock-predictor-app/main/scripts_list.csv")
stocks = read_tickers['SYMBOL']


# Creating form so streamlit will not rerun the whole page with every single action
with st.sidebar.form(key='my_form'):

    # selecting stocks
    selected_stock = st.multiselect(
        "Your favorite stocks (3 max)", stocks)

    # getting the symbol between brackets -> return list
    def extract_symbol():
        cleaned = []
        for i in range(len(selected_stock)):
            cleaned.append(str(selected_stock[i]).split('(')[1][:-1])
        return cleaned

    ticker = extract_symbol()

    # investment duration
    duration = st.number_input(
        'Years of prediction ', min_value=1, max_value=4, step=1)
    period = duration * 365

    # investment Value
    investment_Value = st.number_input(
        'Investment value ', min_value=0, max_value=1000000000, step=50000)

    # Predict button
    Predict_button = st.form_submit_button(label='Predict 📊')

st.sidebar.markdown("")
st.sidebar.markdown("")


# Title
st.markdown('''# **Portfolio Forecast 📊 **
A portfolio forecast app to predict its estimated value in the future.
''')

# introductry video
# with st.expander("Watch (30-seconds) overview video"):
#     st.video("https://youtu.be/qZWW2rMjKG4")

# for stopping autorun from streamlit
if Predict_button == False:
    st.info(
        'On the left sidebar, set your preferred values then Hit the "Predict" button')
elif Predict_button == True:

    if len(selected_stock) == 0:
        st.sidebar.warning("please choose stocks to predict")
        st.stop()
    elif len(selected_stock) > 3:
        st.sidebar.warning("you can select 3 stocks at max")
        st.stop()
    if investment_Value == 0 or investment_Value > 1000000000:
        st.sidebar.warning("please set your investment value")
        st.stop()

    START = "2019-01-01"
    TODAY = date.today().strftime("%Y-%m-%d")

    graph_placeholder = st.empty()
    graph_placeholder.warning(
        "We are fetching live data and cooking +3 years of historical data, please wait...⌛")

    def load_stocks_data(tickers_list):
        stocks_df = []

        for i in range(len(tickers_list)):
            check_df_length = yf.download(tickers_list[i], START, TODAY)
            if (check_df_length.shape[0] < 750):
                # new_added_stock = yf.Ticker(tickers_list[i])
                st.warning(
                    f"The stock {tickers_list[i]} does not has enough historical data so we cannot predict its future, please pick another stock and hit __Predict__ button again")
                st.stop()
            stocks_df.insert(i, check_df_length)
        return stocks_df

    stocks_data = load_stocks_data(ticker)

    # getting the average stock price of selected stocks
    list_of_avg_close_price = []
    list_of_dates = []
    to_get_date_column = stocks_data[0].reset_index()
    for i in range(stocks_data[0].shape[0]):
        stocks_counter = 0
        total_price = 0
        avg_price = 0
        if stocks_data[0]["Close"][i] != 0:
            for k in range(len(selected_stock)):
                total_price += stocks_data[k]["Close"][i]
            avg_price = total_price/len(selected_stock)
            list_of_dates.insert(i, to_get_date_column["Date"][i])
            list_of_avg_close_price.insert(i, avg_price)

    average_data = pd.DataFrame(
        {'Date': list_of_dates, 'Close': list_of_avg_close_price})

    # Forecasting

    # Preparing data for model
    df_train = average_data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    # Training
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    # calculating new investment value and profit/loss
    forecasted_value = pd.DataFrame(forecast.values)
    new_investment_value = investment_Value * \
        (forecasted_value.iloc[-1][1])/(list_of_avg_close_price[-1])
    profit_change = (new_investment_value-investment_Value) / \
        new_investment_value*100
    gain_loss = (new_investment_value-investment_Value)

    # making spcae for two boxes
    st.markdown("")  # empty row
    st.markdown("")  # empty row
    col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 3, 1])
    with col2:
        st.markdown(html_card_header1, unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Indicator(
            mode="number+delta",
            value=new_investment_value,
            number={'prefix': "$", 'valueformat': ',f'},
            delta={'reference': investment_Value,
                   'relative': True, 'valueformat': '.0%'},
            domain={'x': [0, 1], 'y': [0, 1]}))
        fig1.update_layout(autosize=False,
                           width=250, height=100, margin=dict(l=20, r=20, b=20, t=30),
                           paper_bgcolor="#eaf2f4", font={'size': 20})
        st.plotly_chart(fig1)

    with col4:
        st.markdown(html_card_header2, unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Indicator(
            mode="number+delta",
            value=gain_loss,
            number={'prefix': "$", 'valueformat': ',f'},

            domain={'x': [0, 1], 'y': [0, 1]}))
        fig2.update_layout(autosize=False,
                           width=250, height=100, margin=dict(l=20, r=20, b=20, t=30),
                           paper_bgcolor="#eaf2f4", font={'size': 20})
        st.plotly_chart(fig2)

    st.markdown("")  # empty row
    st.markdown("")  # empty row
    st.subheader("__Prediction graph__")

    # Plotting prediction graph
    fig3 = plot_plotly(m, forecast)
    fig3.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Median Price",
        margin=dict(l=10, r=10, b=1, t=10),
    )
    fig3.update_xaxes(rangeslider_visible=False)

    st.plotly_chart(fig3, use_container_width=True)
    graph_placeholder.write("")  # hide warning box

    with st.expander("How the model (Prophet) works?"):
        st.write("""
        Prophet is a procedure for forecasting time series data based on an additive model.

        Prophet use a decomposable time series model with three main
        model components: trend, seasonality, and holidays. They are combined in the following
        equation:
        """)
        st.latex(r'''
        y(t)= g(t) + s(t) + h(t) + εt
        ''')

        st.markdown("""
                Here _g(t)_ is the trend function which models non-periodic changes in the value of the
            time series, _s(t)_ represents periodic changes (e.g., weekly and yearly seasonality), and
            _h(t)_ represents the effects of holidays which occur on potentially irregular schedules over
            one or more days. The error term _εt_ represents any idiosyncratic changes which are not
            accommodated by the model.

            Finally, this how the model function under the hood
        """)
        st.image("https://miro.medium.com/max/1750/1*rZeUGmzn2acsaqUc-MXcow.png")

    st.markdown("")  # empty row
    st.markdown("")  # empty row
    st.markdown("")  # empty row
    st.write("__Returns of stocks__")

    #### calculating stocks returns ####
    def relativeret(df):
        rel = df.pct_change()
        cumret = (1+rel).cumprod()-1
        cumret = cumret.fillna(0)
        return cumret

    stocks_returns = relativeret(
        yf.download(ticker, START, TODAY)['Adj Close'])
    st.line_chart(stocks_returns)

    st.markdown("")
    st.markdown("")
    st.write("__Key Information__")
    st.caption(
        "The more your investments is divertised by industry and region the less riskier it will be")
    st.markdown("")

    # get key information then add convert it to dictionary for plotting purpose
    # list_of_sectors = []
    # list_of_regions = []
    # list_of_industries = []
    # for i in range(len(selected_stock)):
    #     access_ticker = yf.Ticker(ticker[i])
    #     add_industry = access_ticker.info['industry']
    #     add_region = access_ticker.info['country']
    #     add_sector = access_ticker.info['sector']
    #     list_of_sectors.append(add_sector)
    #     list_of_industries.append(add_industry)
    #     list_of_regions.append(add_region)

    # sectors = dict(Counter(list_of_sectors))
    # industries = dict(Counter(list_of_industries))
    # regions = dict(Counter(list_of_regions))

    if __name__ == '__main__':
        with Pool(len(ticker)) as p:
            ticker_cache = p.map(tickerfile.get_ticker, ticker)

    k = len(ticker)

    sectors = defaultdict(int)
    industries = defaultdict(int)
    regions = defaultdict(int)
    for i, _ in enumerate(ticker):
        sectors[ticker_cache[i]['sector']] += 1
        industries[ticker_cache[i]['industry']] += 1
        regions[ticker_cache[i]['country']] += 1

    # building up risk meter value

    def meter_generator(investment, industries, regions):
        meter = 1
        if investment <= -9:
            meter += 5
        elif investment > -9 and investment < -3:
            meter += 4
        elif investment >= -3 and investment < 0:
            meter += 2
        elif investment >= 0 and investment < 5:
            meter += 1
        if len(industries) < len(ticker):
            diffrence = len(ticker)-len(industries)
            meter += diffrence
        if len(regions) < len(ticker):
            meter += 1
        return meter

    col1, col2, col3 = st.sidebar.columns([2, 6, 2])

    with col1:
        st.write("")

    with col2:
        final_meter = meter_generator(
            profit_change, industries, regions)
        if final_meter <= 1:
            st.image(
                "https://github.com/ibrahimashbah/stock-predictor-app/raw/main/imgs/Riskometer%2016.png", width=170)
        elif final_meter == 2:
            st.image(
                "https://github.com/ibrahimashbah/stock-predictor-app/raw/main/imgs/Riskometer%2026.png", width=170)
        elif final_meter == 3:
            st.image(
                "https://github.com/ibrahimashbah/stock-predictor-app/raw/main/imgs/Riskometer%2036.png", width=170)
        elif final_meter == 4:
            st.image(
                "https://github.com/ibrahimashbah/stock-predictor-app/raw/main/imgs/Riskometer%2046.png", width=170)
        elif final_meter == 5:
            st.image(
                "https://github.com/ibrahimashbah/stock-predictor-app/raw/main/imgs/Riskometer%2056.png", width=170)
        elif final_meter >= 6:
            st.image(
                "https://github.com/ibrahimashbah/stock-predictor-app/raw/main/imgs/Riskometer%2066.png", width=170)

    with col3:
        st.write("")

     # plotting key information in pie charts
    pies = st.columns(7)
    with pies[0]:
        labels = list(sectors.keys())
        values = list(sectors.values())

        # Use `hole` to create a donut-like pie chart
        fig4 = go.Figure(data=[go.Pie(
            labels=labels, values=values, title='Sector', hole=.6)])
        fig4.update_layout(showlegend=False,
                           width=160,
                           height=160,
                           margin=dict(l=1, r=1, b=1, t=1),
                           font=dict(color='#383635', size=15))
        fig4.update_traces(textposition='inside', textinfo='label')
        st.plotly_chart(fig4)
    with pies[2]:
        labels = list(industries.keys())
        values = list(industries.values())

        # Use `hole` to create a donut-like pie chart
        fig5 = go.Figure(
            data=[go.Pie(labels=labels, values=values, title='Industry', hole=.6)])
        fig5.update_layout(showlegend=False,
                           width=160,
                           height=160,
                           margin=dict(l=1, r=1, b=1, t=1),
                           font=dict(color='#383635', size=15))
        fig5.update_traces(textposition='inside', textinfo='label')
        st.write(fig5)
    with pies[4]:
        labels = list(regions.keys())
        values = list(regions.values())

        # Use `hole` to create a donut-like pie chart
        fig6 = go.Figure(
            data=[go.Pie(labels=labels, values=values, title='Region', hole=.6)])
        fig6.update_layout(showlegend=False,
                           width=160,
                           height=160,
                           margin=dict(l=1, r=1, b=1, t=1),
                           font=dict(color='#383635', size=15))
        fig6.update_traces(textposition='inside', textinfo='label')
        st.write(fig6)

    st.markdown("")  # empty row
    st.markdown("")  # empty row

    with st.expander("What are the necessery skills to build like this app? "):
        st.write("""
                - Web Scrabing ✅
                - Data Cleaning & Wrangling ✅
                - Large Data extraction and manuplation from Excel/SQL ✅
                - Coding knowledge with several languages: Python, HTML/CSS, Jave ✅
                - Good mathematical, data analytics and problem solving skills ✅
                - Knowledge of advanced statistical techniques and concepts ✅
                - Analyze model performance and data accuracy ✅
                - Familiar with Machine Learning techniques, Pandas, NumPy and SciPy ✅
        """)
    st.info(
        "This app is maintained by Ibrahim Ashbah. You can learn more about me at [ibrahimashbah](https://www.linkedin.com/in/ibrahimashbah/).")
    st.stop()
