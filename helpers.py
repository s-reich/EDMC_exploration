def get_bio_signal_count(entry: dict) -> int:
    """
    looking for this one:
    "Signals": [
        {"Type": "$SAA_SignalType_Biological;", "Type_Localised": "Biological", "Count": 3}
    ],
    """
    if "Signals" not in entry:
        return 0

    for s in entry["Signals"]:
        if s["Type"] == "$SAA_SignalType_Biological;":
            return s["Count"]
    return 0


def get_genus_list(entry: dict, body_info: dict) -> dict[str, tuple]:
    """
    looking for this one:
    "Genuses":[
            { "Genus":"$Codex_Ent_Bacterial_Genus_Name;", "Genus_Localised":"Bacterium" },
            { "Genus":"$Codex_Ent_Conchas_Genus_Name;", "Genus_Localised":"Concha" },
            { "Genus":"$Codex_Ent_Osseus_Genus_Name;", "Genus_Localised":"Osseus" }
    ]
    """
    res: dict[str, tuple] = {}
    for x in entry["Genuses"]:
        genus_name: str = x['Genus_Localised']
        res[genus_name] = get_value_range(genus_name, body_info)
    return res


def get_value_range(genus_name: str, body_info: dict) -> tuple[float, float]:
    from biologial import all_bios

    min_value: float = 999.0
    max_value: float = 0.0
    genus_known: bool = False

    for b in all_bios:
        if b.category != genus_name:
            continue
        genus_known = True
        if body_info and not b.can_grow_on(body_info):
            continue

        if b.net_worth > max_value:
            max_value = b.net_worth
        if b.net_worth < min_value:
            min_value = b.net_worth

    if min_value == 999.0:
        return (0.0,0.0) if genus_known else (1.0, 999.0)

    return min_value, max_value


def get_value_range_anonymous(body: dict, count: int) -> tuple[float, float]:
    """
    More complicated function... get value range for every genus,
    and then pick the <count> worst and best for the range.
    """
    from biologial import all_bios

    genus_value_ranges: list[tuple[str,float,float]] = []
    for genus in set([b.category for b in all_bios]):
        mn, mx = get_value_range(genus, body)
        if mn == 0.0:
            # genus can not grow on that planet
            continue
        genus_value_ranges.append(
            (genus, mn, mx)
        )

    if not genus_value_ranges:
        return 0.0, 0.0

    # lower bound
    genus_value_ranges.sort(key=lambda v: v[1])
    min_value: float = sum([v[1] for v in genus_value_ranges[:count]])

    # upper bound
    genus_value_ranges.sort(key=lambda v: v[2])
    max_value: float = sum([v[2] for v in genus_value_ranges[-count:]])

    return min_value, max_value


def get_species_value(species_name: str) -> float:
    """
    Species name is basically "<genus> <subtype>", without the color variant
    """
    from biologial import all_bios

    for b in all_bios:
        if f'{b.category} {b.name}' == species_name:
            return b.net_worth
    return 999.0


def strip_variant(variant_name: str) -> (str, str):
    """
        Receives a full variant name like "Bacterium Acies - Aquamarine"
        and returns the genus and species parts ("Bacterium", "Acies")
    """
    from biologial import all_bios

    species_name: str = variant_name.split(" - ")[0]
    for b in all_bios:
        if f'{b.category} {b.name}' == species_name:
            return b.category, b.name
    # fallback: split on space and return first two parts
    fallback = variant_name.split(" ", 3)
    return fallback[0], fallback[1]


def scans_to_str(body_id: int, scan_list: list) -> str:
    from json import dumps

    obj: dict = {
        "BodyID": body_id,
        "ScanResults": [
            { s.name: s.signature_count }
            for s in scan_list
        ]
    }
    return dumps(obj)


def test_scan_to_str() -> None:
    from scanresult import ScanResult, ScanFromOrbit, ScanWithShipOrSuit
    assert scans_to_str(10, [ScanResult(3)]) == """{"BodyID": 10, "ScanResults": [{"any": 3}]}"""
    assert scans_to_str(11, [ScanFromOrbit('Bacterium', {})]) == """{"BodyID": 11, "ScanResults": [{"Bacterium": 1}]}"""
    assert scans_to_str(14, [ScanWithShipOrSuit('Tubus Super')]) == """{"BodyID": 14, "ScanResults": [{"Tubus Super": 0}]}"""


def str_to_scans(data: list[str], system_bodies: dict[int, 'Body']) -> dict[int, list['ScanResult']]:
    from json import loads
    from body import Body
    from scanresult import ScanResult

    res: dict = {}
    for d in data:
        decoded: dict = loads(d)
        body_id: int = decoded['BodyID']
        body: Body = system_bodies[body_id] if body_id in system_bodies else Body({})
        res[body_id] = [
            ScanResult.deserialize(dd, body)
            for dd in decoded['ScanResults']
        ]
        print(f'#### loaded biosigns for body {body_id}: {res[body_id]}')
    return res
