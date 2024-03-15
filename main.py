from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

HTM_PATH = r"data/htm/"
TXT_PATH = r"data/text/"


def get_sec_form(url_: str, chrome_options: Options() = None):
    if chrome_options is None:
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
    driver.get(url_)

    # Wait for the user to log in with a maximum timeout of 60 seconds
    # Assume there is a unique element that appears after successful login
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "fact-identifier-5"))
    )

    htm_report_path = HTM_PATH + url_.split("data/")[1].replace("/", "-")
    # Save the page source to an HTML file
    with open(htm_report_path, "w", encoding="utf-8") as file:
        file.write(driver.page_source)
        print(f"Stored at {htm_report_path} successfully")

    return htm_report_path


def text_form_report(htm_report_path):
    # Read the HTML file
    with open(htm_report_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script, style, and unwanted tags
    unwanted_tags = ["script", "style", "header", "footer", "nav", "aside", "figure", "figcaption",
                     "table", "thead", "tbody"]

    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()

    # Remove unwanted attributes from tags
    for tag in soup.find_all(True):
        tag.attrs = {}

    # Extract the clean text
    clean_text = soup.get_text(separator="\n", strip=True)

    str_report_path = TXT_PATH + htm_report_path.split("htm/")[1].split(".")[0] + ".txt"

    # Write the clean text to a file
    with open(str_report_path, "w", encoding="utf-8") as file:
        file.write(clean_text)

    print("Clean text extracted and saved to clean_text.txt")
    return str_report_path


if __name__ == "__main__":
    # url_ = "https://www.sec.gov/ixviewer/ix.html?doc=/Archives/edgar/data/101778/000010177823000146/mro-20230930.htm"
    # get_sec_form(url_)
    text_form_report("data/htm/101778-000010177823000146-mro-20230930.htm")
