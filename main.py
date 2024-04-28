import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

HTM_PATH = r"data/htm/"
TXT_PATH = r"data/text/"


def get_sec_form(url_: str, driver_: webdriver, htm_report_path_: str):
    driver_.get(url_)
    try:
        # Wait for the "document" tag to be present with a maximum timeout of 10 seconds
        WebDriverWait(driver_, 5).until(EC.presence_of_element_located((By.ID, "dynamic-xbrl-form")))
        # WebDriverWait(driver_, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # WebDriverWait(driver_, 5).until(
        #     lambda driver__: driver__.execute_script("return document.readyState") == "complete"
        # )
    except TimeoutException:
        print("Timed out waiting for page `document` to load")
        return None

    # Save the page source to an HTML file
    with open(htm_report_path_, "w", encoding="utf-8") as file:
        file.write(driver_.page_source)
        print(f"Stored at {htm_report_path_} successfully")

    return htm_report_path_


def text_form_report(htm_report_path_, out_path, wanted_id="dynamic-xbrl-form"):
    # Read the HTML file
    with open(htm_report_path_, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Create a BeautifulSoup object

    soup = BeautifulSoup(html_content, "html.parser")
    # soup = soup.find(id=wanted_id)  # div with id #dynamic-xbrl-form

    # unwanted_tags = ["script", "style", "header", "footer", "nav", "aside", "figure", "figcaption",
    #                  "table", "thead", "tbody"]
    #
    # for tag in unwanted_tags:
    #     for element in soup.find_all(tag):
    #         element.decompose()

    # Further filter for text tags (a, p, H1, ..., span) in the HTML file
    # tags_to_find = ['a', 'p', 'span'] + [f'h{i}' for i in range(1, 7)]
    # text_tags = soup.find_all(tags_to_find)

    # Extract the clean text from the filtered tags
    # clean_text = r' '.join(tag.get_text(separator=" ", strip=True) for tag in text_tags).strip()
    # clean_text = soup.get_text(separator=" ", strip=True)
    # If opening a local HTML file:
    # with open('path_to_file.html', 'r') as file:
    #     html_content = file.read()


    # Extract text from the HTML
    # Find all table elements and decompose them
    tables = soup.find_all('table')
    for table in tables:
        table.decompose()

    clean_text = soup.get_text(separator=' ', strip=True)
    clean_text = clean_text.replace("\n", "").replace("\t", "")
    clean_text = clean_text.split("UNITED")[1]
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
    # # Create Chrome options
    # chrome_options = Options()
    # # Add the option to use an existing Chrome session
    # chrome_options.add_argument("--remote-debugging-port=9222")
    # # Set the desired headers
    # headers = {'User-Agent': "email@address.com"}
    # # Add headers to the Chrome options
    # for header_name, header_value in headers.items():
    #     chrome_options.add_argument(f"--header={header_name}={header_value}")
    # # Create a new instance of the Chrome driver with the specified options
    # driver = webdriver.Chrome(options=chrome_options)
    #
    # selected_releases_df = pd.read_csv("data/releases/recent.csv",
    #                                    index_col="accessionNumber")
    #
    # for url in selected_releases_df["report_url"]:
    #     htm_report_path = HTM_PATH + url.split("data/")[1].replace("/", "-")
    #
    #     if not os.path.isfile(htm_report_path):
    #         try:
    #             get_sec_form(url, driver, htm_report_path)
    #             # print(f"Stored at {htm_report_path} successfully")
    #         except Exception as e:
    #             print(f"Excepted {htm_report_path} with: {e}")
    #             continue
    #     else:
    #         print(f"Skipping {htm_report_path}")
    # driver.quit()

    #######################################################################

    for htm_file in os.listdir(HTM_PATH):
        txt_report_path = TXT_PATH + htm_file.replace("htm", "txt")
        if not os.path.isfile(txt_report_path):
            try:
                text_form_report(HTM_PATH + htm_file, "data/text/")
            except AttributeError:
                try:
                    os.remove(HTM_PATH + htm_file)
                    print(f"Deleted {htm_file}")
                except OSError as e:
                    print(f"Error deleting {htm_file}: {e}")
                continue
            except Exception as e:
                print(f"Excepted {htm_file} with: {e}")
                continue
        else:
            print(f"Skipping {htm_file}")
