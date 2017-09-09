import logging
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
APIDIR = ROOT / 'api'
DATADIR = ROOT / 'data'
IMAGESDIR = ROOT / 'images'
TEMPLATESDIR = ROOT / 'templates'
TOOLSDIR = ROOT / 'tools'

logging.basicConfig(format='[%(levelname)s] %(message)s')
logger = logging.getLogger('wxj')
logger.setLevel(logging.DEBUG)
