import requests
import pandas as pd

# Define headers and URLs
headers = {'User-Agent': "email@address.com"}
ciks_url = "https://www.sec.gov/files/company_tickers.json"

company_tickers = dict(
    # oil_gas_tickers=['MRO', 'XOM', 'CVX', 'COP', 'TTE', 'EOG', 'VLO', 'PSX', 'MPC', 'OXY', 'SLB'],
    communication_services_tickers=[
        'GOOGL',  # Alphabet Inc.
        'META',  # Meta Platforms, Inc. (formerly Facebook)
        'DIS',  # The Walt Disney Company
        'CMCSA',  # Comcast Corporation
        'NFLX',  # Netflix, Inc.
        'T',  # AT&T Inc.
        'VZ',  # Verizon Communications Inc.
        'TMUS',  # T-Mobile US, Inc.
        'CHTR',  # Charter Communications, Inc.
        'SIRI',  # Sirius XM Holdings Inc.
    ],
    consumer_discretionary_tickers=[
        'AMZN',  # Amazon.com, Inc.
        'TSLA',  # Tesla, Inc.
        'HD',  # The Home Depot, Inc.
        'MCD',  # McDonald's Corporation
        'NKE',  # NIKE, Inc.
        'LOW',  # Lowe's Companies, Inc.
        'SBUX',  # Starbucks Corporation
        'BKNG',  # Booking Holdings Inc.
        'GM',  # General Motors Company
        'MAR',  # Marriott International, Inc.
    ],
    consumer_staples_tickers=[
        'PG',  # The Procter & Gamble Company
        'KO',  # The Coca-Cola Company
        'PEP',  # PepsiCo, Inc.
        'WMT',  # Walmart Inc.
        'COST',  # Costco Wholesale Corporation
        'MO',  # Altria Group, Inc.
        'PM',  # Philip Morris International Inc.
        'CL',  # Colgate-Palmolive Company
        'K',  # Kellogg Company
        'KR',  # The Kroger Co.
    ],
    energy_tickers=[
        'XOM',  # Exxon Mobil Corporation
        'CVX',  # Chevron Corporation
        'COP',  # ConocoPhillips
        'SLB',  # Schlumberger N.V.
        'EOG',  # EOG Resources, Inc.
        'MPC',  # Marathon Petroleum Corporation
        'PSX',  # Phillips 66
        'VLO',  # Valero Energy Corporation
        'OXY',  # Occidental Petroleum Corporation
        'PBR',  # Petróleo Brasileiro S.A. - Petrobras
    ],
    financials_tickers=[
        'BRK-B',  # Berkshire Hathaway Inc.
        'JPM',  # JPMorgan Chase & Co.
        'BAC',  # Bank of America Corporation
        'WFC',  # Wells Fargo & Company
        'C',  # Citigroup Inc.
        'GS',  # The Goldman Sachs Group, Inc.
        'MS',  # Morgan Stanley
        'BLK',  # BlackRock, Inc.
        'AXP',  # American Express Company
        'SPGI',  # S&P Global Inc.
    ],
    health_care_tickers=[
        'JNJ',  # Johnson & Johnson
        'UNH',  # UnitedHealth Group Incorporated
        'PFE',  # Pfizer Inc.
        'ABBV',  # AbbVie Inc.
        'MRK',  # Merck & Co., Inc.
        'TMO',  # Thermo Fisher Scientific Inc.
        'DHR',  # Danaher Corporation
        'ABT',  # Abbott Laboratories
        'MDT',  # Medtronic plc
        'LLY',  # Eli Lilly and Company
    ],
    industrials_tickers=[
        'HON',  # Honeywell International Inc.
        'UNP',  # Union Pacific Corporation
        'UPS',  # United Parcel Service, Inc.
        'CAT',  # Caterpillar Inc.
        'BA',  # The Boeing Company
        'MMM',  # 3M Company
        'GE',  # General Electric Company
        'DE',  # Deere & Company
        'LMT',  # Lockheed Martin Corporation
        'RTX',  # Raytheon Technologies Corporation
    ],
    information_technology_tickers=[
        'AAPL',  # Apple Inc.
        'MSFT',  # Microsoft Corporation
        'NVDA',  # NVIDIA Corporation
        'V',  # Visa Inc.
        'MA',  # Mastercard Incorporated
        'INTC',  # Intel Corporation
        'CSCO',  # Cisco Systems, Inc.
        'ADBE',  # Adobe Inc.
        'CRM',  # Salesforce, Inc.
        'ACN',  # Accenture plc
    ],
    materials_tickers=[
        'LIN',  # Linde plc
        'BHP',  # BHP Group
        'RIO',  # Rio Tinto Group
        'VALE',  # Vale S.A.
        'SHW',  # The Sherwin-Williams Company
        'ECL',  # Ecolab Inc.
        'APD',  # Air Products and Chemicals, Inc.
        'NEM',  # Newmont Corporation
        'FCX',  # Freeport-McMoRan Inc.
        'PPG',  # PPG Industries, Inc.
    ],
    real_estate_tickers=[
        'AMT',  # American Tower Corporation
        'PLD',  # Prologis, Inc.
        'CCI',  # Crown Castle International Corp.
        'EQIX',  # Equinix, Inc.
        'DLR',  # Digital Realty Trust, Inc.
        'SPG',  # Simon Property Group, Inc.
        'WELL',  # Welltower Inc.
        'PSA',  # Public Storage
        'CBRE',  # CBRE Group, Inc.
        'AVB',  # AvalonBay Communities, Inc.
    ],
    utilities_tickers=[
        'NEE',  # NextEra Energy, Inc.
        'DUK',  # Duke Energy Corporation
        'SO',  # The Southern Company
        'D',  # Dominion Energy, Inc.
        'EXC',  # Exelon Corporation
        'AEP',  # American Electric Power Company, Inc.
        'SRE',  # Sempra Energy
        'XEL',  # Xcel Energy Inc.
        'WEC',  # WEC Energy Group, Inc.
        'PEG',  # Public Service Enterprise Group Incorporated
    ]
)

# company_tickers_key = "oil_gas_tickers"
fill_period = 'recent'
# Fetch CIK mapping and lookup CIK for the given ticker
symbol_to_cik = requests.get(ciks_url, headers=headers).json()
cik_lookup = {val['ticker']: val['cik_str'] for key, val in symbol_to_cik.items()}

if __name__ == "__main__":
    recent_selected_releases_dfs = []
    for industry_group in company_tickers.keys():
        for company_ticker in company_tickers[industry_group]:
            try:
                cik = cik_lookup[company_ticker]

                # Fetch filings for the company using its CIK
                edgar_filings_url = f"https://data.sec.gov/submissions/CIK{cik:0>10}.json"
                edgar_filings = requests.get(edgar_filings_url, headers=headers).json()

                # Convert recent filings to DataFrame and filter for 10-Q and 10-K filings
                recent = pd.DataFrame(edgar_filings['filings'][fill_period])
                recent_selected_releases = recent.loc[recent['primaryDocDescription'].isin(['10-Q', '10-K'])].copy()
                recent_selected_releases['ticker'] = company_ticker

                # Construct URLs for the filtered filings
                base_url = "https://www.sec.gov/ixviewer/ix.html?doc=/Archives/edgar/data"
                recent_selected_releases['report_url'] = recent_selected_releases.apply(
                    lambda row: f"{base_url}/{cik}/{row['accessionNumber'].replace('-', '')}/{row['primaryDocument']}", axis=1)

                # Display the DataFrame with URLs
                # recent_selected_releases.to_csv(f'data/releases/{company_ticker}_recents_selected_releases.csv')
                recent_selected_releases_dfs.append(recent_selected_releases)
                print(recent_selected_releases)
            except ValueError:
                continue

    # Concatenate all DataFrames and export to CSV
    recent_selected_releases_df = pd.concat(recent_selected_releases_dfs).set_index('accessionNumber')
    recent_selected_releases_df.to_csv(f'data/releases/{fill_period}.csv')

