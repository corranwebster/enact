#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from .transition_manager import TransitionManager

_transition_manager = None

def get_transition_manager():
    """ Get the global transition manager. """
    global _transition_manager
    if _transition_manager is None:
        _transition_manager = TransitionManager()
    return _transition_manager

def set_transition_manager(transition_manager):
    """ Set the global transition manager.

    Raises
    ------
    ValueError - If an transition manager has already been set. This is to prevent
        the loss of registered listeners which may be being used by others.

    """
    global _transition_manager
    if _transition_manager is not None:
        raise ValueError('Event manager has already been set.')
    _transition_manager = transition_manager


