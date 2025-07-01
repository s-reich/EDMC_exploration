import unittest
import logging
from json import loads

import fake_tkinter as tk
from explorationhelper import ExplorationHelper


class MyTestCase(unittest.TestCase):
    dut = ExplorationHelper(logging.getLogger("pytest"), tk)

    def test_something(self):
        master: tk.Widget = tk.Widget()
        MyTestCase.dut.frame_init(master)

        MyTestCase.dut.register_organic(loads(
            """
            {
            "timestamp":"2025-06-20T19:08:01Z",
            "event":"ScanOrganic", "ScanType":"Analyse",
            "Genus":"$Codex_Ent_Bacterial_Genus_Name;", "Genus_Localised":"Bacterium",
            "Species":"$Codex_Ent_Bacterial_04_Name;", "Species_Localised":"Bacterium Acies",
            "Variant":"$Codex_Ent_Bacterial_04_Technetium_Name;", "Variant_Localised":"Bacterium Acies - Lime",
            "SystemAddress":357254206266, "Body":15
            }
            """
        ))
        MyTestCase.dut.register_organic(loads(
            """
            {
            "timestamp":"2025-06-20T19:08:01Z",
            "event":"ScanOrganic", "ScanType":"Scan",
            "Genus":"$Codex_Ent_Bacterial_Genus_Name;", "Genus_Localised":"Bacterium",
            "Species":"$Codex_Ent_Bacterial_04_Name;", "Species_Localised":"Bacterium Acies",
            "Variant":"$Codex_Ent_Bacterial_04_Technetium_Name;", "Variant_Localised":"Bacterium Acies - Lime",
            "SystemAddress":357254206266, "Body":12
            }
            """
        ))
        master.print_recursive()

    def test_value_range(self):
        from scanresult import ScanResult
        from body import Body

        body: Body = Body(loads(
            """
            { "timestamp":"2025-06-21T14:26:09Z", "event":"Scan", "ScanType":"Detailed",
            "BodyName":"Stock 1 Sector DD-F b13-2 B 3", "BodyID":19, "Parents":[ {"Star":2}, {"Null":0} ],
            "StarSystem":"Stock 1 Sector DD-F b13-2", "SystemAddress":5056922068609, "DistanceFromArrivalLS":3596.832139,
            "TidalLock":false, "TerraformState":"", "PlanetClass":"Icy body", "Atmosphere":"thin neon atmosphere",
            "AtmosphereType":"Neon", "AtmosphereComposition":[ { "Name":"Neon", "Percent":100.000000 } ],
            "Volcanism":"", "MassEM":0.194205, "Radius":4688739.500000, "SurfaceGravity":3.520929, 
            "SurfaceTemperature":53.402550, "SurfacePressure":123.803070, "Landable":true,
            "Materials":[ { "Name":"sulphur", "Percent":22.450626 }, { "Name":"carbon", "Percent":18.878649 },
            { "Name":"iron", "Percent":15.513670 }, { "Name":"phosphorus", "Percent":12.086437 },
            { "Name":"nickel", "Percent":11.733890 }, { "Name":"chromium", "Percent":6.977013 },
            { "Name":"manganese", "Percent":6.406988 }, { "Name":"germanium", "Percent":3.256915 },
            { "Name":"niobium", "Percent":1.060277 }, { "Name":"ruthenium", "Percent":0.958068 },
            { "Name":"mercury", "Percent":0.677456 } ], "Composition":{ "Ice":0.684784, "Rock":0.211554, "Metal":0.103662 },
            "SemiMajorAxis":76775185465.812683, "Eccentricity":0.002275, "OrbitalInclination":-0.074688,
            "Periapsis":211.571745, "OrbitalPeriod":35722767.114639, "AscendingNode":-151.959620,
            "MeanAnomaly":185.985544, "RotationPeriod":158529.148918, "AxialTilt":-0.444346,
            "WasDiscovered":true, "WasMapped":true
            }
            """
        ))

        assert body.was_mapped()
        assert not body.is_water()
        assert not body.is_terraform()

        # picked a bad planet for this, it only supports two bacteria and one fonticulua
        assert body.value_range_str([ScanResult(1)]) == '[1-19 M]'
        assert body.value_range_str([ScanResult(2)]) == '[20-21 M]'


if __name__ == '__main__':
    pass
