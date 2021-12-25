mkdir -p ~/.streamlit/

echo "[theme]
base='light'
primaryColor='#1AA6B7'
backgroundColor='#fafafa'
secondaryBackgroundColor='#eaf2f4'
textColor='#262730'
font='sans serif'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
