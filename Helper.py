import argparse
import configparser
from pathlib import Path
import logging
# TODO: configparser -c/--config, logging package -l/--log, create package
parser = argparse.ArgumentParser(description="Wolf catch Sheeps game.")
parser.add_argument('-r', '--rounds', type=int, metavar='', help='Define number of rounds,'
                                                                 ' if not defined game simulated to last sheep.')
parser.add_argument('-s', '--sheep', type=int, metavar='',
                    help='Define number of sheeps, if not defined 10 are created.')
parser.add_argument('-w', '--wait', action='store_true', help="Pause after each round.")
parser.add_argument('-d', '--dir', type=Path, metavar='', help='Path to save diagnostic files,'
                                                               ' if not defined current directory.')
parser.add_argument('-c', '--config', type=Path, metavar='', help='Path to config file,'
                                                                  'if not defined are used default valus for PosLimit,'
                                                                  ' Sheep and Wolf speed = 1.0, 0.5.'
                                                                  ' Example structure of config file: example.ini')
parser.add_argument('-l', '--log', action='store_true', help='enabling this option create log file,'
                                                                        ' saved in -d defined option')
args = parser.parse_args()

c_parser = configparser.ConfigParser()
if args.config is not None:
    c_parser.read(str(args.config))
if args.log:
    if args.dir is not None:
        args.dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=str(args.dir) + '/chase.log', filemode='w', level=logging.DEBUG)
    else:
        logging.basicConfig(filename='chase.log', filemode='w', level=logging.DEBUG)
