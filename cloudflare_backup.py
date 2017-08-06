#!/usr/bin/env python3

from cloudflaredns_backup import backup_dns
import logging
import logging.handlers
import random
import argparse
import os
import time

logger = logging.getLogger('cloudflare_backup')
logger.setLevel(logging.DEBUG)

# always write everything to the rotating log files
if not os.path.exists('logs'): os.mkdir('logs')
log_file_handler = logging.handlers.TimedRotatingFileHandler('logs/cloudflare_backup.log', when='M', interval=2)
log_file_handler.setFormatter( logging.Formatter('%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s') )
log_file_handler.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)

# also log to the console at a level determined by the --verbose flag
console_handler = logging.StreamHandler() # sys.stderr
console_handler.setLevel(logging.CRITICAL) # set later by set_log_level_from_verbose() in interactive sessions
console_handler.setFormatter( logging.Formatter('[%(levelname)s](%(name)s): %(message)s') )
logger.addHandler(console_handler)

logger.info("Starting...")

parser = argparse.ArgumentParser(
    description="get information via selenium",
)
parser.add_argument('command', nargs="?", default="count", help="command to execute", choices=['count', 'head', 'tail'])

parser.add_argument('-V', '--version', action="version", version="%(prog)s 2.0")
parser.add_argument('-v', '--verbose', action="count", help="verbose level... repeat up to three times.")


def set_log_level_from_verbose(args):

    if not args.verbose:
        console_handler.setLevel('ERROR')
    elif args.verbose == 1:
        console_handler.setLevel('WARNING')
    elif args.verbose == 2:
        console_handler.setLevel('INFO')
    elif args.verbose >= 3:
        console_handler.setLevel('DEBUG')
    else:
        logger.critical("UNEXPLAINED NEGATIVE COUNT!")
        

def get_config(filename):
    '''
    :param filename: where located configlist in format user:password:host:port or host:port
    :return: config list
    '''
    config = []
    with open(filename, encoding='utf-8') as config_file:
        for line in config_file:
            line = line.strip()
            if not line.startswith("#"):
                line = line.rstrip()
                if (len(line.split(":")) == 3):
                    email, token, output = line.split(":")
                    config.append({"email": email, "token": token, "output": output})
                else:
                    logger.error("unable to parse config in line \"{}\" start parse next line...".format(line))
                    print("Unable to parse config", line)
                # random.shuffle(config)
    logger.info("loading {} config".format(len(config)))
    return config


if __name__ == '__main__':
    now = time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime())
    backup_folder = "/home/backup/cloudflare/"
    args = parser.parse_args()
    set_log_level_from_verbose(args)
    if not os.path.exists(backup_folder):
        os.mkdir(backup_folder)
        os.chmod(backup_folder, 0o700)
    cf = get_config("conf/cf_conf.txt")
    args.zones = ''
    args.ns = ''
    for config in cf:
        archive_folder = backup_folder + now + "_" + config['output']
        backup_dns(config['email'], config['token'], args.zones, archive_folder, args.ns)


