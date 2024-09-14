import requests
from bs4 import BeautifulSoup
import csv
import time

base_url = "http://bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx"
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
}


def get_initial_metadata(url):
    response = session.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    metadata = {
        "__EVENTTARGET": "ctl00$ContentPlaceHolderBody$DropDownList2",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": soup.find("input", {"name": "__VIEWSTATE"})["value"],
        "__VIEWSTATEGENERATOR": soup.find("input", {"name": "__VIEWSTATEGENERATOR"})[
            "value"
        ],
        "__EVENTVALIDATION": soup.find("input", {"name": "__EVENTVALIDATION"})["value"],
    }
    return metadata, soup


def get_page_data(url, metadata, page_number):
    metadata["ctl00$ContentPlaceHolderBody$DropDownList2"] = str(page_number)
    response = session.post(url, data=metadata, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def extract_data(soup):
    results = []
    main_table = soup.find("table", class_="mainTable")
    if main_table:
        table_rows = main_table.find_all("tr")[2:]
        for part_1, part_2 in zip(table_rows[::2], table_rows[1::2]):
            cells_1 = part_1.find_all("td")
            cell_data_1 = [cell.get_text(strip=True) for cell in cells_1]
            cells_2 = part_2.find_all("td")
            cell_data_2 = [cell.get_text(strip=True) for cell in cells_2]
            temp = [
                cell_data_1[0],
                cell_data_1[2],
                cell_data_1[3],
                cell_data_1[6],
                cell_data_1[8],
                cell_data_1[9],
                cell_data_1[10],
                cell_data_1[-5],
                cell_data_2[4],
                cell_data_2[5],
                cell_data_2[6],
                cell_data_1[-4],
                cell_data_2[7],
                cell_data_2[8],
                cell_data_2[9],
                cell_data_1[-2],
                cell_data_1[-1],
            ]
            results.append(temp)
    return results


scraped_data = "scraped_data.csv"
fields = [
    "Nr. crt.",
    "Unitatea de invatamant",
    "Judetul",
    "Specializare",
    "Romana-Scris",
    "Romana-Contestatie",
    "Romana-Final",
    "DiscOblig-Denumire",
    "DiscOblig-Scris",
    "DiscOblig-Contestatie",
    "DiscOblig-Final",
    "DiscAlegere-Denumire",
    "DiscAlegere-Scris",
    "DiscAlegere-Contestatie",
    "DiscAlegere-Final",
    "Media",
    "Rezultatul Final",
]

with open(scraped_data, "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)


def main():
    metadata, initial_soup = get_initial_metadata(base_url)

    total_num_pages = 13442

    print(f"Scraping page 1/{total_num_pages}...")
    data = extract_data(initial_soup)
    with open(scraped_data, "a", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)

    for page_number in range(2, total_num_pages + 1):
        print(f"Scraping page {page_number}/{total_num_pages}...")

        retries = 3
        while retries > 0:
            try:
                soup = get_page_data(base_url, metadata, page_number)

                viewstate = soup.find("input", {"name": "__VIEWSTATE"})
                viewstate_gen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
                eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})

                if not (viewstate and viewstate_gen and eventvalidation):
                    raise ValueError("Required metadata not found on page.")

                page_data = extract_data(soup)

                with open(scraped_data, "a", newline="") as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(page_data)

                metadata["__VIEWSTATE"] = viewstate["value"]
                metadata["__VIEWSTATEGENERATOR"] = viewstate_gen["value"]
                metadata["__EVENTVALIDATION"] = eventvalidation["value"]

                break

            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"An error occurred: {e}. Retrying...")
                retries -= 1
                time.sleep(5)

        if retries == 0:
            print(f"Failed to scrape page {page_number} after multiple attempts.")

    print("Scraping complete.")


if __name__ == "__main__":
    main()
