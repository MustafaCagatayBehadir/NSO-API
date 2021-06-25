import pandas as pd


def vlookup():
    excel_left = input("VLOOKUP LEFT EXCEL NAME:")
    sheet_left = input("VLOOKUP LEFT EXCEL SHEETNAME:")
    excel_right = input("VLOOKUP RIGHT EXCEL NAME:")
    sheet_right = input("VLOOKUP RIGHT EXCEL SHEETNAME:")
    vlookup_column_names = input("VLOOKUP COLUMN NAMES:").split(",")
    df_left = pd.read_excel(excel_left, sheet_name=sheet_left)
    df_right = pd.read_excel(excel_right, sheet_name=sheet_right)
    df = df_left.merge(df_right, how="left", on=vlookup_column_names)
    file = "VLOOKUP_RESULT.xlsx"
    with pd.ExcelWriter(file) as writer:
        df.to_excel(writer)


if __name__ == "__main__":
    vlookup()
