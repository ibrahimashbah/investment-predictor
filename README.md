# Investment Predictor

Welcome to the **Investment Predictor** project! This web application allows users to analyze historical stock prices and predict future values using advanced time series forecasting techniques. Below are the key features and details about the project:


## Features

- **Data Extraction**: Utilizes the Yahoo Finance API to extract financial data, leveraging Python libraries such as Pandas and NumPy for data manipulation.
- **Decomposable Time Series Model**: Trains stock data using the Prophet library to forecast future stock prices based on historical trends, seasonality, and holidays.
- **Visualizations**: Generates various plots and visualizations to present the model predictions and stock performance.
- **Web Application**: Built using Streamlit, the application is deployed on Heroku, allowing for a user-friendly experience to interact with investment predictions.

## Technical Details

The application is structured to include the following key components:

- **Data Collection**: A streaming script collects financial data, ensuring a robust and reliable input for predictions.
- **Model Training**: The decomposable time series model is used to forecast stock prices, accounting for trends, seasonal variations, and external factors.
- **User Interface**: An intuitive sidebar allows users to select stocks, specify investment values, and define prediction durations, followed by displaying calculated gains or losses based on user input.
- **Risk Meter**: An innovative risk meter visually represents the risk associated with investment choices, based on diversification across sectors and regions.
- **Stock Returns Analysis**: The application calculates and displays cumulative returns for selected stocks over time.

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/ibrahimashbah/Investment-Predictor.git
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application locally:
   ```bash
   streamlit run app.py
   ```

4. Access the app via the browser at `http://localhost:8501`.

## Usage

- **Select Your Stocks**: Choose up to three stocks from the provided list.
- **Set Investment Parameters**: Define the investment duration in years and the investment amount.
- **Predict**: Click the "Predict" button to generate forecasts and visualize results, including predicted values and potential gains or losses.

## Acknowledgments

This project is a collaborative effort, showcasing the application of machine learning and data analysis in the finance sector. It emphasizes the importance of data-driven decision-making in investment strategies.

## Skills Developed

- Web scraping and data manipulation using Python
- Statistical modeling and time series forecasting
- Data visualization with Plotly and Streamlit
- Deployment of web applications using Heroku

## Author

This application is maintained by [Ibrahim Ashbah](https://www.linkedin.com/in/ibrahimashbah/). Feel free to connect for more information or inquiries!

