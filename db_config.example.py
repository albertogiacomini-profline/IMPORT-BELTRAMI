# Copia questo file in db_config.py (nella stessa cartella) e non toccare più questo esempio.
# db_config.py contiene la password del database e non va committato: è già escluso in .gitignore.
DB_CONFIG = dict(
    server='10.0.3.7',
    port='50425',       # porta dinamica di SQL Server Express: se cambia, ridiscoprila
                         # interrogando il SQL Server Browser (UDP 1434) su 10.0.3.7
    user='sqlRead',
    password='sqlRead',
    database='CmpGestCont',
    timeout=30,
    login_timeout=15,
)
