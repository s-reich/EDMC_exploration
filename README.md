# EDMC Exploration Plugin

Plugin for the Elite Dangerous Market Connector to help in exobiology exploration, especially:

- list planets identified to contain bilogical signals (Full Spectrum Scanner)
- list genus types identified per planet (Planet Surface Scanner)
- list species names identified per planet (artemis suit and comp. scanner)

In each case, the potential Vista Genomics payout[^1] is shown as a possibility range (per planet and per genus),
calculated by species availability on planetary details.

[^1]: This includes the potential x5 bonus for first scan of a species; however, the only indicator available is the
      `wasMapped` flag, which is not exact: In theory, someone can land and scan stuff without mapping the planet or moon,
      or someone can map and land on a planet, but chose not to fully scan some or all bio signals &mdash; blame frontier for
      not adding the required flags to the journal logs.

Bonus:

- the plugin will also list stellar bodies worth a simple scan / mapping due to their rareness (terraformables, water worlds, etc.)

## Installation

Copy the full repository contents to your [EDMC](https://github.com/EDCD/EDMarketConnector) plugin folder.

Or better yet, simply clone this project in there (linux example):

```shell
cd ~/.local/share/EDMarketConnector/plugins
git clone https://github.com/s-reich/EDMC_exploration.git
```

EDMC should load the plugin on the next (re)start.

## Usage

Fully automated &mdash; the plugin is silent until you start scanning stuff, at which time it will add an output section to the EDMC window.
Current system information is stored persistently, so you can shut down EDMC and continue system exploration after some well-earned sleep.

(TODO: screenshot)

The plugin does not use external data sources or share your data anywhere.

## TODO - Incomplete

(see also github issues)

- The list of recognized biological genera is not complete yet. I'm adding them as I find them. Feel free to offer pull requests for `biological.py` if you want to help or share.
- Visual display is not very professional. I once stumbled across a planet with 10 (ten!) bio signals, and the list/grid would not fit my screen...
