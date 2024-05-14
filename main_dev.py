import os
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict
from sec_edgar_downloader import Downloader as SECDownloader

TEMP_PATH = "sec-edgar-filings"
FILING_NAME = "full-submission.txt"
TARGET_DAYS = 28

company_tickers = dict(
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

# Flatten the dictionary into a single list of tickers
all_tickers = [ticker for sector in company_tickers.values() for ticker in sector]
out_dir = "output"
form_type = "10-Q"
after_date = "2023-06-01"
user_id = "WQU"
email = "user@wqu.com"

# Load the returns data
secs = pd.read_csv("data/structured_prices/ticks_daily_closing.csv", index_col="Date")
secs.index = pd.to_datetime(secs.index, format='%Y-%m-%d')
secs_q_shifted = secs.shift(-TARGET_DAYS)
secs_q_ret = (secs_q_shifted - secs) / secs


def get_return(ticker, report_date, df_returns):
    try:
        # Return the returns data for the next trading day
        return df_returns.at[report_date, ticker]
    except (KeyError, RecursionError):
        # Return None if no data is available for the next trading day
        next_trading_day = report_date + pd.Timedelta(days=1)
        return get_return(ticker, next_trading_day, df_returns)


def get_filing_segments(doc: str, filing_type: str):
    # Define item numbers for 10-K and 10-Q
    items_10k = ['1A', '1B', '1.', '7A', '7', '8']
    items_10q = ['1', '2', '3', '4', '5', '6']

    # Select the appropriate item numbers based on the filing type
    if filing_type == '10-K':
        items = items_10k
    elif filing_type == '10-Q':
        items = items_10q
    else:
        raise ValueError("Invalid filing type. Use '10-K' or '10-Q'.")

    # Create the regex pattern dynamically
    items_pattern = '|'.join(items)
    regex_pattern = fr'(>(Item|ITEM)(\s|&#160;|&nbsp;)({items_pattern})\.{{0,1}})|(ITEM\s({items_pattern}))'
    regex = re.compile(regex_pattern)

    # Find all matches in the document
    matches = regex.finditer(doc)

    return matches


class FileProcessor:
    def __init__(self, company_name: str, filing_type: str):
        self.company_name = company_name
        self.form_type = filing_type

    def load_parse_save(self, input_file_path: str, output_file_path: str, save_files=False) -> Dict:
        with open(input_file_path, 'r') as file:
            raw_txt = file.read()

        dates_info = self.extract_dates_info(raw_txt)
        doc = self.extract_document(raw_txt, self.form_type)
        cleaned_data = self.extract_section_text(doc, self.form_type)
        cleaned_data.update(dates_info)
        cleaned_data['companyName'] = self.company_name

        if save_files:
            with open(output_file_path, 'w') as json_file:
                json.dump(cleaned_data, json_file, indent=4)

        return cleaned_data

    def extract_dates_info(self, txt: str) -> Dict[str, str]:
        pattern = re.compile(
            r'CONFORMED PERIOD OF REPORT:\s*(\d+)\s*'
            r'FILED AS OF DATE:\s*(\d+)\s*'
            r'DATE AS OF CHANGE:\s*(\d+)',
            re.MULTILINE | re.DOTALL
        )
        match = pattern.search(txt)
        if match:
            return {
                "CONFORMED PERIOD OF REPORT": pd.to_datetime(match.group(1), format="%Y%m%d"),
                "FILED AS OF DATE": pd.to_datetime(match.group(2), format="%Y%m%d"),
                "DATE AS OF CHANGE": pd.to_datetime(match.group(3), format="%Y%m%d")
            }
        return {}

    def extract_document(self, txt: str, doc_type: str) -> str:
        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        type_pattern = re.compile(r'<TYPE>[^\n]+')

        doc_start_is = [x.end() for x in doc_start_pattern.finditer(txt)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(txt)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(txt)]

        for dtype, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if dtype.strip() == doc_type:
                return txt[doc_start:doc_end]
        return ""

    def extract_section_text(self, doc: str, filing_type: str) -> Dict[str, str]:
        matches = get_filing_segments(doc, filing_type)

        # Create a DataFrame from the matches
        item_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches], columns=['item', 'start', 'end'])
        item_df['item'] = item_df['item'].str.lower()

        # Replace unwanted characters
        item_df.replace({
            '&#160;': ' ',
            '&nbsp;': ' ',
            ' ': '',
            r'\.': '',
            '>': ''
        }, regex=True, inplace=True)

        # Sort and remove duplicates
        all_pos_df = item_df.sort_values('start').drop_duplicates(subset=['item'], keep='last').set_index('item')

        # Add section end using start of next section
        all_pos_df['sectionEnd'] = all_pos_df['start'].iloc[1:].tolist() + [len(doc)]

        # Filter to just the sections we care about
        if filing_type == '10-K':
            pos_df = all_pos_df.loc[['item1a', 'item1b', 'item1', 'item7a', 'item7', 'item8'], :]
        elif filing_type == '10-Q':
            pos_df = all_pos_df.loc[['item1', 'item2', 'item3', 'item4', 'item5', 'item6'], :]

        # Extract text for each section
        res = {i: self.extract_text(row, doc) for i, row in pos_df.iterrows()}

        return res

    def extract_text(self, row: pd.Series, txt: str) -> str:
        section_txt = txt[row.start:row.sectionEnd].replace('Error! Bookmark not defined.', '')
        return self.beautify_text(section_txt)

    def beautify_text(self, txt: str) -> str:
        return BeautifulSoup(txt, 'lxml').get_text('\n')


class FilingManager:
    def __init__(self, company_list: list, out_dir: str, user_id: str, email: str, filing_type: str):
        self.company_list = company_list
        self.out_dir = out_dir
        self.downloader = SECDownloader(user_id, email)
        self.form_type = filing_type

    def process_filings(self, after: str):
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        all_data = []
        total = len(self.company_list)
        print(f'=== Downloading {total:,} {self.form_type} filings ===')

        for count, company_cik in enumerate(self.company_list, start=1):
            print(f'--- Downloading {count:,} of {total:,} {self.form_type} filings for CIK: {company_cik}')
            try:
                # self.downloader.get(self.form_type, company_cik, after=after)
                filing_list = os.listdir(os.path.join(TEMP_PATH, company_cik, self.form_type))

                for filing in filing_list:
                    raw_file_path = os.path.join(TEMP_PATH, company_cik, self.form_type, filing, FILING_NAME)
                    output_file_path = os.path.join(self.out_dir, filing)
                    try:
                        processor = FileProcessor(company_cik, self.form_type)
                        data = processor.load_parse_save(raw_file_path, output_file_path)
                        all_data.append(data)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

        df = pd.DataFrame(all_data)

        # Define the replacements
        replacements = {
            "\\n": " ",
            "\\*\\*": "",
            "\xa0": "",
            ">Item\\s*(\\d+)*.": ""
        }

        # Apply the replacements to every cell of columns with data type `str`
        for col in df.select_dtypes(include=['object']).columns:
            df[col].replace(replacements, regex=True, inplace=True)

        # Add the following day's return
        df[f'{TARGET_DAYS}_days_return'] = df.apply(
            lambda row: get_return(row['companyName'], row['FILED AS OF DATE'], secs_q_ret), axis=1)

        df.to_csv(os.path.join(self.out_dir, f'compiled_{self.form_type.lower()}_data.csv'), index=False)


def main() -> int:
    filing_manager = FilingManager(all_tickers, out_dir, user_id, email, form_type)
    filing_manager.process_filings(after_date)
    return 0


if __name__ == "__main__":
    main()
