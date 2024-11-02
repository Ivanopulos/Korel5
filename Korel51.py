import pandas as pd
import os
import numpy as np

# Получение текущей директории
current_directory = os.getcwd()

# Чтение всех .txt файлов
files = [f for f in os.listdir(current_directory) if f.endswith('.txt')]
dataframes = {}

for file in files:
    # Предполагаем, что первая строка содержит заголовки, если это так
    df = pd.read_csv(os.path.join(current_directory, file), header=0)
    # Проверяем, есть ли нужные столбцы, и если нет, пытаемся прочитать без заголовков
    if 'DATE' not in df.columns or 'HIGH' not in df.columns:
        df = pd.read_csv(os.path.join(current_directory, file), header=None)
        df.columns = ['TICKER', 'PER', 'DATE', 'TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOL']

    df['DATE'] = pd.to_datetime(df['DATE'], format='%y%m%d', errors='coerce')  # Преобразование даты с обработкой ошибок
    df.set_index('DATE', inplace=True)

    # Преобразование столбцов в числовой тип
    df['HIGH'] = pd.to_numeric(df['HIGH'], errors='coerce')
    df['LOW'] = pd.to_numeric(df['LOW'], errors='coerce')
    df['CLOSE'] = pd.to_numeric(df['CLOSE'], errors='coerce')

    # Расчет DELTA
    df['DELTA'] = df['HIGH'] / df['LOW']

    dataframes[file[:-4]] = df['DELTA']  # Или df['DELTA'], если вы хотите анализировать DELTA

# Подготовка к корреляционному анализу и т.д.
all_results = pd.DataFrame()

results = {}
for lag in range(-30, 31):  # Включаем отрицательные и положительные лаги
    shifted_dataframes = {k: v.shift(lag) for k, v in dataframes.items()}
    combined_df = pd.concat(shifted_dataframes, axis=1)
    correlation_matrix = combined_df.corr()

    # Сохраняем топ-100 положительных и отрицательных корреляций для каждого лага
    top_positive = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates().head(100)
    top_negative = correlation_matrix.unstack().sort_values().drop_duplicates().head(100)

    #results[lag] = (top_positive, top_negative)
    # Сбор всех результатов в один DataFrame
    for df, kind in [(top_positive, 'Positive'), (top_negative, 'Negative')]:
        temp_df = df.reset_index()
        temp_df.columns = ['Pair1', 'Pair2', 'Correlation']
        temp_df['Lag'] = lag
        temp_df['Type'] = kind
        all_results = pd.concat([all_results, temp_df])

# Отсортировать общий DataFrame по корреляции
all_results.sort_values(by='Correlation', ascending=False, inplace=True)
# # Сохранение результатов
# for lag in results:
#     pos, neg = results[lag]
#     pos.to_csv(f'top_100_positive_correlations_lag_{lag}.csv')
#     neg.to_csv(f'top_100_negative_correlations_lag_{lag}.csv')
# Сохранить результаты в один файл
all_results.to_csv('combined_correlations.csv', index=False)