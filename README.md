# Forecast-Investment


# Reproducing this web app
To recreate this web app on your own computer, do the following.

### Create conda environment
Firstly, we will create a conda environment called *myenv*
```
conda create -n myenv python=3.8
```
Secondly, we will login to the *myenv* environement
```
conda activate myenv
```
### Install prerequisite libraries

Download requirements.txt file

```
wget https://raw.githubusercontent.com/ibrahimashbah/stock-predictor-app/main/requirements.txt

```

Pip install libraries
```
pip install -r requirements.txt
```

###  Download and unzip contents from GitHub repo

Download and unzip contents from https://github.com/ibrahimashbah/stock-predictor-app/archive/refs/heads/main.zip



###  Launch the app

```
streamlit run app.py
```
