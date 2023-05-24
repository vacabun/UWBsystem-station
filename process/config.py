import pandas


def load_config():
    df = pandas.read_excel('config/config.xlsx')
    return df.loc[0, ['server_ip', 'server_port', 'com', ]].to_dict()
