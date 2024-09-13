import requests
from bs4 import BeautifulSoup
import csv
import time
import re

base_url = "http://static.bacalaureat.edu.ro/2024/rapoarte/rezultate/index.html"
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
}


def get_page_data(page_number):
    response = session.post(
        f"http://static.bacalaureat.edu.ro/2024/rapoarte_sept/rezultate/dupa_medie/page_{page_number}.html",
        data=None,
        headers=headers,
        timeout=10,
    )
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def extract_data(soup):
    results = []
    main_table = soup.find("table", class_="mainTable")
    if main_table:
        table_rows = main_table.find_all("tr")[2:]
        for part_1, part_2 in zip(table_rows[::2], table_rows[1::2]):
            # dynamic javascript
            script_cells = part_1.find_all("script")[0].string
            pattern = re.compile(r'\["([^"]+)\s*<br>"]\s*=\s*"([^"]+)"(?:<br>)?')
            matches = re.findall(pattern, script_cells)

            # cleaned data
            candidate_data = [match[1].replace("<br>", "").strip() for match in matches]

            # parse basic td
            cells_1 = part_1.find_all("td")
            cell_data_1 = [cell.get_text(strip=True) for cell in cells_1]
            cells_2 = part_2.find_all("td")
            cell_data_2 = [cell.get_text(strip=True) for cell in cells_2]

            # print(cell_data_1)

            temp = (
                [cell_data_1[0]]
                + [candidate_data[0]]
                + cell_data_1[2:12]
                + [
                    cell_data_2[0],
                    cell_data_2[1],
                    cell_data_2[2],
                    cell_data_2[3],
                ]
                + cell_data_1[12:15]
                + cell_data_2[4:7]
                + [cell_data_1[15]]
                + cell_data_2[7:10]
                + [cell_data_1[16]]
                + candidate_data[1:3]
            )

            results.append(temp)
    return results


scraped_data = "scraped_data.csv"
fields = [
    "Nr. crt.",
    "Codul candidatului",
    "Unitatea de invatamant",
    "Judetul",
    "Promotie anterioara",
    "Forma invatamant",
    "Specializare",
    "Romana-Competente",
    "Romana-Scris",
    "Romana-Contestatie",
    "Romana-Final",
    "Limba materna-Denumire",
    "Limba materna-Competente",
    "Limba materna-Scris",
    "Limba materna-Contestatie",
    "Limba materna-Final",
    "Limba moderna",
    "Limba moderna-Nota",
    "DiscOblig-Denumire",
    "DiscOblig-Nota",
    "DiscOblig-Contestatie",
    "DiscOblig-Final",
    "DiscAlegere-Denumire",
    "DiscAlegere-Nota",
    "DiscAlegere-Contestatie",
    "DiscAlegere-Final",
    "Competente digitale",
    "Media",
    "Rezultatul Final",
]

with open(scraped_data, "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)


def main():
    initial_soup = get_page_data(1)

    total_num_pages = 3368

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
                soup = get_page_data(page_number)

                page_data = extract_data(soup)

                with open(scraped_data, "a", newline="") as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(page_data)

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
    # soup = get_page_data(1)
    # data = extract_data(soup)
