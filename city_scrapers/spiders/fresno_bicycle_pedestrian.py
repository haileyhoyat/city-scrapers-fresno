from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parser


class FresnoBicyclePedestrianSpider(CityScrapersSpider):
    name = "fresno_bicycle_pedestrian"
    agency = "Fresno Bicycle and Pedestrian Advisory Committee"
    timezone = "America/Chicago"
    start_urls = ["https://fresno.legistar.com/Calendar.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".rgMasterTable tr")[1:]:
            title = item.css("td:nth-child(1) font font::text").get()
            if title == "Bicycle and Pedestrian Advisory Committee":
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

    def _parse_title(self, item):
        """Parse or generate meeting title"""
        title = item.css("td:nth-child(1) font font::text").get()
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return ADVISORY_COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object. Added by pipeline if None"""
        date = item.css("td:nth-child(2) font::text").get()
        time = item.css("td:nth-child(4) font font::text").get()
        dt_obj = date + " " + time
        return parser().parse(dt_obj)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        location1 = item.css("td:nth-child(5) font::text").get()
        location2 = item.css("td:nth-child(5) font em::text").get()
        return {"address": location1 + " " + location2, "name": ""}

    def _parse_links(self, item):
        """Parse or generate links."""
        return [
            {
                "hrefMeetingDetails": item.css(
                    "td:nth-child(6) font a::attr(href)"
                ).get(),  # noqa
                "titleMeetingDetails": "Meeting Details",
                "hrefAgenda": item.css("td:nth-child(7) font span a::attr(href)").get(),
                "titleAgenda": "Meeting Agenda",
            }
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
