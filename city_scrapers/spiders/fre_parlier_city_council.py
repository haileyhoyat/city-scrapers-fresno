from city_scrapers_core.constants import CITY_COUNCIL
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parser


class FreParlierCityCouncilSpider(CityScrapersSpider):
    name = "fre_parlier_city_council"
    agency = "Parlier City Council"
    timezone = "America/Los_Angeles"
    start_urls = ["https://parlier.ca.us/agendas/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css("article[id='post-129'] p"):
            titleRaw = item.css("a::text").get()
            if (titleRaw != "12.16.21 REGULAR Agenda") and (
                "Cancellation" not in titleRaw
            ):
                meeting = Meeting(
                    title=self._parse_title(item),
                    description=self._parse_description(item),
                    classification=self._parse_classification(item),
                    start=self._parse_start(item),
                    end=self._parse_end(item),
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self._parse_location(item),
                    links=self._parse_links(item),
                    source=self._parse_source(response),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting
            if titleRaw == "12.16.21 REGULAR Agenda":
                break

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = ""
        titleRaw = item.css("a::text").get()
        if "REGULAR" in titleRaw:
            title = "Regular Meeting"

        if "SPECIAL" in titleRaw:
            title = "Special Meeting"

        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return CITY_COUNCIL

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""

        dateRaw = item.css("a::text").get()
        startDate = dateRaw.split()[0]
        startTime = "00:00:00"

        dt_obj = startDate + " " + startTime
        return parser().parse(dt_obj)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return "Time is unscrapable from the website, please check the meeting agenda link for start time."  # noqa

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "1100 E. Parlier Avenue. Parlier CA. 93648",
            "name": "Parlier City Hall",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": item.css("a::attr(href)").get(), "title": "Meeting Agenda"}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
