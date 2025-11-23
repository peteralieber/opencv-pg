import logging
import cv2
import numpy as np
from imgui_bundle import imgui, hello_imgui, immapp

from opencv_pg.models.pipeline import Pipeline

LOG_FORMAT = "%(levelname)s:%(name)s:%(lineno)d:%(message)s"

DEF_WINDOW_SIZE = (800, 600)


class ImGuiPipelineWindow:
    """ImGui-based pipeline window"""
    
    def __init__(self, window, show_info_widget=False):
        self.window = window
        self.show_info_widget = show_info_widget
        self.output_image = None
    
    def render(self):
        """Render this window's content"""
        imgui.text(f"Window: {self.window.name}")
        imgui.separator()
        
        # Render image
        if self.output_image is not None:
            img_rgb = self._prepare_image_for_display(self.output_image)
            if img_rgb is not None:
                h, w = img_rgb.shape[:2]
                avail = imgui.get_content_region_avail()
                scale = min(avail.x / w, (avail.y - 100) / h, 1.0)
                display_w = int(w * scale)
                display_h = int(h * scale)
                
                try:
                    texture = hello_imgui.image_from_asset(img_rgb)
                    imgui.image(texture, imgui.ImVec2(display_w, display_h))
                except Exception as e:
                    imgui.text(f"Error displaying image: {e}")
        
        # Render transform parameters
        for transform in self.window.transforms:
            if transform.params:
                if imgui.collapsing_header(transform.__class__.__name__):
                    for param in transform.params:
                        imgui.text(f"{param.label}: {param._value or param.default}")
    
    def _prepare_image_for_display(self, img):
        """Convert OpenCV image to RGB format suitable for ImGui"""
        if img is None:
            return None
        
        # Handle different image types
        if img.dtype == np.uint16 or img.dtype == np.int32:
            img = (img / 256).astype(np.uint8)
        elif img.dtype == np.float32 or img.dtype == np.float64:
            img = (img * 255).astype(np.uint8)
        
        # Convert to RGB
        if len(img.shape) == 2:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img
        
        return img_rgb


class ImGuiPipelineApp:
    """ImGui application for displaying multiple pipeline windows"""
    
    def __init__(self, pipeline, show_info_widgets=False):
        self.pipeline = pipeline
        self.windows = []
        self.selected_window = 0
        
        # Create window objects for each pipeline window
        for window in pipeline.windows:
            win = ImGuiPipelineWindow(window, show_info_widgets)
            self.windows.append(win)
        
        # Run pipeline to get initial outputs
        pipeline.run_pipeline()
        
        # Update window outputs
        for i, window in enumerate(pipeline.windows):
            if window.last_out is not None:
                self.windows[i].output_image = window.last_out
    
    def gui(self):
        """Main GUI rendering"""
        # Window selector tabs
        if len(self.windows) > 1:
            for i, win in enumerate(self.windows):
                if imgui.radio_button(win.window.name, self.selected_window == i):
                    self.selected_window = i
                if i < len(self.windows) - 1:
                    imgui.same_line()
            imgui.separator()
        
        # Render selected window
        if 0 <= self.selected_window < len(self.windows):
            self.windows[self.selected_window].render()


def launch_pipeline(pipeline: Pipeline, show_info_widgets: bool = False,
                    log_level=logging.INFO):
    """Opens ImGui windows for each Window in the Pipeline

    Args:
        pipeline (Pipeline): Incoming Pipeline
        show_info_widgets (bool): If True, shows info_widgets on Transforms.
            Default is False.
        log_level (logging.LEVEL_NAME): Log level to use. Default is INFO.
    """
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
    
    app = ImGuiPipelineApp(pipeline, show_info_widgets)
    
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "OpenCV Pipeline"
    runner_params.app_window_params.window_geometry.size = DEF_WINDOW_SIZE
    runner_params.app_window_params.resizable = True
    
    runner_params.callbacks.show_gui = app.gui
    
    immapp.run(runner_params=runner_params)
