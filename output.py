import pandas as pd

def to_csv(df):
    df.to_csv("shocial_products.csv", index=False)

def to_google_sheets(df):
    # In the future, we will implement this
    print("Data saved to Google Sheets (not implemented yet)")
