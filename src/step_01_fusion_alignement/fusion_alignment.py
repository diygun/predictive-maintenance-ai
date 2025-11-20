import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()

def process(folder:str="PI-donnee-saine"):
    input_dir = Path("data/01_raw_input") / folder
    output_dir = Path("data/02_merged") / folder
    files = get_files(input_dir)
    
    # lecture de tous les fichiers
    df_ax = read_and_prepare(files["ax"], "ax_vibration_ms2")
    df_ay = read_and_prepare(files["ay"], "ay_vibration_ms2")
    df_az = read_and_prepare(files["az"], "az_vibration_ms2")
    df_gx = read_and_prepare(files["gx"], "gx_vibration_gx")
    df_gy = read_and_prepare(files["gy"], "gy_vibration_gy")
    df_gz = read_and_prepare(files["gz"], "gz_vibration_gz")
    df_hall = read_and_prepare(files["hall"], "hall_switch")
    
    # créer l'index commun (union triée de tous les timestamps)
    all_times = pd.Index(sorted(
        pd.concat([df.index.to_series() for df in (df_ax, df_ay, df_az, df_gx, df_gy, df_gz, df_hall)])
        .unique()
    ))

    # tolérance pour associer les horodatages (ajuster si nécessaire)
    # Ce paramettre permet d'accepte de décaler une donnée pour l'aligner
    delay = os.getenv("STEP1_HORODATAGES_TOLERANCE")# ici 30 millisecondes
    tolerance = pd.Timedelta(delay)  

    # réindexer chaque df sur all_times en prenant la valeur la plus proche
    def reindex_nearest(df, index, tol):
        return df.reindex(index, method="nearest", tolerance=tol)

    r_ax = reindex_nearest(df_ax, all_times, tolerance)
    r_ay = reindex_nearest(df_ay, all_times, tolerance)
    r_az = reindex_nearest(df_az, all_times, tolerance)
    r_gx = reindex_nearest(df_gx, all_times, tolerance)
    r_gy = reindex_nearest(df_gy, all_times, tolerance)
    r_gz = reindex_nearest(df_gz, all_times, tolerance)
    r_hall = reindex_nearest(df_hall, all_times, tolerance)

    # concaténer toutes les colonnes dans un seul DataFrame
    df_merged = pd.concat([r_ax, r_ay, r_az, r_gx, r_gy, r_gz, r_hall], axis=1)

    # index datetime commun
    df_merged.index.name = "date"

    # sauvegarde
    df_merged.to_csv(output_dir / f"{folder}_output.csv")

    # aperçu
    # print(df_merged.head(20))

def get_files(base_dir):
    files = {
        "ax": base_dir / "AX_vibration.csv",
        "ay": base_dir / "AY_vibration.csv",
        "az": base_dir / "AZ_vibration.csv",
        "gx": base_dir / "gx_vibration.csv",
        "gy": base_dir / "gy_vibration.csv",
        "gz": base_dir / "GZ_vibration.csv",
        "hall": base_dir / "HALL_switch.csv",
    }
    return files

# fonction lecture + parse date
def read_and_prepare(path, value_col_name):
    df = pd.read_csv(path)
    # si la colonne s'appelle déjà autre chose on la renomme
    if df.columns[0].lower() not in ("date",):
        df = df.rename(columns={df.columns[0]: "date"})
    df = df.rename(columns={df.columns[1]: value_col_name})
    # parse date (pandas gère le format AM/PM et les micro/nano secondes)
    df["date"] = pd.to_datetime(df["date"], format='%m/%d/%Y %I:%M:%S.%f %p', errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df.set_index("date")
    return df

