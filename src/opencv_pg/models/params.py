"""
Parameter classes for transforms - ImGui version

This replaces the Qt-based parameter system with a simpler callback-based approach
that works with ImGui's immediate mode paradigm.
"""
import copy
import logging
import numpy as np

log = logging.getLogger(__name__)


class Param:
    """Base class for all Transform Param's
    
    Args:
        default (any): The default value to use
        label (str, optional): The displayed label for this Param. Default is
            the class variable name will be used with `_` replaced by ` ` and
            each word capitalized.
        help_text (str, optional): Tooltip text to display. Default is ''.
    """
    
    def __init__(self, default=None, label=None, read_only=False, help_text="", fmt_str=None, **kwargs):
        super().__init__()
        self.label = label
        self._value = None
        self.default = default
        self._transform = None
        self.help_text = help_text
        self.read_only = read_only
        self.fmt_str = fmt_str  # Format string for displaying value
        # Ignore any other kwargs for compatibility
    
    def _store_value_and_start(self, value):
        """Store the changed value and run the pipeline
        
        Arguments:
            value (any): value to be stored in _value
        """
        if value is not None:
            self._value = value
            log.debug("%s: %s", self.__class__.__name__, value)
        if self._transform:
            self._transform.start_pipeline()


class IntSlider(Param):
    """Integer slider parameter"""
    
    def __init__(self, default, min_val, max_val, step=1, editable_range=False, **kwargs):
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.editable_range = editable_range


class FloatSlider(Param):
    """Float slider parameter"""
    
    def __init__(self, default, min_val, max_val, step=0.1, editable_range=False, **kwargs):
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.editable_range = editable_range


class IntPairSlider(Param):
    """Pair of integer sliders"""
    
    def __init__(self, default=None, min_val=0, max_val=100, step=1, editable_range=False, **kwargs):
        if default is None:
            default = (min_val, max_val)
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.editable_range = editable_range


class FloatPairSlider(Param):
    """Pair of float sliders"""
    
    def __init__(self, default=None, min_val=0.0, max_val=1.0, step=0.1, editable_range=False, **kwargs):
        if default is None:
            default = (min_val, max_val)
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.editable_range = editable_range


class Choice(Param):
    """Dropdown choice parameter"""
    
    def __init__(self, default=None, choices=None, options=None, options_map=None, **kwargs):
        super().__init__(default=default, **kwargs)
        # Support both 'choices' and 'options' for compatibility
        choice_list = choices or options or []
        self.choices = choice_list if isinstance(choice_list, list) else list(choice_list)
        self.options_map = options_map  # For mapping display names to values
    
    @property
    def options(self):
        """Alias for choices for backward compatibility"""
        return self.choices


class Bool(Param):
    """Boolean checkbox parameter"""
    
    def __init__(self, default=False, **kwargs):
        super().__init__(default=default, **kwargs)


class IntInput(Param):
    """Integer input parameter"""
    
    def __init__(self, default=0, min_val=None, max_val=None, step=1, unit_type=None, **kwargs):
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.unit_type = unit_type


class FloatInput(Param):
    """Float input parameter"""
    
    def __init__(self, default=0.0, min_val=None, max_val=None, decimals=2, step=0.1, unit_type=None, **kwargs):
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.decimals = decimals
        self.step = step
        self.unit_type = unit_type


class Color(Param):
    """Color picker parameter"""
    
    def __init__(self, default=(255, 255, 255), **kwargs):
        super().__init__(default=default, **kwargs)


class Text(Param):
    """Read-only text display parameter"""
    
    def __init__(self, default="", **kwargs):
        super().__init__(default=default, **kwargs)
        self.read_only = True


class Array2D(Param):
    """2D array parameter (kernel, structuring element, etc.)"""
    
    def __init__(self, default=None, use_anchor=True, use_struct=False, dims=2, editable_array=True, **kwargs):
        # Set default array if none provided
        if default is None:
            if dims == 1:
                default = np.array([1, 1, 1])
            else:
                default = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        super().__init__(default=default, **kwargs)
        self.use_anchor = use_anchor
        self.use_struct = use_struct  # Whether this is a structuring element
        self.dims = dims  # 1D or 2D array
        self.editable_array = editable_array  # Whether user can edit the array
        if default is not None:
            self._value = np.array(default)
        else:
            self._value = None


class Array1D(Param):
    """1D array parameter"""
    
    def __init__(self, default=None, use_anchor=False, dims=1, **kwargs):
        # Set default array if none provided
        if default is None:
            default = np.array([1, 1, 1])
        super().__init__(default=default, **kwargs)
        self.use_anchor = use_anchor
        self.dims = dims
        if default is not None:
            self._value = np.array(default)
        else:
            self._value = None


class KernelSize(Param):
    """Kernel size parameter (width, height)"""
    
    def __init__(self, default, min_val=1, max_val=100, **kwargs):
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val


class Point(Param):
    """Point parameter (x, y)"""
    
    def __init__(self, default=(0, 0), **kwargs):
        super().__init__(default=default, **kwargs)


class Dimensions2D(Param):
    """2D dimensions parameter (width, height)"""
    
    def __init__(self, default=(100, 100), min_val=1, max_val=1000, **kwargs):
        super().__init__(default=default, **kwargs)
        self.min_val = min_val
        self.max_val = max_val


# Aliases for backward compatibility with Qt version
ComboBox = Choice
CheckBox = Bool
ColorPicker = Color
ReadOnlyLabel = Text
SpinBox = IntInput
SliderPairParam = IntPairSlider
Array = Array2D
