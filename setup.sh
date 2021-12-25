mkdir -p ~/.streamlit/

echo "[theme]
primaryColor='#b88f89'
backgroundColor='#fafafa'
secondaryBackgroundColor='#fafafa'
textColor='#424242'
font='sans serif'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
