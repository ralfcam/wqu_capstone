from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

HTM_PATH = r"data/htm/"


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

    save_path = HTM_PATH + url_.split("data/")[1].replace("/", "-")
    # Save the page source to an HTML file
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(driver.page_source)
        print(f"Stored at {save_path} successfully")

    return save_path


if __name__ == "__main__":
    url_ = "https://www.sec.gov/ixviewer/ix.html?doc=/Archives/edgar/data/101778/000010177823000146/mro-20230930.htm"
    get_sec_form(url_)
