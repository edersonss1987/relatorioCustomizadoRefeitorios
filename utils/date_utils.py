from datetime import datetime

def to_timestamp(data_hora):
    formato = "%Y-%m-%d %H:%M:%S"
    data_obj = datetime.strptime(str(data_hora), formato)
    return datetime.timestamp(data_obj)