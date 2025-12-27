import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# Konfiguracja
TICKERS = ["AAPL", "MSFT", "TSLA", "PKO.WA", "PEO.WA", "BTC-USD"]
YEARS = 3
OUTPUT_FILE = "market_data.csv"

def main():
    print(" ROZPOCZĘCIE POBIERANIA...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * YEARS)
    
    all_data = [] 
    
    for ticker in TICKERS:
        print(f"   -> Pobieram: {ticker}...", end=" ")
        try:
            # Pobieranie danych
            raw_df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
            
            if len(raw_df) > 0:
                # Spłaszczanie struktury (usunięcie MultiIndex)
                if isinstance(raw_df.columns, pd.MultiIndex):
                    raw_df.columns = raw_df.columns.get_level_values(0)
                
                # Reset indeksu, aby Data stała się kolumną
                raw_df = raw_df.reset_index()
                
                clean_df = pd.DataFrame()
                
                if 'Date' in raw_df.columns:
                    clean_df['Date'] = raw_df['Date']
                else:
                    clean_df['Date'] = raw_df['index']
                
                if 'Close' in raw_df.columns:
                    clean_df['Close_Price'] = raw_df['Close']
                else:
                    clean_df['Close_Price'] = raw_df.iloc[:, 1] 

                clean_df['Ticker'] = ticker
                
                all_data.append(clean_df)
                print("OK")
            else:
                print("PUSTE DANE")
                
        except Exception as e:
            print(f"BŁĄD ({e})")
        
        time.sleep(0.5)

    if not all_data:
        print("\nBŁĄD KRYTYCZNY: Brak danych.")
        return

    print("\n Łączenie i Przetwarzanie...")
    df_final = pd.concat(all_data, ignore_index=True)
    
    # Sortowanie
    df_final = df_final.sort_values(by=['Ticker', 'Date'])
    
    df_final['Volatility_30d'] = df_final.groupby('Ticker')['Close_Price'].transform(lambda x: x.rolling(window=30).std())
    
    # Czyszczenie
    df_final = df_final.dropna()
    df_final['Close_Price'] = df_final['Close_Price'].round(2)
    df_final['Volatility_30d'] = df_final['Volatility_30d'].round(2)
    
    # Formatowanie daty (usunięcie godziny)
    if pd.api.types.is_datetime64_any_dtype(df_final['Date']):
        df_final['Date'] = df_final['Date'].dt.date
    
    # Zapis
    df_final.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\nUtworzono plik: {OUTPUT_FILE}")
    print(f"Pobrane spółki: {df_final['Ticker'].unique()}")

if __name__ == "__main__":
    main()