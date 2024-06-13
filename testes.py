from datetime import datetime

data_agr = datetime.now()

hoje     = datetime.strptime(f'{data_agr.year}-{data_agr.month}-{data_agr.day}', '%Y-%m-%d')

print(data_agr)
print(hoje)