#!/usr/bin/env python3

"""
For maintaining information on Drosophila bottles / vials, with a combination of
PostreSQL and a label printer.
"""

from __future__ import print_function

import time
from subprocess import Popen
from enum import Enum

import qrcode
import reportlab


# TODO options to support
class Actions(Enum):
    # flipping a bottle (+ vial?) (starting another bottle w/ same progeny)
    # to be further differentiated by whether source container is ecclosing?
    FLIP = 0
    # start a new bottle (from fixed number progeny of another bottle)
    SEED = 1
    # crosses (2 QR codes at once? succession? other keys / buttons?)
    CROSS = 2
    # separating eclosed flies to get them to a certain age
    AGE = 3
    # starving flies to incur all the modulation that comes with starving,
    # including higher activity
    STARVE = 4
    # throw out bottle / vial (maybe won't want to use this?)
    TOSS = 5
    # cancel label (remove from database.)
    VOID = 6

# want to do it this way?
#class Container():


# TODO callback or polling to monitor button state?
# TODO gui / manual entry alternative to headless button + indicator based
# system for switching between modes
# TODO wake button?

def check_for_qr_code():
    """
    """
    return None

def get_container_info(code):
    """
    """
    return None

def remove_from_database(container_info):
    """
    """
    # TODO if container info isn't going to have the unique identifier, then
    # refactor?
    identifier = container_info['id']
    # TODO
    raise NotImplementedError

def create_id(container_info):
    """Creates a unique identifier for container, and pairs it with info in db.
    """
    # TODO get next ID (or use probabilistic IDs?) from database
    identifier = None
    
    # TODO add (ID, container_info) to database

    # TODO maybe just add something like an 'id' key to the container_info dict?
    return identifier

def get_new_container_info(mode, source_container_info, *second_source_info):
    """
    """
    if mode == Actions.FLIP:
        raise NotImplementedError

    elif mode == Actions.SEED:
        raise NotImplementedError

    elif mode == Actions.CROSS:
        raise NotImplementedError

    elif mode == Actions.AGE:
        raise NotImplementedError

    elif mode == Actions.STARVE:
        raise NotImplementedError

    elif mode == Actions.TOSS:
        raise NotImplementedError

    elif mode == Actions.VOID:
        remove_from_database(source_container_info)
        return None

def qr_code(container_info):
    """Generates a QR code for a new fly container, with info as in argument.
    """
    identifier = create_id(container_info)
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
    mode = Actions.STARVE
    while True:
        # TODO
        # - have another process to poll feed for QR code?
        # - intermediate motion detector that initiates polling (if less
        #   resource intensive?)?
        # - just make it button / keypress driven?
        code = check_for_qr_code()
        if not code is None:
            fly_container_info = get_fly_information(code)

            if mode == Actions.CROSS:
                # TODO would need to refactor s.t. this only returns if
                # successful, or poll again here. not sure i want to enforce
                # scanning male container second, but not sure what else to do.
                male_code = check_for_qr_code()
                male_container_info = get_fly_information(male_code)
                new_container_info = get_new_container_info(mode,
                                                            fly_container_info,
                                                            male_container_info)

            else:
                new_container_info = get_new_container_info(mode,
                                                            fly_container_info)
                print_label(new_container_info)

        time.sleep(0.3)
        

if __name__ == '__main__':
    main()

