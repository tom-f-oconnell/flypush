#!/usr/bin/env python3

"""
For maintaining information on Drosophila bottles / vials, with a combination of
PostreSQL and a label printer.
"""

from __future__ import print_function

import time
import datetime
from subprocess import Popen
from enum import Enum

import pytz
import psycopg2
import qrcode
import reportlab


# TODO options to support
class Actions(Enum):
    # flipping a bottle (+ vial?) (starting another bottle w/ same progeny)
    # to be further differentiated by whether source container is ecclosing?
    FLIP = 0
    CLEAR = 1
    # start a new bottle (from fixed number progeny of another bottle)
    SEED = 2
    # crosses (2 QR codes at once? succession? other keys / buttons?)
    CROSS = 3
    # separating eclosed flies to get them to a certain age
    AGE = 4
    # starving flies to incur all the modulation that comes with starving,
    # including higher activity
    STARVE = 5
    # throw out bottle / vial (maybe won't want to use this?)
    TOSS = 6
    # cancel label (remove from database.)
    VOID = 7

# want to do it this way?
#class Container():

# TODO class to deal with the state of the database without having to either
# pass a cursor around or use a global variable? some idiom?

# TODO callback or polling to monitor button state?
# TODO gui / manual entry alternative to headless button + indicator based
# system for switching between actions
# TODO wake button?

def check_for_qr_code():
    """
    Returns
    """
    # TODO what type should this be?
    code = None
    raise NotImplementedError
    return code


def qr_code_to_info(code):
    """
    Args:

    Returns
    """
    info = dict()
    raise NotImplementedError
    return info


def qr_code_to_id(code):
    """
    Args:

    Returns
    """
    identifier = None
    raise NotImplementedError
    return identifier


def get_container_info(pg_cursor, identifier):
    """
    Args:

    Returns
    """
    
    return None


# TODO make local db if remote is unavailable? + warn + sync up later
def remove_from_database(pg_cursor, container_info):
    """
    """
    # TODO if container info isn't going to have the unique identifier, then
    # refactor?
    identifier = container_info['id']
    # TODO
    raise NotImplementedError


def mark_tossed_in_database(pg_cursor, container_info):
    """
    """
    raise NotImplementedError


def create_id(pg_cursor):
    """Creates a unique identifier for container, and pairs it with info in db.
    """
    raise NotImplementedError
    # TODO get next ID (or use probabilistic IDs?) from database
    identifier = None
    return identifier


def update_database(pg_cursor, info):
    """
    Args:
        info (dict): 

    Returns a new unique identifier for the vial described by the metadata in
    info.
    """
    identifier = create_id(pg_cursor)
    # TODO maybe add all the timestamps here, which timestamp conditional on the
    # action (stored in info or passed separately)? might tie me more to one
    # database backend though...
    raise NotImplementedError
    return identifier


def get_new_container_info(action, pg_cursor, source_container_info, 
                           *second_source_info):
    """Returns metadata dict for fly container, given action. Updates database.

    Args:

    Returns
    """
    identifier = source_container_info['id']
    if action == Actions.TOSS:
        mark_tossed_in_database(pg_cursor, identifier)
        return None

    elif action == Actions.VOID:
        remove_from_database(pg_cursor, identifier)
        return None

    info = dict()
    # TODO helper to assert key is not already in dict?
    if action == Actions.SEED:
        # TODO *could* use postgres times upon insert, but i might rather have
        # my data defined outside of the database, to switch backends
        info['parents_added_at'] = datetime.utcnow()
        # TODO another field only populated when everyone is the same genotype
        # (and leave these unpopulated in that case?)
        info['male_parent_ids'] = source_container_info['id']
        info['female_parent_ids'] = source_container_info['id']
        # TODO make defaults (maybe user specific?)
        info['num_male_parents'] = 20
        info['num_female_parents'] = 10
        raise NotImplementedError

    elif action == Actions.FLIP:
        info['cleared_at'] = 
        # TODO make defaults
        info['food_protocol'] = source_container_info['food_protocol']
        # bottle or vial (way to encode efficiently?)
        info['container_type'] = source_container_info['container_type']
        raise NotImplementedError

    elif action == Actions.CLEAR:
        info['parents_removed_at']
        raise NotImplementedError
        return None

    elif action == Actions.CROSS:
        # TODO copy from seed
        raise NotImplementedError

    # TODO add a mechanism for defining arbitrary extra actions w/o editing
    # code? for things like rearing? (or just add that?)
    elif action == Actions.AGE:
        # TODO make default
        info['aging_protocol']
        raise NotImplementedError

    elif action == Actions.STARVE:
        raise NotImplementedError
        info['started_starvation_at']
        # TODO make default
        info['starvation_protocol']

    else:
        raise NotImplementedError

    identifier = update_database(pg_cursor, info)
    info['id'] = identifier
    return info


def qr_code(container_info):
    """Generates a QR code for a new fly container, with identifier and other
    information in dictionary argument encoded.
    """
    # TODO encode identifier + container_info into QR code (or at least the
    # former)
    code = None
    raise NotImplementedError
    return code


def print_label(container_info):
    """
    """
    if container_info is None:
        return
    code = qr_code(container_info)
    # TODO either save qr_code in a printable format (e.g. pdf via reportlab)
    # or get it into such a format internally, and then pipe it to lpr
    raise NotImplementedError


def main():
    """
    """
    action = Actions.STARVE

    # TODO create db + tables if not there?

    # TODO passwordless (+userless?) authentication?
    conn = psycopg2.connect(database='flypush', user='flypush', host='atlas', 
        password='flypush')
    conn.autocommit = True
    pg_cursor = conn.cursor()

    '''
    try:
        # TODO read create_tables sql file
        pg_cursor.execute()
    except
    '''

    while True:
        # TODO
        # - have another process to poll feed for QR code?
        # - intermediate motion detector that initiates polling (if less
        #   resource intensive?)?
        # - just make it button / keypress driven?
        code = check_for_qr_code()
        if not code is None:
            fly_container_info = get_container_info(pg_cursor, code)

            if action == Actions.CROSS:
                # TODO would need to refactor s.t. this only returns if
                # successful, or poll again here. not sure i want to enforce
                # scanning male container second, but not sure what else to do.
                male_code = check_for_qr_code()
                male_container_info = get_container_info(pg_cursor, male_code)
                new_container_info = get_new_container_info(action, pg_cursor,
                                                            fly_container_info,
                                                            male_container_info)

            else:
                new_container_info = get_new_container_info(action, pg_cursor,
                                                            fly_container_info)
                print_label(new_container_info)

        time.sleep(0.3)
        

if __name__ == '__main__':
    main()

