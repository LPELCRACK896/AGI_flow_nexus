from itemadapter import ItemAdapter
from components.scrapp.scrapp.items import StationItem, WeatherStationItem


class UniversalPipeline:
    def process_item(self, item, spider):
        if isinstance(item, StationItem):
            return StationPipeline().process_item(item, spider)

        if isinstance(item, WeatherStationItem):
            return WeatherStationPipeline().process_item(item, spider)

        return item


class StationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        spider.logger.info(f"Processing StationItem with fields: {field_names}")

        # Perform your logic for StationItem
        # For example, you might want to store this in a database or a file
        # Example:
        # save_to_database(item)

        return item


class WeatherStationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        spider.logger.info(f"Processing WeatherStationItem with fields: {field_names}")

        # Perform your logic for WeatherStationItem
        # For example, you might want to store this in a database or a file
        # Example:
        # save_to_database(item)

        return item


class IccScraperPipeline:
    def process_item(self, item, spider):
        return item

    def start(self, item, spider):
        pass