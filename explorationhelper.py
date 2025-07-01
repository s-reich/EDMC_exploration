import tkinter
from logging import Logger
from json import loads, dumps
from config import AbstractConfig


import helpers
from scanresult import ScanResult, ScanFromOrbit, ScanWithShipOrSuit
from body import Body

tk = tkinter


class ExplorationHelper:
    def __init__(self, logger: Logger, config: AbstractConfig, tk_impl: any = None):
        global tk
        self.logger: Logger = logger
        self.config: AbstractConfig = config
        self.current_system_name: str = self.load_system_name()
        self.system_bodies: dict[int, Body] = self.load_bodies()
        self.bio_signs: dict[int, list[ScanResult]] = self.load_biosigns()
        if tk_impl is not None:
            tk = tk_impl
        self.tk_frame: tk.Frame|None = None

    def load_system_name(self) -> str:
        return self.config.get_str("explorationhelper.current_system", default="")

    def load_bodies(self) -> dict[int, Body]:
        res = {}
        for v in self.config.get_list("explorationhelper.known_bodies", default=[]):
            b: Body = Body(loads(v))
            self.logger.info(f"Loaded body {b.id()} worth {b.discovery_value()}")
            res[b.id()] = b
        return res

    def load_biosigns(self) -> dict[int, list[ScanResult]]:
        return helpers.str_to_scans(
            self.config.get_list("explorationhelper.known_bios", default=[]),
            self.system_bodies
        )

    def override_config(self, config_mock: any) -> None:
        self.config = config_mock

    def frame_init(self, parent: tk.Widget) -> tk.Frame:
        self.tk_frame = tk.Frame(parent)
        self.frame_redraw()
        return self.tk_frame

    def frame_clear(self) -> None:
        for w in self.tk_frame.winfo_children():
            w.destroy()

    def frame_redraw(self) -> None:
        """
        Refresh the tk window contents, which is a table/grid of planets with their
        properties related to exobiology
        """
        self.frame_clear()
        row: int = 0

        # TODO: store stuff to config
        self.config.set("explorationhelper.current_system", self.current_system_name)
        self.config.set(
            "explorationhelper.known_bodies",
            [
                dumps(b)
                for b in self.system_bodies.values()
            ]
        )
        self.config.set(
            "explorationhelper.known_bios",
            [
                helpers.scans_to_str(body_id, scan_list)
                for body_id, scan_list in self.bio_signs.items()
            ]
        )

        # TODO: sort by distance from entry point ?
        #       sorting by Body-ID seems to be ok.
        for body_id, body in sorted(self.system_bodies.items()):
            result_list: list[ScanResult] = (
                self.bio_signs[body_id]
                if body_id in self.bio_signs
                else []
            )
            if body.discovery_value() < 1.0 and not result_list:
                # not worth to be listed
                continue

            """
            Display of of those:
                <body-name> | (x) | <N> bios: <min> - <max> $$         
                <body-name> | (y) | genus1: A-B, genus2: C-D, ...             
                <body-name> | (z) | genus1: A-B, genus2: C-D, ...      
                <body-name> | (x) | name1: A $$, bio2: C-D, ...
                
                x/y/z: symbols for already mapped, $$ > 10M, ...           
            """
            body: Body = self.system_bodies[body_id]
            name_props: dict = {
                "text": body.name().removeprefix(self.current_system_name),
                "justify": tk.RIGHT,
                "fg": body.display_color()
            }
            symbol_props: dict = {
                "text": body.value_range_str(result_list),
                "justify": tk.RIGHT
            }
            if not body.was_mapped():
                name_props['background'] = 'gold'
                symbol_props['background'] = 'gold'

            p_name = tk.Label(self.tk_frame, **name_props)
            p_name.grid(row=row, column=0, sticky=tk.W)

            p_symbol = tk.Label(self.tk_frame, **symbol_props)
            p_symbol.grid(row=row, column=1, sticky=tk.W)

            col: int = 2
            for scan_result in result_list:
                color: str = scan_result.get_display_color()
                text: str = scan_result.get_display_string()
                label_props: dict = {
                    "text": text,
                    "justify": tk.LEFT,
                    "fg": color
                }
                if scan_result.is_done():
                    label_props['font'] = "-weight bold"

                p_desc = tk.Label(self.tk_frame, **label_props)
                p_desc.grid(row=row, column=col, sticky=tk.W)
                col += 1
            row += 1

    def clear_all(self) -> None:
        self.system_bodies.clear()
        self.bio_signs.clear()
        self.frame_redraw()

    def register_system(self, entry:dict) -> None:
        self.current_system_name = entry['StarSystem']
        self.clear_all()
        # TODO: write current system to config

    def register_detail_scan(self, entry: dict) -> None:
        """
        Handles result of a detailed planet scan, extracting genus list:
        {
            "timestamp":"2025-06-13T15:28:13Z",
            "event":"SAASignalsFound",
            "BodyName":"Vulpecula Dark Region QT-R b4-4 4 a",
            "SystemAddress":9458994456113,
            "BodyID":10,
            "Signals":[
                { "Type":"$SAA_SignalType_Biological;", "Type_Localised":"Biological", "Count":3 }
                ],
            "Genuses":[
                { "Genus":"$Codex_Ent_Bacterial_Genus_Name;", "Genus_Localised":"Bacterium" },
                { "Genus":"$Codex_Ent_Conchas_Genus_Name;", "Genus_Localised":"Concha" },
                { "Genus":"$Codex_Ent_Osseus_Genus_Name;", "Genus_Localised":"Osseus" }
                ]
        }
        """
        if "Genuses" not in entry:
            # not a scan we are interested in
            return

        body_id: int = entry["BodyID"]
        if body_id not in self.system_bodies:
            self.system_bodies[body_id] = Body({"BodyName": entry['BodyName']})
        body: Body = self.system_bodies[body_id]

        if body_id  not in self.bio_signs:
            self.bio_signs[body_id] = []
        scan_results: list[ScanResult] = self.bio_signs[body_id]

        # we check existing scans first -- this may be a repeat event where we already have better data
        for b in scan_results:
            if b.is_done() or b.is_exact():
                self.logger.info(f'Ignoring SSA data for known {body.name()}')
                return
        scan_results.clear()

        for genus in entry["Genuses"]:
            scan_results.append(ScanFromOrbit(genus['Genus_Localised'], body))

        # self.logger.info(f'Bioscan result for {body.name()}: {scan_results}')
        self.frame_redraw()

    def register_organic(self, event: dict) -> None:
        """
        register detail scan of some organic, so we can fix price display
                {
            "timestamp":"2025-06-13T15:29:38Z",
            "event":"ScanOrganic",
            "ScanType":"Sample",
                // or "Log"
                // or "Analyse" --> 3rd closeup scan
            "Genus":"$Codex_Ent_Conchas_Genus_Name;",
            "Genus_Localised":"Concha",
            "Species":"$Codex_Ent_Conchas_04_Name;",
            "Species_Localised":"Concha Biconcavis",
            "Variant":"$Codex_Ent_Conchas_04_Polonium_Name;",
            "Variant_Localised":"Concha Biconcavis - Red",
            "SystemAddress":9458994456113,
            "Body":10
        }
        """
        body_id: int = event['Body']
        # genus_name: str = event['Genus_Localised']
        species_name: str = event['Species_Localised']

        new_scan: ScanWithShipOrSuit = ScanWithShipOrSuit(species_name)
        if event['ScanType'] == 'Analyse':
            new_scan.signature_count = 1

        if body_id not in self.bio_signs:
            self.bio_signs[body_id] = []

        scan_list: list[ScanResult] = self.bio_signs[body_id]
        new_scan.emplace_in_list(scan_list)
        self.frame_redraw()

    def register_codex_entry(self, event: dict):
        """
            Happens (among others?) when scanning a plant using the ship's Component Scanner
            { "timestamp":"2025-06-16T15:51:51Z",
                "event":"CodexEntry",
                "EntryID":2320406,
                "Name":"$Codex_Ent_Bacterial_04_Yttrium_Name;",
                "Name_Localised":"Bacterium Acies - Aquamarine",
                "SubCategory":"$Codex_SubCategory_Organic_Structures;",
                "SubCategory_Localised":"Organic structures",
                "Category":"$Codex_Category_Biology;",
                "Category_Localised":"Biological and Geological",
                "Region":"$Codex_RegionName_18;",
                "Region_Localised":"Inner Orion Spur",
                "System":"Stock 1 Sector AZ-P b6-1",
                "SystemAddress":2860314207817,
                "BodyID":5,
                "Latitude":-42.812225, "Longitude":-155.397385,
                "VoucherAmount":2500
            }
        """
        self.logger.info(f'Ship identified target: {event["Name_Localised"]}')
        # yes.... for some reason, the semicolon is part of the category name.
        # Possibly to match the $ marker in some template engine?
        if event['SubCategory'] != '$Codex_SubCategory_Organic_Structures;':
            return
        body_id: int = event['BodyID']
        genus, species = helpers.strip_variant(event['Name_Localised'])
        full_name: str = f'{genus} {species}'

        new_scan: ScanWithShipOrSuit = ScanWithShipOrSuit(full_name)

        if body_id not in self.bio_signs:
            self.bio_signs[body_id] = [new_scan]
            return

        new_scan.emplace_in_list(self.bio_signs[body_id])
        self.frame_redraw()

    def register_body_scan(self, event: dict) -> None:
        """
        Initial scan of a body:
        { "timestamp":"2025-06-18T16:26:36Z", "event":"Scan", "ScanType":"Detailed",
            "BodyName":"Stock 1 Sector AW-J b10-0 3", "BodyID":8, "Parents":[ {"Null":6}, {"Star":0} ],
            "StarSystem":"Stock 1 Sector AW-J b10-0", "SystemAddress":659680667241,
            "DistanceFromArrivalLS":1354.838891, "TidalLock":true,
            "TerraformState":"", "PlanetClass":"Icy body", "Atmosphere":"thin neon atmosphere", "AtmosphereType":"Neon",
            "AtmosphereComposition":[ { "Name":"Neon", "Percent":100.000000 } ], "Volcanism":"",
            "MassEM":0.160852, "Radius":4411225.000000, "SurfaceGravity":3.294706, "SurfaceTemperature":33.784779,
            "SurfacePressure":114.438019, "Landable":true,
            "Materials":[ { "Name":"sulphur", "Percent":21.918215 }, { "Name":"carbon", "Percent":18.430950 },
                { "Name":"iron", "Percent":15.442792 }, { "Name":"phosphorus", "Percent":11.799810 },
                { "Name":"nickel", "Percent":11.680281 }, { "Name":"chromium", "Percent":6.945137 },
                { "Name":"manganese", "Percent":6.377716 }, { "Name":"zinc", "Percent":4.196773 },
                { "Name":"cadmium", "Percent":1.199203 }, { "Name":"niobium", "Percent":1.055433 },
                { "Name":"ruthenium", "Percent":0.953691 } ],
            "Composition":{ "Ice":0.681768, "Rock":0.211446, "Metal":0.106786 },
            "SemiMajorAxis":396475595.235825, "Eccentricity":0.037682, "OrbitalInclination":-2.609289,
            "Periapsis":162.693849, "OrbitalPeriod":9178518.712521, "AscendingNode":-9.022772,
            "MeanAnomaly":300.328454, "RotationPeriod":12079028.376417, "AxialTilt":0.522809,
            "WasDiscovered":true, "WasMapped":false
        }
        """
        body_id: int = event["BodyID"]
        body: Body = Body(event)

        self.system_bodies[body_id] = body
        self.frame_redraw()

    def register_signal_count(self, event: dict) -> None:
        body_id: int = event["BodyID"]
        body_name: str = event["BodyName"]
        bio_count: int = helpers.get_bio_signal_count(event)
        if bio_count > 0:
            self.logger.warning(f'Found {bio_count} bio signs on {body_name}')
            # for some stupid reason this bio count may show up before the actual planet description
            if body_id not in self.system_bodies:
                self.system_bodies[body_id] = Body({"BodyName": body_name, "BodyID": body_id})

            if body_id not in self.bio_signs:
                self.bio_signs[body_id] = []
            ScanResult(bio_count).emplace_in_list(self.bio_signs[body_id])
            self.frame_redraw()
