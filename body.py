from scanresult import ScanResult
from helpers import get_value_range_anonymous


class Body(dict):
    def __init__(self, src: dict):
        super().__init__(src)

        if 'BodyClass' not in self:
            self['BodyClass'] = 'unknown'

    def pget(self, name: str) -> str:
        if name not in self:
            return ""
        return self[name]

    def id(self) -> int:
        return self["BodyID"] if "BodyID" in self else 0

    def was_mapped(self) -> bool:
        """
        Return true if the body has already been mapped.
        What we actually need is "has first footfall", but unfortunately, the game's journal does not list that
        """
        if 'WasDiscovered' in self and not self['WasDiscovered']:
            # not discovered? can't be mapped or explored yet
            return False

        if 'WasMapped' in self:
            # lets see...
            return self['WasMapped']

        # not sure about this, but let us hope for the best
        return False

    def is_terraform(self) -> bool:
        return self.pget('TerraformState') != ""

    def is_water(self) -> bool:
        return self.pget('PlanetClass') == "Water world"

    def is_earthlike(self) -> bool:
        return self.pget('PlanetClass') == 'Earthlike body'

    def is_ammonia(self) -> bool:
        return self.pget('PlanetClass') == 'Ammonia world'

    def is_rocky(self) -> bool:
        return self.pget('PlanetClass') == 'Rocky body'

    def is_high_metal(self) -> bool:
        return self.pget('PlanetClass') == 'High metal content body'

    def name(self) -> str:
        return (
            self["BodyName"] if "BodyName" in self
            else f'# {self["BodyID"]}' if "BodyID" in self
            else f'{self}'
        )

    def display_color(self) -> str:
        """
        Return planet base color depending on properties.
        """
        if self.is_terraform():
            return 'cyan' if self.is_water() else 'saddle brown'
        if self.is_earthlike():
            return 'forest green'
        return 'blue' if self.is_water() else 'black'

    def value_range_str(self, bios: list[ScanResult]) -> str:
        min_sum: float = self.discovery_value()
        max_sum: float = min_sum
        # first finder's fee
        factor: float = 1 if self.was_mapped() else 5

        for b in bios:
            x,y = b.get_value_range()
            if x == -1:
                # generic "X signatures" .. recalculate
                # TODO: should not be done in the redraw part
                x,y = get_value_range_anonymous(self, b.signature_count)

            min_sum += x * factor
            max_sum += y * factor

        if min_sum == max_sum:
            return f'[{min_sum:.0f} M]'
        return f'[{min_sum:.0f}-{max_sum:.0f} M]'

    def discovery_value(self) -> float:
        discovery_bonus: float = 1.0 if self.was_mapped() else 2.88
        terraform: bool = self.is_terraform()
        if self.is_water():
            return discovery_bonus * (
                1.119 if terraform else 0.416
            )
        if self.is_earthlike():
            return discovery_bonus * 1.126
        if self.is_ammonia():
            return discovery_bonus * 0.598
        if self.is_high_metal():
            return discovery_bonus * (
                0.683 if terraform else 0.059
            )
        if self.is_rocky():
            return discovery_bonus * (
                0.540 if terraform else 0.001
            )
        return 0.0


def test_value() -> None:
    assert 0.0 == Body({}).discovery_value()
    assert 1.0 > Body({"PlanetClass": "Rocky body"}).discovery_value()
    assert 1.0 < Body({"PlanetClass": "Rocky body", "TerraformState": "yes"}).discovery_value()
    assert 1.0 > Body({"PlanetClass": "Rocky body", "TerraformState": "yes", "WasMapped": True}).discovery_value()
    assert 1.0 < Body({"PlanetClass": "Earthlike body", "WasMapped": True}).discovery_value()
    assert (
        Body({"PlanetClass": "Earthlike body", "WasMapped": True}).discovery_value()
        <
        Body({"PlanetClass": "Earthlike body", "WasMapped": False}).discovery_value()
    )
