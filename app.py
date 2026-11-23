import streamlit as st
import pandas as pd
import numpy as np
from skfuzzy import control as ctrl
import skfuzzy as fuzz

# Завантаження датасету
df = pd.read_csv('climate_change_dataset.csv')

# Виправлення типів даних для Year та Month
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Month'] = pd.to_numeric(df['Month'], errors='coerce')

# Заповнення пропущених значень forward fill
df['Year'] = df['Year'].ffill().bfill()
df['Month'] = df['Month'].ffill().bfill()

# Перетворення на int
df['Year'] = df['Year'].round().astype(int)
df['Month'] = df['Month'].round().astype(int)

# Очищення інших даних (заміна 'Unknown', 'NAN' на NaN, перетворення на числові)
df.replace(['Unknown', 'NAN'], np.nan, inplace=True)
df = df.apply(pd.to_numeric, errors='coerce')

# Заповнення пропущених значень медіаною
df.fillna(df.median(), inplace=True)

# Визначення нечітких змінних
avg_temp = ctrl.Antecedent(np.arange(-5, 40, 1), 'Avg_Temp')
humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'Humidity')
pm = ctrl.Antecedent(np.arange(0, 50, 1), 'Particulate_Matter')
precip = ctrl.Antecedent(np.arange(0, 200, 1), 'Precipitation')
enso = ctrl.Antecedent(np.arange(-1, 1.1, 0.1), 'ENSO_Index')
hri = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'HRI')

# Функції належності
avg_temp['N'] = fuzz.trimf(avg_temp.universe, [-5, 0, 5])
avg_temp['M'] = fuzz.trimf(avg_temp.universe, [0, 5, 12.5])
avg_temp['H'] = fuzz.trimf(avg_temp.universe, [5, 12.5, 20])

humidity['N'] = fuzz.trimf(humidity.universe, [0, 25, 50])
humidity['M'] = fuzz.trimf(humidity.universe, [25, 50, 65])
humidity['H'] = fuzz.trimf(humidity.universe, [50, 65, 80])

pm['N'] = fuzz.trimf(pm.universe, [0, 5, 10])
pm['M'] = fuzz.trimf(pm.universe, [5, 10, 20])
pm['H'] = fuzz.trimf(pm.universe, [10, 20, 30])

precip['N'] = fuzz.trimf(precip.universe, [0, 25, 50])
precip['M'] = fuzz.trimf(precip.universe, [25, 50, 100])
precip['H'] = fuzz.trimf(precip.universe, [50, 100, 150])

enso['N'] = fuzz.trimf(enso.universe, [-1, -0.75, -0.5])
enso['Z'] = fuzz.trimf(enso.universe, [-0.75, -0.5, 0])
enso['P'] = fuzz.trimf(enso.universe, [-0.5, 0, 0.5])

hri['L'] = fuzz.trimf(hri.universe, [0, 0.15, 0.3])
hri['M'] = fuzz.trimf(hri.universe, [0.15, 0.3, 0.5])
hri['H'] = fuzz.trimf(hri.universe, [0.5, 0.7, 0.85])

# Правила (спрощений набір; для повного - додати всі комбінації)
rules = []
rules.append(ctrl.Rule(avg_temp['N'] & humidity['N'] & pm['N'] & precip['N'] & enso['Z'], hri['L']))
rules.append(ctrl.Rule(avg_temp['H'] | pm['H'], hri['H']))
rules.append(ctrl.Rule(avg_temp['M'] & humidity['M'] & pm['M'] & precip['M'] & enso['Z'], hri['M']))
rules.append(ctrl.Rule(avg_temp['H'] & humidity['H'] & pm['H'] & precip['H'] & enso['P'], hri['H']))
rules.append(ctrl.Rule(avg_temp['N'] & humidity['H'] & pm['M'] & precip['N'] & enso['N'], hri['M']))
rules.append(ctrl.Rule(avg_temp['H'] & humidity['M'] & pm['N'] & precip['M'] & enso['P'], hri['M']))
rules.append(ctrl.Rule(avg_temp['M'] & humidity['H'] & pm['H'] & precip['N'] & enso['Z'], hri['H']))
rules.append(ctrl.Rule(avg_temp['N'] & humidity['N'] & pm['M'] & precip['H'] & enso['N'], hri['L']))
# Додайте решту правил для охоплення комбінацій

# Система контролю
hri_ctrl = ctrl.ControlSystem(rules)
hri_sim = ctrl.ControlSystemSimulation(hri_ctrl)

# Нейтральні значення для невибраних параметрів
neutrals = {
    'Avg_Temp': 12.5,
    'Humidity': 65,
    'Particulate_Matter': 20,
    'Precipitation': 100,
    'ENSO_Index': 0
}

# Мапінг для параметрів
param_map = {
    'Avg_Temp (°C)': 'Avg_Temp',
    'Humidity (%)': 'Humidity',
    'Particulate_Matter (µg/m³)': 'Particulate_Matter',
    'Precipitation (mm)': 'Precipitation',
    'ENSO_Index': 'ENSO_Index'
}

# Streamlit інтерфейс
st.title('Система аналізу впливу кліматичних умов на здоров\'я населення')

# Вибір критеріїв користувачем
selected_params = st.multiselect('Оберіть критерії для аналізу:', list(param_map.keys()))
year = st.slider('Рік:', 2020, 2024)
month = st.slider('Місяць:', 1, 12)

# Фільтрація даних
filtered_df = df[(df['Year'] == year) & (df['Month'] == month)]

if not filtered_df.empty:
    inputs = {
        'Avg_Temp': filtered_df['Avg_Temp (°C)'].values[0],
        'Humidity': filtered_df['Humidity (%)'].values[0],
        'Particulate_Matter': filtered_df['Particulate_Matter (µg/m³)'].values[0],
        'Precipitation': filtered_df['Precipitation (mm)'].values[0],
        'ENSO_Index': filtered_df['ENSO_Index'].values[0]
    }

    # Встановлення вхідних значень: актуальні для вибраних, нейтральні для інших
    selected_keys = [param_map[p] for p in selected_params]
    for key in inputs.keys():
        if key in selected_keys:
            hri_sim.input[key] = inputs[key]
        else:
            hri_sim.input[key] = neutrals[key]

    try:
        hri_sim.compute()
        hri_value = hri_sim.output['HRI']
        if np.isnan(hri_value):
            st.write('HRI не визначено (немає активних правил для цієї комбінації)')
        else:
            st.write(f'Індекс ризику для здоров\'я (HRI): {hri_value:.2f}')
    except ValueError as e:
        st.write(f'Помилка в обчисленні HRI: {str(e)}')

    # Графіки для вибраних параметрів
    if selected_params:
        # Мапінг назад до колонок з одиницями
        selected_columns = selected_params
        chart_data = df[selected_columns].copy()
        chart_data['Year-Month'] = df['Year'].astype(str) + '-' + df['Month'].astype(str).str.zfill(2)
        chart_data.set_index('Year-Month', inplace=True)
        st.line_chart(chart_data)
else:
    st.write('Дані за обраний період відсутні.')