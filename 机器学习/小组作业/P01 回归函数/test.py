import numpy as np
import pandas as pd

df = pd.read_csv('archive/dirty_v3_path.csv')
print(df.head())
print(df.columns)

all_cols = ['Age', 'Glucose', 'Blood Pressure',
       'BMI', 'Oxygen Saturation', 'LengthOfStay', 'Cholesterol',
       'Triglycerides', 'HbA1c', 'Physical Activity',
       'Diet Score', 'Stress Level', 'Sleep Hours']

y = df['Blood Pressure']
selected_cols = ['Age', 'Glucose',
       'BMI', 'Oxygen Saturation', 'Cholesterol',
       'Triglycerides', 'HbA1c', 'Physical Activity',
       'Diet Score', 'Stress Level', 'Sleep Hours']
X = df[selected_cols]



def calc_corr(df, col1, col2):
    return df[col1].corr(df[col2])


corrs = []
for i in range(len(all_cols)):
    for j in range(i+1, len(all_cols)):
        if all_cols[i] in selected_cols and all_cols[j] in selected_cols:
            cor = calc_corr(df, all_cols[i], all_cols[j])
            corrs.append((all_cols[i], all_cols[j], cor))

corrs = sorted(corrs, key=lambda x: x[2], reverse=True)

for c in corrs:
    print(c[0], c[1], c[2])


# Temperature (C) Apparent Temperature (C) 0.9926285641921317
# Temperature (C) Humidity -0.6322546750278026
# Temperature (C) Wind Speed (km/h) 0.00895696834370139
# Temperature (C) Wind Bearing (degrees) 0.02998820447357343
# Temperature (C) Visibility (km) 0.3928465717241786
# Temperature (C) Pressure (millibars) -0.005447106151951313
# Apparent Temperature (C) Humidity -0.6025709955733909
# Apparent Temperature (C) Wind Speed (km/h) -0.056649698289561595
# Apparent Temperature (C) Wind Bearing (degrees) 0.029030519766564636
# Apparent Temperature (C) Visibility (km) 0.3817184704633866
# Apparent Temperature (C) Pressure (millibars) -0.00021899978632533172
# Humidity Wind Speed (km/h) -0.22495145587978208
# Humidity Wind Bearing (degrees) 0.0007346453563290166
# Humidity Visibility (km) -0.36917250059800705
# Humidity Pressure (millibars) 0.005454263261941814
# Wind Speed (km/h) Wind Bearing (degrees) 0.10382150773640675
# Wind Speed (km/h) Visibility (km) 0.1007492840677869
# Wind Speed (km/h) Pressure (millibars) -0.049262805511161946
# Wind Bearing (degrees) Visibility (km) 0.04759417525904441
# Wind Bearing (degrees) Pressure (millibars) -0.011650884797118888
# Visibility (km) Pressure (millibars) 0.059818381034748534