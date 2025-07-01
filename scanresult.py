from helpers import get_value_range


class ScanResult:
    def __init__(self, signature_count: int, name: str = 'any'):
        self.signature_count: int = signature_count
        self.name: str = name

    def genus(self) -> str:
        return "None"

    def is_simple(self) -> bool:
        """Return True if this is a simple planetary signature count, as returned from the FSS scanner"""
        return True

    def is_vague(self) -> bool:
        """Return True if this is a simple genus type, as returned from the Planetary Detail scanner"""
        return False

    def is_exact(self) -> bool:
        """
        Return True if this is an exact Species definition,
        as returned from the Ship's comp. scanner or the artemis suit
        """
        return False

    def is_done(self) -> bool:
        """Return True if this has been scanned three times using the Artemis suit"""
        return False

    def get_display_color(self) -> str:
        if self.is_simple():
            return 'black'
        if self.is_vague():
            return 'blue'
        return 'green'

    def get_display_string(self) -> str:
        return f'({self.signature_count} bios)'

    def get_value_range(self) -> (float, float):
        # TODO: this should be properly filtered by planet type and available species
        #       currently we re-handle it in Body::value_range
        return -1.0, 1.0

    def emplace_in_list(self, result_list: list['ScanResult']) -> None:
        result_list.append(self)

    @staticmethod
    def deserialize(data: dict, body: 'Body') -> 'ScanResult':
        assert len(data) == 1
        name, count = list(data.items())[0]

        if name == "any":
            return ScanResult(count)

        from biologial import all_bios
        for b in all_bios:
            if name == b.category:
                return ScanFromOrbit(name, body)
            if name == b.display_name():
                res = ScanWithShipOrSuit(name)
                res.signature_count = count
                return res
        # should not reach here...
        return ScanResult(99)


class ScanFromOrbit(ScanResult):
    def __init__(self, genus: str, planet: dict):
        super().__init__(1, genus)
        self.genus_name: str = genus
        self.min_value, self.max_value = get_value_range(genus, planet)

    def genus(self) -> str:
        return self.genus_name

    def is_simple(self) -> bool:
        return False

    def is_vague(self) -> bool:
        return True

    def get_display_string(self) -> str:
        if self.min_value == 999.0:
            return f'{self.genus_name} (?)'
        if self.min_value == self.max_value:
            return f'{self.genus_name} ({self.min_value:.0f} M)'
        return f'{self.genus_name} ({self.min_value:.0f}-{self.max_value:.0f} M)'

    def get_value_range(self) -> (float, float):
        return self.min_value, self.max_value


class ScanWithShipOrSuit(ScanResult):
    def __init__(self, species: str):
        from biologial import Biological, get_bio_for_species

        super().__init__(0, species)
        self.bio: Biological = get_bio_for_species(species)

    def genus(self) -> str:
        return self.bio.category

    def is_simple(self) -> bool:
        return False

    def is_exact(self) -> bool:
        return True

    def is_done(self) -> bool:
        return self.signature_count == 1

    def get_display_string(self) -> str:
        return f'{self.bio.display_name()} ({self.bio.net_worth:.0f} M)'

    def get_value_range(self) -> (float, float):
        return self.bio.net_worth, self.bio.net_worth

    def emplace_in_list(self, result_list: list['ScanResult']) -> None:
        # find some entry to update or replace

        for old_scan in result_list:
            if old_scan.is_vague() and old_scan.name == self.genus():
                result_list.remove(old_scan)
                result_list.insert(0, self)
                return
            # that leaves only non-vagues
            if isinstance(old_scan, ScanWithShipOrSuit):
                oss: ScanWithShipOrSuit = old_scan
                if oss.name == self.name:
                    if self.signature_count:
                        oss.signature_count = self.signature_count
                    return
        result_list.append(self)
