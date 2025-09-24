from pathlib import Path

import pandas as pd

labels = {
	'stations': {
		'SE': 'sureste',
		'NE': 'noreste',
		'CE': 'centro',
		'NO': 'noroeste',
		'SO': 'suroeste',
		'NO2': ['noroeste2', 'noroeste 2'],
		'NTE': 'norte',
		'NE2': ['noreste2', 'noreste 2'],
		'SE2': ['sureste2', 'sureste 2'],
		'SO2': ['suroeste2', 'suroeste 2'],
		'SUR': 'sur',
		'NTE2': ['norte2', 'norte 2'],
		'SE3': ['sureste3', 'sureste 3'],
		'NE3': ['noreste3', 'noreste 3'],
		'NO3': ['noroeste3', 'noroeste 3']
	},
	'contaminants': {
		'PM10': 'Partículas menores a 10 micras',
		'PM2.5': 'Partículas menores a 2.5 micras',
		'O3': 'Ozono',
		'SO2': 'Dióxido de azufre',
		'NO2': 'Dióxido de nitrógeno',
		'CO': 'Monóxido de carbono',
		'NO': 'Monóxido de nitrógeno',
		'NOX': 'Óxidos de nitrógeno'
	}
}

additional_labels = {
	'parameters': {
		'TOUT': 'Temperatura',
		'RH': 'Humedad Relativa',
		'SR': 'Radiación Solar',
		'RAINF': 'Precipitación',
		'PRS': 'Presión Atmosférica',
		'WSR': 'Velocidad del Viento',
		'WDR': 'Dirección del Viento'
	}
}

df_2020_2021_all_stations = pd.read_excel(
	Path("../data/raw/DATOS HISTÓRICOS 2020_2021_TODAS ESTACIONES.xlsx"),
	sheet_name=None
)

df_2022_2023_all_stations = pd.read_excel(
	Path("../data/raw/DATOS HISTÓRICOS 2022_2023_TODAS ESTACIONES.xlsx"),
	sheet_name=None
)

df_2024_all_stations = pd.read_excel(
	Path("../data/raw/BD 2024.xlsx"),
	sheet_name=None
)

df_2025_all_stations = pd.read_excel(
	Path("../data/raw/BD 2025.xlsx"),
	sheet_name=None
)

df_2023_2024_all_stations = pd.read_excel(
	Path("../data/raw/DATOS HISTÓRICOS 2023_2024_TODAS ESTACIONES_ITESM.xlsx"),
	sheet_name='Param_horarios_Estaciones',
	header=None
)

# Process dataset 1
frames = []
for name, frame in df_2020_2021_all_stations.items():
	if name == 'NOROESTE3':
		continue
	for code, codename in labels['stations'].items():
		frame_copy = frame.copy()
		if isinstance(codename, list):
			if any(name.upper() == cn.upper() for cn in codename):
				frame_copy['station_code'] = code
				frames.append(frame_copy)
		else:
			if name.upper() == codename.upper():
				frame_copy['station_code'] = code
				frames.append(frame_copy)

df_2020_2021_all_stations_processed = pd.concat(frames, ignore_index=True)

# Process dataset 2
frames = []
for name, frame in df_2022_2023_all_stations.items():
	for code, codename in labels['stations'].items():
		frame_copy = frame.copy()
		if isinstance(codename, list):
			if any(name.upper() == cn.upper() for cn in codename):
				frame_copy['station_code'] = code
				frames.append(frame_copy)
		else:
			if name.upper() == codename.upper():
				frame_copy['station_code'] = code
				frames.append(frame_copy)

df_2022_2023_all_stations_processed = pd.concat(frames, ignore_index=True)

# Process dataset 3
stations_map = labels['stations']

station_name_to_code = {}
for code, names in stations_map.items():
	if isinstance(names, list):
		for name in names:
			station_name_to_code[name.upper()] = code
	else:
		station_name_to_code[names.upper()] = code

stations_row = df_2023_2024_all_stations.iloc[0, 1:].astype(str).str.strip()
vars_row = df_2023_2024_all_stations.iloc[1, 1:].astype(str).str.strip()

full_body = df_2023_2024_all_stations.iloc[3:].reset_index(drop=True)
dates = pd.to_datetime(full_body.iloc[:, 0], errors="coerce", dayfirst=True)
body = full_body.iloc[:, 1:]

contaminants = list(labels["contaminants"].keys())

frames = []
for station in stations_row.unique():
	if pd.isna(station) or station == "nan" or station.upper() not in station_name_to_code:
		continue

	station_columns = stations_row[stations_row == station].index.tolist()

	station_data = {
		"station_code": station_name_to_code[station.upper()],
		"date": dates
	}

	for col_idx in station_columns:
		if col_idx not in vars_row.index or col_idx not in body.columns:
			print(f"Warning: Column label {col_idx} not found in vars_row or body.")
			continue

		var_name = vars_row.loc[col_idx]
		# Normalize known aliases in dataset 3 (only)
		if var_name == "WDV":
			var_name = "WDR"

		if var_name in contaminants or var_name in additional_labels["parameters"]:
			column_data = body.loc[:, col_idx]
			station_data[var_name] = pd.to_numeric(column_data, errors='coerce')

	if len(station_data) > 3:
		station_df = pd.DataFrame(station_data)
		frames.append(station_df)

df_2023_2024_all_stations_processed = pd.concat(frames, ignore_index=True)

if 'date' in df_2023_2024_all_stations_processed.columns:
	mask_not_2024 = df_2023_2024_all_stations_processed['date'].isna() | (df_2023_2024_all_stations_processed['date'].dt.year != 2024)
	df_2023_2024_all_stations_processed_no_2024 = df_2023_2024_all_stations_processed.loc[mask_not_2024].reset_index(drop=True)
else:
	df_2023_2024_all_stations_processed_no_2024 = df_2023_2024_all_stations_processed

# Process dataset 4
frames_2024 = []

param_codes_2024 = list(labels["contaminants"].keys()) + list(additional_labels["parameters"].keys())

for sheet_name, frame in df_2024_all_stations.items():
	code_clean = str(sheet_name).strip().upper()
	if code_clean in labels['stations'].keys():
		f = frame.copy()
		rename_map = {}

		for c in f.columns:
			c_str = str(c).strip()
			c_upper = c_str.upper()
			c_lower = c_str.lower()

			if c_lower.startswith('fecha'):
				rename_map[c] = 'date'
				continue

			match = next((code for code in param_codes_2024 if c_upper.startswith(code)), None)

			if match:
				rename_map[c] = match

		if rename_map:
			f = f.rename(columns=rename_map)

		f = f.loc[:, ~f.columns.duplicated()].copy()

		if 'date' in f.columns:
			f['date'] = pd.to_datetime(f['date'], errors='coerce', dayfirst=True)

		keep_cols = []

		if 'date' in f.columns:
			keep_cols.append('date')

		keep_cols += [code for code in param_codes_2024 if code in f.columns]

		if keep_cols:
			f = f.loc[:, keep_cols]

		for code in param_codes_2024:
			if code in f.columns:
				f[code] = pd.to_numeric(f[code], errors='coerce')
		f['station_code'] = code_clean
		frames_2024.append(f)

df_2024_all_stations_processed = pd.concat(frames_2024, ignore_index=True) if frames_2024 else pd.DataFrame()

# Process dataset 5
frames_2025 = []
for sheet_name, frame in df_2025_all_stations.items():
	code_clean = str(sheet_name).strip().upper()
	if code_clean in labels['stations'].keys():
		f = frame.copy()

		if len(f) > 0:
			f = f.drop(f.index[0]).reset_index(drop=True)

		if 'date' in f.columns:
			f['date'] = pd.to_datetime(f['date'], errors='coerce')

			f['station_code'] = code_clean
			frames_2025.append(f)

df_2025_all_stations_processed = pd.concat(frames_2025, ignore_index=True) if frames_2025 else pd.DataFrame()

# Concat all dataframes
main_dataframe = pd.concat(
	[
		df_2020_2021_all_stations_processed,
		df_2022_2023_all_stations_processed,
		df_2023_2024_all_stations_processed_no_2024,
		df_2024_all_stations_processed,
		df_2025_all_stations_processed
	],
	ignore_index=True
)

Path("../data/processed").mkdir(parents=True, exist_ok=True)

df_2020_2021_all_stations_processed.to_csv(
	Path("../data/processed/df_2020_2021_all_stations_processed.csv"),
	index=False,

)
df_2022_2023_all_stations_processed.to_csv(
	Path("../data/processed/df_2022_2023_all_stations_processed.csv"),
	index=False
)
df_2023_2024_all_stations_processed_no_2024.to_csv(
	Path("../data/processed/df_2023_2024_all_stations_processed_no_2024.csv"),
	index=False
)
df_2024_all_stations_processed.to_csv(
	Path("../data/processed/df_2024_all_stations_processed.csv"),
	index=False
)
df_2025_all_stations_processed.to_csv(
	Path("../data/processed/df_2025_all_stations_processed.csv"),
	index=False
)

main_dataframe.to_csv(
	Path("../data/processed/main_dataframe.csv"),
	index=False
)
