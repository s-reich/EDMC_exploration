class FakeConfig:
    data: dict = {}

    def get_str(self, key: str, default: str = "") -> str:
        return self.data[key] if key in self.data else default

    def get_list(self, key: str, default: list = ()) -> list:
        return self.data[key] if key in self.data else default

    def set(self, key: str, value: str|list|int) -> None:
        self.data[key] = value
