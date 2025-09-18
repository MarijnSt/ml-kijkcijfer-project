import joblib
import pandas as pd
import numpy as np
import sys

# Kijk of er een command line argument is meegegeven
if len(sys.argv) != 2:
    print("Gelieve een csv file mee te geven als input voor het model.")
    print("Voorbeeld: python kijkcijfers.py <csv_file_location>")
    sys.exit(1)

# Lees de csv file in
print("Bestand lezen...")
csv_file_location = sys.argv[1]
ratings_df = pd.read_csv(csv_file_location, sep=";")


""" 
1. RATINGS DATA VERWERKEN
"""

# Datum omzetten in datetime
ratings_df["Datum"] = pd.to_datetime(ratings_df["Datum"], format='%d/%m/%Y')

# Start omzetten in datetime
ratings_df["Start"] = pd.to_datetime(ratings_df["Start"], format='%H:%M:%S').dt.time
ratings_df["Start"] = [pd.Timestamp.combine(d,t) for d,t in zip(ratings_df['Datum'],ratings_df['Start'])]

# Duur omzetten in timedelta
ratings_df["Duur"] = pd.to_timedelta(ratings_df["Duur"])

# Zet verschillende waardes voor EEN om
ratings_df.loc[ratings_df["Zender"].isin(["EEN", "VRT 1"]), "Zender"] = "EEN"

# Zet verschillende waardes voor CANVAS om
ratings_df.loc[ratings_df["Zender"].isin(["Canvas", "CANVAS", "VRT CANVAS"]), "Zender"] = "CANVAS"

# Zet verschillende waardes voor KETNET om
ratings_df.loc[ratings_df["Zender"].isin(["KETNET", "OP 12"]), "Zender"] = "KETNET"

# Zet verschillende waardes voor PLAY4 om
ratings_df.loc[ratings_df["Zender"].isin(["VIER", "PLAY4"]), "Zender"] = "PLAY4"

# Zet verschillende waardes voor PLAY5 om
ratings_df.loc[ratings_df["Zender"].isin(["VIJF", "PLAY5"]), "Zender"] = "PLAY5"

# Zet verschillende waardes voor PLAY6 om
ratings_df.loc[ratings_df["Zender"].isin(["ZES", "PLAY6"]), "Zender"] = "PLAY6"

# Zet verschillende waardes voor VTM2 om
ratings_df.loc[ratings_df["Zender"].isin(["Q2", "VTM2"]), "Zender"] = "VTM2"

# Zet verschillende waardes voor VTM3 om
ratings_df.loc[ratings_df["Zender"].isin(["VITAYA", "VTM3"]), "Zender"] = "VTM3"

# Zet verschillende waardes voor VTM4 om
ratings_df.loc[ratings_df["Zender"].isin(["CAZ", "VTM4"]), "Zender"] = "VTM4"

# Wijs programma's over gedeelde zenders toe aan EEN
ratings_df.loc[ratings_df["Zender"].isin(["EEN,VTM,PLAY4", "EEN, VTM, PLAY", "VRT 1/VTM/Play4"]), "Zender"] = "EEN"

# Geef ELEVEN en DAZN dezelfde waarde
ratings_df.loc[ratings_df["Zender"].isin(["ELEVEN PRO LEAGUE 1 NL", "DAZN PRO LEAGUE 1 (NL)"]), "Zender"] = "PRO LEAGUE 1"


"""
2. ZONSOPGANG EN -ONDERGANG DATA VERWERKEN
"""

solar_df = pd.DataFrame({
    'Datum': [ '2025-06-01', '2025-06-02', '2025-06-03', '2025-06-04', '2025-06-05', '2025-06-06', '2025-06-07', '2025-06-08', '2025-06-09', '2025-06-10', '2025-06-11', '2025-06-12', '2025-06-13', '2025-06-14'],
    'Zonsopgang': ['2025-06-01 05:34:37', '2025-06-02 05:33:53', '2025-06-03 05:33:12', '2025-06-04 05:32:34', '2025-06-05 05:31:58', '2025-06-06 05:31:26', '2025-06-07 05:30:56', '2025-06-08 05:30:29', '2025-06-09 05:30:05', '2025-06-10 05:29:45', '2025-06-11 05:29:27', '2025-06-12 05:29:12', '2025-06-13 05:29:00', '2025-06-14 05:28:51'],
    'Zonsondergang': ['2025-06-01 21:46:58', '2025-06-02 21:47:59', '2025-06-03 21:48:58', '2025-06-04 21:49:55', '2025-06-05 21:50:50', '2025-06-06 21:51:43', '2025-06-07 21:52:33', '2025-06-08 21:53:21', '2025-06-09 21:54:07', '2025-06-10 21:54:50', '2025-06-11 21:55:30', '2025-06-12 21:56:08', '2025-06-13 21:56:43', '2025-06-14 21:57:15']
})

# Datums omzetten
solar_df["Datum"] = pd.to_datetime(solar_df["Datum"])
solar_df["Zonsopgang"] = pd.to_datetime(solar_df["Zonsopgang"])
solar_df["Zonsondergang"] = pd.to_datetime(solar_df["Zonsondergang"])

# Mergen met ratings data
ratings_solar_df = pd.merge(ratings_df, solar_df, on="Datum", how="inner")


"""
3. WEER DATA VERWERKEN
"""

weather_df_predict = pd.DataFrame({
    'Datum': [ '2025-06-01', '2025-06-02', '2025-06-03', '2025-06-04', '2025-06-05', '2025-06-06', '2025-06-07', '2025-06-08', '2025-06-09', '2025-06-10', '2025-06-11', '2025-06-12', '2025-06-13', '2025-06-14'],
    'Temp': [15.902307692307694, 16.88223076923077, 16.631615384615387, 16.58968992248062, 15.815078125, 15.266850393700787, 15.596356589147288, 15.792558139534885, 15.931317829457363, 16.85813953488372, 17.53708661417323, 16.459212598425196, 16.19234375, 17.128671875],
    'Zon': [507.3521666666667, 477.32416666666666, 467.38291666666663, 466.12033333333335, 337.953781512605, 539.1359322033899, 481.2871666666667, 471.4726890756302, 549.8870588235294, 503.4599159663866, 552.733813559322, 417.7365254237288, 560.1251260504201, 581.5693220338983],
    'Regen': [2.9973846153846155, 1.7195384615384615, 1.045076923076923, 3.274108527131783, 5.733333333333333, 1.9814728682170542, 2.426201550387597, 1.7692248062015503, 1.376589147286822, 1.64984375, 1.186875, 3.30671875, 1.6744094488188976, 1.4854330708661418],
    'Druk': [998.2348461538461, 996.9444615384615, 996.4503846153847, 994.1857364341085, 993.0446875, 994.54890625, 996.6054263565892, 996.8062015503876, 998.01, 996.950546875, 995.7625984251969, 994.9400787401574, 995.3712598425196, 993.8235433070865],
    'Luchtvochtigheid': [73.66053846153847, 71.00761538461538, 74.11007692307692, 75.25255813953488, 79.580390625, 73.732890625, 73.77767441860465, 75.68953488372094, 71.07837209302326, 71.60255813953488, 70.699609375, 73.586015625, 70.33328125, 69.507734375],
})

# Zet datum om in het juiste format
weather_df_predict["Datum"] = pd.to_datetime(weather_df_predict["Datum"])

# Merge met ratings_solar_df
data = pd.merge(ratings_solar_df, weather_df_predict, on="Datum", how="inner")


""" 
4. FEATURE ENGINEERING
"""

# Jaar, maand, dag en week afleiden uit de datum
data["Jaar"] = data["Datum"].dt.year
data["Maand"] = data["Datum"].dt.month
data["Dag"] = data["Datum"].dt.day_of_week
data["Week"] = data["Datum"].dt.isocalendar().week

# Covid features
data["Covid19"] = np.where((data["Datum"] >= "2020-02-04") & (data["Datum"] <= "2022-03-13"), 1, 0) # Van de eerste nationale veiligheidsraad tot wanneer we naar code geel gingen
data["Lockdown1"] = np.where((data["Datum"] >= "2020-03-13") & (data["Datum"] <= "2020-06-08"), 1, 0) # Afbouwplan startte op 8 juni.
data["Lockdown2"] = np.where((data["Datum"] >= "2020-10-30") & (data["Datum"] <= "2021-04-19"), 1, 0) # Minder duidelijk afbouwplan.Het onderwijs herstart terug op 19 april.

# Eind tijd berekenen
data["Eind"] = data["Start"] + data["Duur"]

# Startuur en einduur afsplitsen
data["Startuur"] = data["Start"].dt.hour
data["Einduur"] = data["Eind"].dt.hour

# Duur in minuten berekenen
data["Duur"] = np.round(data["Duur"].dt.total_seconds() / 60)
data["Duur"] = data["Duur"].astype(int)

# Voeg primetime kolommen toe
data["Primetime"] = ((data["Startuur"] >= 20) & (data["Einduur"] <= 22)).astype(int)
data["Einde_In_Primetime"] = ((data["Einduur"] >= 20) & (data["Einduur"] <= 22)).astype(int)
data["Start_In_Primetime"] = ((data["Startuur"] >= 20) & (data["Startuur"] <= 22)).astype(int)

# Zenders van de openbare omroep onderbreken hun programma's niet voor reclame
data["Reclame_Onderbrekingen"] = np.where(data["Zender"].isin(["EEN", "CANVAS", "KETNET", "LA UNE"]), 0, 1)

# Delta's zonsopgang/zonsondergang
data["Zonsopgang_Delta_Start"] = data["Startuur"] - data["Zonsopgang"].dt.hour
data["Zonsopgang_Delta_Einde"] = data["Einduur"] - data["Zonsopgang"].dt.hour
data["Zonsondergang_Delta_Start"] = data["Zonsondergang"].dt.hour - data["Startuur"]
data["Zonsondergang_Delta_Einde"] = data["Zonsondergang"].dt.hour - data["Einduur"]

# Sommige features hebben we niet nodig, we kunnen de andere ook wel beter sorteren
final_features = ["Programma", "Zender", "Jaar", "Maand", "Dag", "Week", "Covid19", "Lockdown1", "Lockdown2", "Startuur", "Einduur", "Duur", "Primetime", "Einde_In_Primetime", "Start_In_Primetime", "Zonsopgang_Delta_Start", "Zonsopgang_Delta_Einde", "Zonsondergang_Delta_Start", "Zonsondergang_Delta_Einde", "Reclame_Onderbrekingen", "Temp", "Zon", "Regen", "Druk", "Luchtvochtigheid"]
data = data[final_features]

# Drop duplicates
data = data.drop_duplicates()


""" 
5. MODEL GEBRUIKEN OM VOORSPELLING TE MAKEN
"""

print("Model laden...")
model = joblib.load("kijkcijfer_model.pkl")
new_data = data.drop(columns=["Programma"])
print("Voorspellingen maken...")
predictions = model.predict(new_data)


"""
6. OUTPUT VERWERKEN
"""

# Resultaten toevoegen aan data df
ratings_df["Kijkers"] = predictions
ratings_df

# Output opslaan als csv
csv = ratings_df.to_csv("examen_oplossing.csv", index=False)

# Print in console
print("Resultaten:")
for index, row in ratings_df.iterrows():
    print(f"{row['Start']} - {row['Programma']} ({row['Zender']}) - {row['Kijkers']:.0f} kijkers")

print("Resulaten opgeslagen in examen_oplossing.csv")