"""Over-abstracted pipeline with unnecessary class hierarchy and deep nesting."""

from typing import Any, Optional


class AbstractDataProvider:
    pass


class ConcreteDataProvider(AbstractDataProvider):
    def get_data(self) -> dict[str, Any]:
        return {"user": {"profile": {"settings": {"theme": "dark"}}}}


class DataExtractorFactory:
    @staticmethod
    def create() -> ConcreteDataProvider:
        return ConcreteDataProvider()


class SettingExtractor:
    def __init__(self, provider: ConcreteDataProvider) -> None:
        self.provider = provider

    def extract_theme(self) -> Optional[str]:
        data = self.provider.get_data()
        if data:
            if "user" in data:
                if "profile" in data["user"]:
                    if "settings" in data["user"]["profile"]:
                        if "theme" in data["user"]["profile"]["settings"]:
                            return data["user"]["profile"]["settings"]["theme"]
        return None
