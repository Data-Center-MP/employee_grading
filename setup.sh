mkdir -p ~/.streamlit/
echo "[theme]
base='light'
primaryColor='#f68a06'
font='serif'
\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml


