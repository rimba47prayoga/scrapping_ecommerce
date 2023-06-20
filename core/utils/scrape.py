from datetime import date
from typing import List, NamedTuple, Optional

import requests
import xlsxwriter
from bs4 import BeautifulSoup


class Product(NamedTuple):
    name: str
    price: str
    image_url: str
    seller_name: Optional[str]
    seller_location: str
    sold: Optional[str]
    source: str


class Scrape:
    """
    its only scrape from tokopedia, no need to use selenium.
    """
    def __init__(self, product_name: str):
        self.product_name = product_name
        self.results: List[Product] = []

    def _fetch(self, url: str) -> BeautifulSoup:
        response = requests.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15;"
                              " rv:109.0) Gecko/20100101 Firefox/114.0"
            }
        )
        if not response.ok:
            raise requests.exceptions.RequestException(
                f"Failed to fetch from {url} \n"
                f"status_code: {response.status_code}"
            )
        return BeautifulSoup(response.text, "html.parser")

    def _scrape_tokopedia(self) -> None:
        print(f"Scrapping {self.product_name} from Tokopedia")
        soup = self._fetch(
            f"https://www.tokopedia.com/search?st=&q={self.product_name}"
        )
        results = []
        for card in soup.select(".prd_container-card"):
            name = card.select_one(".prd_link-product-name").get_text()
            price = card.select_one(".prd_link-product-price").get_text()
            image_url = card.select_one("a img").attrs.get("src")
            seller_name = card.select_one(".prd_link-shop-name").get_text()
            seller_location = card.select_one(".prd_link-shop-loc").get_text()
            sold = card.select_one(".prd_label-integrity")
            if sold is not None:
                sold = sold.get_text()
            product = Product(
                name=name,
                price=price,
                image_url=image_url,
                seller_name=seller_name,
                seller_location=seller_location,
                sold=sold,
                source="Tokopedia"
            )
            results.append(product)

        if not results:
            raise Exception("No Product Found.")

        print(f"Success, found {len(results)} products.")
        # it needed when we do multi threading
        self.results.extend(results)

    def _save_to_excel(self):
        print("Writing to excels.")
        today = date.today()
        filename = f"scrape-results-{today}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        headers = [
            "name", "price", "image_url", "seller_name",
            "seller_location", "sold", "source"
        ]
        for index, header in enumerate(headers):
            worksheet.write(0, index, header)

        row = 1
        for product in self.results:
            col = 0
            for attr in headers:
                worksheet.write(row, col, getattr(product, attr))
                col += 1
            row += 1
        workbook.close()
        print("Success.")

    def execute(self):
        self._scrape_tokopedia()
        self._save_to_excel()
