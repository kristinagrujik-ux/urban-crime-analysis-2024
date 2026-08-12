import pandas as pd

# Вчитување на податоците од Excel фајлот
file_path = 'KRIMINALITET.xlsx'

try:
    df = pd.read_excel(file_path)
    print("--- Анализа на податоци за криминалитет ---")
    print(df.info())
    print("\nПрви 5 редови од табелата:")
    print(df.head())
except Exception as e:
    print(f"Грешка при вчитување на фајлот: {e}")
