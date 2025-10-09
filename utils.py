import datetime

# Dia atual
def data_atual(formato = '%Y-%m-%d'):
    hoje = datetime.date.today()
    #data = hoje - datetime.timedelta(days=3)
    return hoje.strftime(formato)
