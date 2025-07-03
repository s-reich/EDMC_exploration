# All filter criteria taken from https://elite-dangerous.fandom.com/wiki/Exobiology_Sample_Values_and_Details


class Biological:
    def __init__(self, category: str, name: str, net_worth_millions: float, filters: list = ()):
        self.category: str = category
        self.name: str = name
        self.net_worth: float = net_worth_millions
        self.filters: list = filters

    def can_grow_on(self, planet: dict) -> bool:
        for f in self.filters:
            if not f.accepts(planet):
                return False
        return True

    def display_name(self) -> str:
        return f'{self.category} {self.name}'


class Filter:
    def accepts(self, planet: dict) -> bool:
        """ Planet entry is a "Scan" result:
        {
            "timestamp":"2025-06-16T16:28:29Z",
            "event":"Scan",
            "ScanType":"Detailed",
            "BodyName":"Stock 1 Sector AZ-P b6-2 A 2",
            "BodyID":11,
            "Parents":[ {"Star":1}, {"Null":0} ],
            "StarSystem":"Stock 1 Sector AZ-P b6-2"
             "SystemAddress":5059337463369,
             "DistanceFromArrivalLS":107.543725,
             "TidalLock":true,
             "TerraformState":"",
             "PlanetClass":"Icy body",
             "Atmosphere":"thick argon rich atmosphere",
             "AtmosphereType":"ArgonRich",
             "AtmosphereComposition":[
                { "Name":"Nitrogen", "Percent":96.068344 },
                { "Name":"Argon", "Percent":3.919174 }
                ],
             "Volcanism":"major water geysers volcanism",
             "MassEM":2.671570,
             "Radius":10387594.000000,
             "SurfaceGravity":9.868385,
             "SurfaceTemperature":173.788452,
             "SurfacePressure":104048696.000000,
             "Landable":false,
             "Composition":{ "Ice":0.686562, "Rock":0.210540, "Metal":0.102898 },
             "SemiMajorAxis":32240716814.994812,
             "Eccentricity":0.000003,
             "OrbitalInclination":-0.005551,
             "Periapsis":23.688319,
             "OrbitalPeriod":6741344.273090,
             "AscendingNode":-21.632036,
             "MeanAnomaly":221.932979,
             "RotationPeriod":6750124.822942,
             "AxialTilt":0.294516,
             "WasDiscovered":true,
             "WasMapped":false
         }
        """
        pass


class Atmosphere(Filter):
    def __init__(self, gas: str):
        self.required: str = gas

    def accepts(self, planet: dict) -> bool:
        if 'AtmosphereComposition' not in planet:
            return True
        return self.required in [
            x["Name"]
            for x in planet["AtmosphereComposition"]
        ]


class Volcanism(Filter):
    def __init__(self, volcanism: str):
        self.required = volcanism

    def accepts(self, planet: dict) -> bool:
        if 'Volcanism' not in planet:
            return True
        return (
                self.required in planet["Volcanism"]
                or
                self.required == "None" and planet["Volcanism"] == ""
        )


class Planet(Filter):
    def __init__(self, planet_type: str):
        self.required: str = planet_type

    def accepts(self, planet: dict) -> bool:
        return (
                self.required in planet['PlanetClass']
                if 'PlanetClass' in planet
                else True
        )


class Temperature(Filter):
    def __init__(self, min_temp: int, max_temp: int):
        self.min: int = min_temp
        self.max: int = max_temp

    def accepts(self, planet: dict) -> bool:
        return (
                self.min <= planet['SurfaceTemperature'] < self.max
                if 'SurfaceTemperature' in planet
                else True
        )


class Gravity(Filter):
    def __init__(self, min_grav: float, max_grav: float):
        self.min: float = min_grav
        self.max: float = max_grav

    def accepts(self, planet: dict) -> bool:
        return (
                self.min <= planet['SurfaceGravity'] < self.max
                if 'SurfaceGravity' in planet
                else True
        )


class Distance(Filter):
    def __init__(self, min_distance: float, max_distance: float):
        self.min: float = min_distance
        self.max: float = max_distance

    def accepts(self, planet: dict) -> bool:
        # TODO: for anything NOT orbiting a sun (moons, twin planets, ...)
        #       Periapsis is quite possibly the wrong thing to check; instead, a recursive
        #       search over the body`s parents would have to be done...
        return (
            self.min <= planet['Periapsis'] < self.max
            if 'Periapsis' in planet
            else True
        )


class Aleoida(Biological):
    def __init__(self, name: str, net_worth_millions: float, filters: list = ()):
        super().__init__('Aleoida', name, net_worth_millions, filters)
        self.planet1: Filter = Planet('Rocky')
        self.planet2: Filter = Planet('High metal content')
        self.gravity: Filter = Gravity(0, 0.27)

    def can_grow_on(self, planet: dict) -> bool:
        if not self.gravity.accepts(planet):
            return False
        if not self.planet1.accepts(planet) and not self.planet2.accepts(planet):
            return False

        return super().can_grow_on(planet)


class Clypeus(Biological):
    """
    Has a colony distance of 150m.
    They are only found on Rocky or High Metal Content worlds that have
    a mean temperature superior to 190K,
    water or carbon dioxide atmosphere,
    and a maximum gravity of 0.27.
    """
    def __init__(self, name: str, net_worth_millions: float, filters: list = ()):
        super().__init__('Clypeus', name, net_worth_millions, filters)
        self.planet1: Filter = Planet('Rocky')
        self.planet2: Filter = Planet('High metal content')
        self.temperature: Filter = Temperature(190,999)
        self.gravity: Filter = Gravity(0, 0.27)
        self.atmosphere1: Filter = Atmosphere("Water")
        self.atmosphere2: Filter = Atmosphere("CarbonDioxide")

    def can_grow_on(self, planet: dict) -> bool:
        if not self.gravity.accepts(planet):
            return False
        if not self.temperature.accepts(planet):
            return False
        if not self.planet1.accepts(planet) and not self.planet2.accepts(planet):
            return False
        if not self.atmosphere1.accepts(planet) and not self.atmosphere2.accepts(planet):
            return False

        return super().can_grow_on(planet)


all_bios: list[Biological] = [
    Aleoida('Arcus', 7.3, [Atmosphere('CarbonDioxide'), Temperature(175, 180)]),
    Aleoida('Coronamus', 6.3, [Atmosphere('CarbonDioxide'), Temperature(180, 190)]),
    Aleoida('Gravis', 12.9, [Atmosphere('CarbonDioxide'), Temperature(190, 195)]),
    Aleoida('Laminiae', 3.4, [Atmosphere('Ammonia')]),
    Aleoida('Spica', 3.4, [Atmosphere('Ammonia')]),

    Biological('Bacterium', 'Nebulus', 9.1, [Atmosphere('Helium'), Volcanism('None') ]),
    Biological('Bacterium', 'Acies', 1.0, [Atmosphere('Neon'), Volcanism('None')]),
    Biological('Bacterium', 'Acies', 1.0, [Atmosphere('Neon'), Volcanism('nitrogen')]),
    Biological('Bacterium', 'Omentum', 4.6, [Atmosphere('Neon'), Volcanism('nitrogen')]),
    Biological('Bacterium', 'Omentum', 4.6, [Atmosphere('Neon'), Volcanism('ammonia')]),
    Biological('Bacterium', 'Scopulum', 8.6, [Atmosphere('Neon'), Volcanism('carbon')]),
    Biological('Bacterium', 'Scopulum', 8.6, [Atmosphere('Neon'), Volcanism('methane')]),
    Biological('Bacterium', 'Verrata', 3.9, [Atmosphere('Neon'), Volcanism('water')]),
    Biological('Bacterium', 'Bullaris', 1.1, [Atmosphere('Methane'), Volcanism('None')]),
    Biological('Bacterium', 'Vesicula', 1.0, [Atmosphere('Argon'), Volcanism('None')]),
    Biological('Bacterium', 'Informem', 8.4, [Atmosphere('Nitrogen'), Volcanism('None')]),
    Biological('Bacterium', 'Volu', 7.7, [Atmosphere('Oxygen'), Volcanism('None')]),
    Biological('Bacterium', 'Alcyoneum', 1.7, [Atmosphere('Ammonia'), Volcanism('None')]),
    Biological('Bacterium', 'Aurasus', 1.0, [Atmosphere('CarbonDioxide'), Volcanism('None')]),
    Biological('Bacterium', 'Cerbrus', 1.7, [Atmosphere('Water'), Volcanism('None')]),
    Biological('Bacterium', 'Cerbrus', 1.7, [Atmosphere('CarbonDioxide'), Volcanism('None')]),
    Biological('Bacterium', 'Tela', 1.9, [Volcanism('None')]),
    Biological('Bacterium', 'Tela', 1.9, [Volcanism('helium')]),
    Biological('Bacterium', 'Tela', 1.9, [Volcanism('iron')]),
    Biological('Bacterium', 'Tela', 1.9, [Volcanism('silicate')]),
    Biological('Bacterium', 'Tela', 1.9, [Volcanism('methane')]),

    Biological('Cactoida', 'Cortexum', 3.7, [Atmosphere('CarbonDioxide')]),
    Biological('Cactoida', 'Lapis', 2.5, [Atmosphere('Ammonia')]),
    Biological('Cactoida', 'Peperatis', 2.5, [Atmosphere('Ammonia')]),
    Biological('Cactoida', 'Pullulanta', 3.7, [Atmosphere('CarbonDioxide'), Temperature(180, 195)]),
    Biological('Cactoida', 'Vermis', 16.2, [Atmosphere('Water')]),

    Clypeus('Lacrimam', 8.4),
    Clypeus('Margaritus', 11.9),
    Clypeus('Speculumi', 16.2, [Distance(2500,999999)]),

    Biological('Concha', 'Aureolas', 7.8, [Atmosphere('Ammonia')]),
    Biological('Concha', 'Biconcavis', 16.8, [Atmosphere('Nitrogen')]),
    Biological('Concha', 'Labiata', 2.4, [Atmosphere('CarbonDioxide')]),
    Biological('Concha', 'Renibus', 4.6, [Atmosphere('Water'), Temperature(180, 195)]),



    Biological('Fonticulua', 'Campestris', 1.0, [Atmosphere('Argon')]),
    Biological('Fonticulua', 'Digitos', 1.8, [Atmosphere('Methane')]),
    Biological('Fonticulua', 'Fluctus', 16.8, [Atmosphere('Oxygen')]),
    Biological('Fonticulua', 'Lapida', 3.1, [Atmosphere('Nitrogen')]),
    Biological('Fonticulua', 'Segmentatus', 19.0, [Atmosphere('Neon')]),
    Biological('Fonticulua', 'Upupam', 5.7, [Atmosphere('Argon')]),

    Biological('Frutexa', 'Acus', 7.8, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(0, 195)]),
    Biological('Frutexa', 'Collum', 1.6, [Planet('Rocky'), Atmosphere('SulphurDioxide')]),
    Biological('Frutexa', 'Fera', 1.6, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(0, 195)]),
    Biological('Frutexa', 'Flabellum', 1.8, [Planet('Rocky'), Atmosphere('Ammonia')]),
    Biological('Frutexa', 'Flammasis', 10.3, [Planet('Rocky'), Atmosphere('Ammonia')]),
    Biological('Frutexa', 'Metallicum', 1.6, [Planet('High metal content'), Atmosphere('Ammonia'), Temperature(0, 195)]),
    Biological('Frutexa', 'Metallicum', 1.6, [Planet('High metal content'), Atmosphere('CarbonDioxide'), Temperature(0, 195)]),
    Biological('Frutexa', 'Sponsae', 6.0, [Planet('Rocky'), Atmosphere('Water')]),

    Biological('Fungoida', 'Bullarum', 3.7, [Atmosphere('Argon')]),
    Biological('Fungoida', 'Gelata', 3.3, [Atmosphere('CarbonDioxide'), Temperature(180, 195)]),
    Biological('Fungoida', 'Gelata', 3.3, [Atmosphere('Water')]),
    Biological('Fungoida', 'Setisis', 1.7, [Atmosphere('Ammonia')]),
    Biological('Fungoida', 'Setisis', 1.7, [Atmosphere('Methane')]),
    Biological('Fungoida', 'Stabitis', 2.7, [Atmosphere('CarbonDioxide'), Temperature(180, 195)]),
    Biological('Fungoida', 'Stabitis', 2.7, [Atmosphere('Water')]),

    Biological('Osseus', 'Cornibus', 1.5, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(180, 195)]),
    Biological('Osseus', 'Cornibus', 1.5, [Planet('High metal content'), Atmosphere('CarbonDioxide'), Temperature(180, 195)]),
    Biological('Osseus', 'Discus', 12.9, [Planet('Rocky'), Atmosphere('Water')]),
    Biological('Osseus', 'Discus', 12.9, [Planet('High metal content'), Atmosphere('Water')]),
    Biological('Osseus', 'Fractus', 4.0, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(180, 195)]),
    Biological('Osseus', 'Fractus', 4.0, [Planet('High metal content'), Atmosphere('CarbonDioxide'), Temperature(180, 190)]),
    Biological('Osseus', 'Pellebantus', 9.7, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(190, 195)]),
    Biological('Osseus', 'Pellebantus', 9.7, [Planet('High metal content'), Atmosphere('CarbonDioxide'), Temperature(190, 195)]),
    Biological('Osseus', 'Pumice', 3.2, [Planet('Rocky'), Atmosphere('Methane')]),
    Biological('Osseus', 'Pumice', 3.2, [Planet('Rocky'), Atmosphere('Argon')]),
    Biological('Osseus', 'Pumice', 3.2, [Planet('Rocky'), Atmosphere('Nitrogen')]),
    Biological('Osseus', 'Pumice', 3.2, [Planet('Ice'), Atmosphere('Methane')]),
    Biological('Osseus', 'Pumice', 3.2, [Planet('Ice'), Atmosphere('Argon')]),
    Biological('Osseus', 'Pumice', 3.2, [Planet('Ice'), Atmosphere('Nitrogen')]),
    Biological('Osseus', 'Spiralis', 2.4, [Planet('Rocky'), Atmosphere('Ammonia')]),
    Biological('Osseus', 'Spiralis', 2.5, [Planet('High metal content'), Atmosphere('Ammonia')]),

    Biological('Recepta', 'Conditivus', 14.3, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Gravity(0, 0.27)]),
    Biological('Recepta', 'Conditivus', 14.3, [Planet('Icy'), Atmosphere('CarbonDioxide'), Gravity(0, 0.27)]),
    Biological('Recepta', 'Deltahedronix', 16.2, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Gravity(0, 0.27)]),
    Biological('Recepta', 'Deltahedronix', 16.2, [Planet('High metal content'), Atmosphere('CarbonDioxide'), Gravity(0, 0.27)]),
    Biological('Recepta', 'Umbrux', 12.9, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Gravity(0, 0.27)]),
    Biological('Recepta', 'Umbrux', 12.9, [Planet('High metal content'), Atmosphere('CarbonDioxide'), Gravity(0, 0.27)]),
    Biological('Recepta', 'Umbrux', 14.3, [Planet('Icy'), Atmosphere('CarbonDioxide'), Gravity(0, 0.27)]),

    Biological('Stratum', 'Araneamus', 2.4, [Planet('Rocky'), Atmosphere('SulphurDioxide'), Temperature(165, 999)]),
    Biological('Stratum', 'Cucumisis', 16.2, [Planet('Rocky'), Atmosphere('SulphurDioxide'), Temperature(190, 999)]),
    Biological('Stratum', 'Cucumisis', 16.2, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(190, 999)]),
    Biological('Stratum', 'Excutitus', 2.4, [Planet('Rocky'), Atmosphere('SulphurDioxide'), Temperature(165, 190)]),
    Biological('Stratum', 'Excutitus', 2.4, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(165, 190)]),
    Biological('Stratum', 'Frigus', 2.4, [Planet('Rocky'), Atmosphere('SulphurDioxide'), Temperature(190, 999)]),
    Biological('Stratum', 'Frigus', 2.4, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(190, 999)]),
    Biological('Stratum', 'Laminamus', 2.8, [Planet('Rocky'), Atmosphere('Ammonia'), Temperature(165, 999)]),
    Biological('Stratum', 'Limaxus', 1.4, [Planet('Rocky'), Atmosphere('SulphurDioxide'), Temperature(165, 999)]),
    Biological('Stratum', 'Limaxus', 1.4, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(165, 190)]),
    Biological('Stratum', 'Limaxus', 1.4, [Planet('Rocky'), Atmosphere('SulphurDioxide'), Temperature(165, 999)]),
    Biological('Stratum', 'Paleas', 1.4, [Planet('Rocky'), Atmosphere('Ammonia'), Temperature(165, 999)]),
    Biological('Stratum', 'Paleas', 1.4, [Planet('Rocky'), Atmosphere('Water')]),
    Biological('Stratum', 'Tectonicas', 19.0, [Planet('High metal content'), Temperature(165, 999)]),

    Biological('Tubus', 'Cavas', 11.9, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(160, 190)]),
    Biological('Tubus', 'Compagibus', 7.8, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(160, 190)]),
    Biological('Tubus', 'Conifer', 2.4, [Planet('Rocky'), Atmosphere('CarbonDioxide'), Temperature(160, 190)]),
    Biological('Tubus', 'Rosarium', 2.6, [Planet('Rocky'), Atmosphere('Ammonia'), Temperature(160, 999)]),
    Biological('Tubus', 'Sororibus', 11.9, [Planet('High metal content'), Atmosphere('Ammonia'), Temperature(160, 190)]),
    Biological('Tubus', 'Sororibus', 11.9, [Planet('High metal content'), Atmosphere('CarbonDioxide'), Temperature(160, 190)]),

    Biological('Tussock', 'Albata', 3.3, [Atmosphere('CarbonDioxide'), Temperature(175, 180)]),
    Biological('Tussock', 'Capillum', 7.0, [Atmosphere('Methane')]),
    Biological('Tussock', 'Capillum', 7.0, [Atmosphere('Argon')]),
    Biological('Tussock', 'Caputus', 3.5, [Atmosphere('CarbonDioxide'), Temperature(180, 190)]),
    Biological('Tussock', 'Catena', 1.8, [Atmosphere('Ammonia')]),
    Biological('Tussock', 'Cultro', 1.8, [Atmosphere('Ammonia')]),
    Biological('Tussock', 'Divisa', 1.8, [Atmosphere('Ammonia')]),
    Biological('Tussock', 'Ignis', 1.8, [Atmosphere('CarbonDioxide'), Temperature(160, 170)]),
    Biological('Tussock', 'Pennata', 5.9, [Atmosphere('CarbonDioxide'), Temperature(145, 155)]),
    Biological('Tussock', 'Pennatis', 1.0, [Atmosphere('CarbonDioxide'), Temperature(0, 195)]),
    Biological('Tussock', 'Propagito', 1.0, [Atmosphere('CarbonDioxide'), Temperature(0, 195)]),
    Biological('Tussock', 'Serrati', 4.5, [Atmosphere('CarbonDioxide'), Temperature(170, 175)]),
    Biological('Tussock', 'Stigmasis', 19.0, [Atmosphere('SulphurDioxide')]),
    Biological('Tussock', 'Triticum', 7.8, [Atmosphere('CarbonDioxide'), Temperature(190, 195)]),
    Biological('Tussock', 'Ventusa', 3.3, [Atmosphere('CarbonDioxide'), Temperature(155, 160)]),
    Biological('Tussock', 'Virgam', 14.3, [Atmosphere('Water')]),

]


def get_bio_for_species(name: str) -> Biological:
    for b in all_bios:
        if b.display_name() == name:
            return b
    return Biological(name, '?', 999.0)