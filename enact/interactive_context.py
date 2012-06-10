#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from traits.api import HasTraits, Bool, Int, Str, Enum, Tuple, Set, Instance, Property

from .animated_context import AbstractAnimatedContext

MouseButton = Enum('left', 'right', 'middle')
ModifierKeys = Enum('shift', 'alt', 'control')


class AbstractMouseState(HasTraits):
    """ Class which tracks the mouse state
    
    Where state is not dynamically queryable, these variables should store the
    values from the most recent mouse event.
    """
    
    #: the position of the mouse in context-local coordinates
    position = Tuple(Int, Int)
    
    #: the x-coordinate of the mouse in context-local coordinates
    x = Property(Int, depends_on='position')
    
    #: the x-coordinate of the mouse in context-local coordinates
    y = Property(Int, depends_on='position')

    #: the mouse buttons which are down
    buttons = Set(MouseButton)
    
    #: whether the left mouse button is down
    left_button = Property(Bool, depends_on='buttons')

    #: whether the left mouse button is down
    right_button = Property(Bool, depends_on='buttons')

    #: whether the left mouse button is down
    middle_button = Property(Bool, depends_on='buttons')

    def _get_x(self):
        return self.position[0]

    def _get_y(self):
        return self.position[1]

    def _get_left_button(self):
        return 'left' in self.buttons

    def _get_right_button(self):
        return 'left' in self.buttons

    def _get_middle_button(self):
        return 'left' in self.buttons


class AbstractKeyboardState(HasTraits):
    
    #: the most recently emitted unicode character
    character = Str
    
    #: the most recently pressed keycode
    key_code = Str
    
    #: the modifier keys pressed, if any
    modifiers = Set(ModifierKeys)
    
    #: whether the shift key is down
    shift_down = Property(Bool)
    
    #: whether the shift key is down
    alt_down = Property(Bool)
    
    #: whether the shift key is down
    control_down = Property(Bool)

    def _get_shift_down(self):
        return 'shift' in self.modifiers

    def _get_alt_down(self):
        return 'shift' in self.modifiers

    def _get_control_down(self):
        return 'shift' in self.modifiers


class InteractiveContext(AbstractAnimatedContext):
    
    mouse = Instance(AbstractMouseState)

    keyboard = Instance(AbstractKeyboardState)



