#!/usr/bin/env python
# -*-coding:utf-8 -*

import logging
import json
import click
import jicson
import requests

from alkivi.logger import Logger
from configparser import ConfigParser


# Define the global logger
logger = Logger(min_log_level_to_mail=None,
                min_log_level_to_save=logging.DEBUG,
                min_log_level_to_print=logging.INFO,
                emails=['monitoring@alkivi.fr'])


def _get_config():
    config = ConfigParser()
    config.read('config')
    return config


@click.command()
@click.option('--debug', default=False, is_flag=True,
              help='Toggle Debug mode')
@click.option('--dry/--no-dry', default=True, is_flag=True,
              help='Toggle DRY mode')
def run(debug, dry):
    """General group."""
    if debug:
        logger.set_min_level_to_print(logging.DEBUG)
        logger.set_min_level_to_save(logging.DEBUG)
        logger.set_min_level_to_mail(None)
        logger.debug('debug activated')

    if dry:
        logger.set_min_level_to_save(logging.DEBUG)
        logger.set_min_level_to_mail(None)
        logger.info('DRY MODE activated')

    logger.debug('test')
    config = _get_config()

    numbers = config.sections()
    numbers_ok = []

    # parse all numbers
    logger.new_loop_logger()
    for number in numbers:
        logger.new_iteration(prefix=number)
        url = config[number].get('url')
        if not url:
            logger.warning('No url')
            continue

        response = requests.get(url)
        if response.status_code != 200:
            logger.warning('Weird return', response.text)

        ics_result = response.text
        result = jicson.fromText(ics_result)
        logger.debug('test', result)
        with open(f'{number}.json', 'w') as f:
            f.write(json.dumps(result))
            logger.info(f'{number}.json written')
            numbers_ok.append(number)
    logger.del_loop_logger()

    # Now write numbers data
    with open('numbers.json', 'w') as f:
        final_data = {'numbers': numbers_ok}
        f.write(json.dumps(final_data))
        logger.info('numbers.json written')


if __name__ == "__main__":
    try:
        run()
    except Exception as exception:
        logger.exception(exception)
