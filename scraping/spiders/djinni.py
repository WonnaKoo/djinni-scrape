import scrapy
from scrapy.http import Response
import re

from scraping.config import TECHOLOGIES_LIST


class DjinniSpider(scrapy.Spider):
    name = "djinni"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Python"]

    def parse(self, response: Response, **kwargs):
        for vacancy in response.css(".job-list-item"):
            vacancy_detail_url = vacancy.css(".job-list-item__link::attr(href)").get()
            yield scrapy.Request(
                url=response.urljoin(vacancy_detail_url), callback=self._parse_single_vacancy
            )

        next_page = response.css('li.page-item:last-child a.page-link::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_single_vacancy(response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get().strip(),
            "technologies": DjinniSpider.get_technologies(response),
            "english": DjinniSpider.english_level(response),
            "recruiter": "djinni.co" + DjinniSpider.recruiter_info(response),
            "url": response.url
        }

    @staticmethod
    def get_technologies(response: Response) -> list:
        current_vacancy_technologies = []

        for technologies in TECHOLOGIES_LIST:
            if technologies.lower() in response.css(".mb-4").get().lower():
                current_vacancy_technologies.append(technologies)

        return current_vacancy_technologies

    @staticmethod
    def english_level(response: Response) -> str:
        element = response.css('.job-additional-info--item-text:contains("Англійська")').get()
        return re.search("Англійська:\s*(\S+)", element).group(1)

    @staticmethod
    def recruiter_info(response: Response) -> str:
        url = response.css(".job-details--recruiter-name::attr(href)").get()
        return url