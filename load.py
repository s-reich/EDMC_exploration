import sys

from typing import Any

from explorationhelper import ExplorationHelper

import logging
import os

from config import appname, config

# This could also be returned from plugin_start3()
plugin_name = os.path.basename(os.path.dirname(__file__))

# A Logger is used per 'found' plugin to make it easy to include the plugin's
# folder name in the logging output format.
# NB: plugin_name here *must* be the plugin's folder name as per the preceding
#     code, else the logger won't be properly set up.
logger: logging.Logger = logging.getLogger(f'{appname}.{plugin_name}')

this = sys.modules[__name__]
this.exploration_helper = ExplorationHelper(logger, config)

# If the Logger has handlers then it was already set up by the core code, else
# it needs setting up here.
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)


def plugin_start3(plugin_dir: str) -> str:
    """
    Load this plugin into EDMarketConnector
    """
    return "Exploration-Helper"


def plugin_app(parent):
    """
    Create a pair of TK widgets for the EDMC main window
    """
    return this.exploration_helper.frame_init(parent)


def journal_entry(
    cmdr: str, is_beta: bool, system: str, station: str, entry: dict[str, Any], state: dict[str, Any]
) -> None:
    event: str = entry['event']

    if event == 'FSDJump':
        this.exploration_helper.register_system(entry)
    elif event == 'SAASignalsFound':
        this.exploration_helper.register_detail_scan(entry)
    elif event == 'FSSBodySignals':
        # happens when the Full Spectrum Scanner finds something on a planet
        this.exploration_helper.register_signal_count(entry)
    elif event == 'Scan':
        # happens when the Full Spectrum Scanner identifies a planet
        this.exploration_helper.register_body_scan(entry)
    elif event == 'CodexEntry':
        # happens when the ship's comp-scanner identifies something
        this.exploration_helper.register_codex_entry(entry)
    elif event == 'ScanOrganic':
        # happens when Artemis suit scans a biological
        this.exploration_helper.register_organic(entry)

