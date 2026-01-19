import copy
import logging

import numpy as np

log = logging.getLogger(__name__)


class Window:
    """Window containing a sequence of transforms
    
    Note: This has been updated to remove Qt dependencies. The image_updated
    signal has been replaced with a callback mechanism.
    """
    
    counter = 1

    def __init__(self, transforms, name: str = ""):
        self.transforms = transforms
        self.index = None
        self.pipeline = None
        self.last_out = None
        self.image_updated_callback = None  # Callback function for image updates

        # Use a suitable name if none is provided
        if not name:
            self.name = f"Step {self.counter}"
            Window.counter += 1
        else:
            self.name = name

    def set_image_updated_callback(self, callback):
        """Set a callback to be called when image is updated"""
        self.image_updated_callback = callback

    def start_pipeline(self, transform_index: int = 0):
        """Runs pipeline from current window, starting on `transform_index`"""
        log.debug(
            "Starting Pipeline from Window %s, transform index: %s",
            self.index,
            transform_index,
        )
        self.pipeline.run_pipeline(self.index, transform_index)

    def draw(self, img_in, extra_in, transform_index=0):
        """Call _draw on each child transform in sequence and return final output"""
        if transform_index < 0:
            raise ValueError(f"Transform index must be >= 0. Got {transform_index}")

        if img_in is not None and len(img_in.shape) > 0:
            self.last_in = np.copy(img_in)
            img_out = np.copy(img_in)
            self.extra_in = copy.deepcopy(extra_in)
            extra_out = copy.deepcopy(extra_in)
        else:
            img_out = None
            extra_out = None

        # Run the transforms
        for transform in self.transforms[transform_index:]:
            img_out, extra_out = transform._draw(img_out, extra_out)

        self.last_out = np.copy(img_out)
        
        # Call callback if set
        if self.image_updated_callback:
            self.image_updated_callback()
        
        return img_out, extra_out
