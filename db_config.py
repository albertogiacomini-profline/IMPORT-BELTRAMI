# Credenziali del DB GestCont (utenza sola lettura). Repo a uso interno, condiviso solo
# con i collaboratori: committato di proposito, vedi conversazione del 24/09/2026.
DB_CONFIG = dict(
    server='10.0.3.7',
    port='50425',
    user='sqlRead',
    password='sqlRead',
    database='CmpGestCont',
    timeout=30,
    login_timeout=15,
)
