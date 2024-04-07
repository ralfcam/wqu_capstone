import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

HTM_PATH = r"data/htm/"
TXT_PATH = r"data/text/"


def get_sec_form(url_: str, driver_: webdriver, htm_report_path_: str):
    driver_.get(url_)
    # Wait for the user to log in with a maximum timeout of 60 seconds
    # Assume there is a unique element that appears after successful login
    WebDriverWait(driver_, 5).until(EC.presence_of_element_located((By.TAG_NAME, "document")))
    # Save the page source to an HTML file
    with open(htm_report_path_, "w", encoding="utf-8") as file:
        file.write(driver_.page_source)
        print(f"Stored at {htm_report_path_} successfully")

    return htm_report_path_


def text_form_report(htm_report_path_, out_path, wanted_tag="document"):
    # Read the HTML file
    with open(htm_report_path_, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, "html.parser")
    soup = soup.find(wanted_tag)
    # Find the wanted tag or use the whole document if not found
    # if wanted_tag != "document":
    #     soup = soup.find(wanted_tag) or soup

    # Remove script, style, and unwanted tags
    unwanted_tags = ["script", "style", "header", "footer", "nav", "aside", "figure", "figcaption",
                     "table", "thead", "tbody"]
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()

    # Extract the clean text
    clean_text = soup.get_text(separator=" ", strip=True)

    # Construct the output file path
    base_name = os.path.basename(htm_report_path_)
    file_name_without_ext = os.path.splitext(base_name)[0]
    # str_report_path = os.path.join(os.path.dirname(htm_report_path), file_name_without_ext + ".txt")
    str_report_path = out_path + file_name_without_ext + ".txt"
    # Write the clean text to a file
    with open(str_report_path, "w", encoding="utf-8") as file:
        file.write(clean_text)

    print(f"Clean text extracted and saved to {str_report_path}")
    return str_report_path


if __name__ == "__main__":
    # Create Chrome options
    chrome_options = Options()
    # Add the option to use an existing Chrome session
    chrome_options.add_argument("--remote-debugging-port=9222")
    # Set the desired headers
    headers = {'User-Agent': "email@address.com"}
    # Add headers to the Chrome options
    for header_name, header_value in headers.items():
        chrome_options.add_argument(f"--header={header_name}={header_value}")
    # Create a new instance of the Chrome driver with the specified options
    driver = webdriver.Chrome(options=chrome_options)

    selected_releases_df = pd.read_csv("data/releases/oil_gas_tickers_recent_selected_releases.csv",
                                       index_col="accessionNumber")

    for url in selected_releases_df["report_url"]:
        htm_report_path = HTM_PATH + url.split("data/")[1].replace("/", "-")
        print(f"Stored at {htm_report_path} successfully")
        if not os.path.isfile(htm_report_path):
            try:
                get_sec_form(url, driver, htm_report_path)
            except:
                continue

    for htm_file in os.listdir(HTM_PATH):
        try:
            text_form_report(HTM_PATH + htm_file, "data/text/")
        except:
            continue