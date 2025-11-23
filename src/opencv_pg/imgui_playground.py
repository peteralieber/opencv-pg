"""
ImGui-based Playground for OpenCV functions

This replaces the Qt6-based playground with an immediate mode GUI using imgui_bundle.
"""
import logging
from pathlib import Path
import numpy as np
import cv2
from imgui_bundle import imgui, hello_imgui, immapp
import webbrowser

from opencv_pg.models.transform_windows import collect_builtin_transforms, get_transform_window
from opencv_pg.models.pipeline import Pipeline
from opencv_pg.docs import doc_writer

log = logging.getLogger(__name__)


class ImGuiPlayground:
    """ImGui-based OpenCV Playground application"""
    
    def __init__(self, img_path, no_docs=False, disable_info_widgets=False):
        self.img_path = str(img_path)
        self.show_docs = not no_docs
        self.show_info_widgets = not disable_info_widgets
        
        # Get list of available transforms
        self.transforms = collect_builtin_transforms()
        self.transform_names = [t.__name__ for t in self.transforms]
        self.selected_transform_idx = 0
        
        # Current pipeline and window
        self.current_window = None
        self.current_pipeline = None
        self.output_image = None
        
        # Initialize with first transform
        if self.transforms:
            self._load_transform(0)
        
        # Documentation
        doc_writer._create_rendered_docs()
    
    def _load_transform(self, index):
        """Load a transform and create its window/pipeline"""
        if 0 <= index < len(self.transforms):
            self.selected_transform_idx = index
            transform_class = self.transforms[index]
            
            # Create window with this transform
            self.current_window = get_transform_window(transform_class, self.img_path)
            self.current_pipeline = Pipeline(self.current_window)
            
            # Run pipeline to get initial output
            self.output_image, _ = self.current_pipeline.run_pipeline()
            
            log.info(f"Loaded transform: {transform_class.__name__}")
    
    def _render_transform_list(self):
        """Render the left panel with transform list"""
        imgui.begin_child("TransformList", imgui.ImVec2(200, 0), border=True)
        imgui.text("Built-in Transforms")
        imgui.separator()
        
        for i, name in enumerate(self.transform_names):
            is_selected = (i == self.selected_transform_idx)
            if imgui.selectable(name, is_selected)[0]:
                if i != self.selected_transform_idx:
                    self._load_transform(i)
        
        imgui.end_child()
    
    def _render_image_display(self):
        """Render the center panel with image output"""
        imgui.begin_child("ImageDisplay", imgui.ImVec2(0, 0), border=True)
        imgui.text("Image Output")
        imgui.separator()
        
        if self.output_image is not None:
            # Convert image for display
            img_rgb = self._prepare_image_for_display(self.output_image)
            if img_rgb is not None:
                h, w = img_rgb.shape[:2]
                
                # Calculate display size to fit in available space
                avail = imgui.get_content_region_avail()
                scale = min(avail.x / w, avail.y / h, 1.0)
                display_w = int(w * scale)
                display_h = int(h * scale)
                
                # Display image
                try:
                    # TODO: Fix texture creation for numpy arrays
                    # hello_imgui.image_from_asset is for file assets, not numpy arrays
                    # Need to use proper texture creation API (imgui.ImTextureID with backend-specific code)
                    # For now, this is a placeholder that needs testing in a real environment
                    texture = hello_imgui.image_from_asset(img_rgb)
                    imgui.image(texture, imgui.ImVec2(display_w, display_h))
                except Exception as e:
                    imgui.text(f"Error displaying image: {e}")
        else:
            imgui.text("No image to display")
        
        imgui.end_child()
    
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
            # Grayscale to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 3:
            # BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img
        
        return img_rgb
    
    def _render_parameters(self):
        """Render the parameters panel for the current transform"""
        imgui.begin_child("Parameters", imgui.ImVec2(300, 0), border=True)
        
        if self.current_window:
            transform_name = self.transform_names[self.selected_transform_idx]
            imgui.text(f"Parameters: {transform_name}")
            imgui.separator()
            
            # Render parameters for each transform in the window
            for transform in self.current_window.transforms:
                if transform.params:
                    imgui.push_id(str(id(transform)))
                    
                    if imgui.collapsing_header(transform.__class__.__name__, 
                                                imgui.TreeNodeFlags_.default_open):
                        for param in transform.params:
                            self._render_param(param, transform)
                    
                    imgui.pop_id()
        else:
            imgui.text("No transform selected")
        
        imgui.end_child()
    
    def _render_param(self, param, transform):
        """Render a single parameter widget"""
        from opencv_pg.models.params import IntSlider, FloatSlider, Choice, IntInput, FloatInput, Bool
        
        param_name = param.label or param.__class__.__name__
        
        try:
            if isinstance(param, IntSlider):
                changed, new_val = imgui.slider_int(
                    param_name, 
                    param._value or param.default or 0,
                    param.min_val,
                    param.max_val
                )
                if changed:
                    param._value = new_val
                    self._rerun_pipeline()
            
            elif isinstance(param, FloatSlider):
                changed, new_val = imgui.slider_float(
                    param_name,
                    param._value or param.default or 0.0,
                    param.min_val,
                    param.max_val
                )
                if changed:
                    param._value = new_val
                    self._rerun_pipeline()
            
            elif isinstance(param, Choice):
                current_val = param._value or param.default
                if current_val in param.choices:
                    current_idx = param.choices.index(current_val)
                else:
                    current_idx = 0
                
                changed, new_idx = imgui.combo(
                    param_name,
                    current_idx,
                    param.choices
                )
                if changed:
                    param._value = param.choices[new_idx]
                    self._rerun_pipeline()
            
            elif isinstance(param, Bool):
                changed, new_val = imgui.checkbox(
                    param_name,
                    param._value or param.default or False
                )
                if changed:
                    param._value = new_val
                    self._rerun_pipeline()
            
            elif isinstance(param, (IntInput, FloatInput)):
                # For now, just show as text
                imgui.text(f"{param_name}: {param._value or param.default}")
            
            else:
                # Generic parameter display
                imgui.text(f"{param_name}: {param._value or param.default}")
        
        except Exception as e:
            log.error(f"Error rendering param {param_name}: {e}")
            imgui.text(f"{param_name}: Error")
    
    def _rerun_pipeline(self):
        """Re-run the pipeline after parameter change"""
        if self.current_pipeline:
            try:
                self.output_image, _ = self.current_pipeline.run_pipeline()
            except Exception as e:
                log.error(f"Error running pipeline: {e}")
    
    def _show_docs(self):
        """Open documentation in browser"""
        if self.current_window:
            transform = self.current_window.transforms[0]
            doc_fname = doc_writer.RENDERED_DIR.joinpath(transform.get_doc_filename())
            if doc_fname.exists():
                webbrowser.open(f'file://{doc_fname}')
    
    def gui(self):
        """Main GUI rendering function"""
        # Main menu bar
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Exit")[0]:
                    hello_imgui.get_runner_params().app_shall_exit = True
                imgui.end_menu()
            
            if imgui.begin_menu("View"):
                if imgui.menu_item("Show Documentation", enabled=self.current_window is not None)[0]:
                    self._show_docs()
                imgui.end_menu()
            
            imgui.end_main_menu_bar()
        
        # Main layout with splitters
        # Left: Transform list
        self._render_transform_list()
        imgui.same_line()
        
        # Center and Right: Image and Parameters
        imgui.begin_group()
        
        # Get remaining width
        remaining_width = imgui.get_content_region_avail().x
        
        # Center: Image (take most of the space)
        image_width = remaining_width - 320  # Leave 320px for parameters
        imgui.begin_child("ImageContainer", imgui.ImVec2(image_width, 0), border=False)
        self._render_image_display()
        imgui.end_child()
        
        imgui.same_line()
        
        # Right: Parameters
        self._render_parameters()
        
        imgui.end_group()


def run_imgui_playground(img_path, no_docs=False, disable_info_widgets=False):
    """Launch the ImGui-based OpenCV Playground"""
    app = ImGuiPlayground(img_path, no_docs, disable_info_widgets)
    
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "OpenCV Playground"
    runner_params.app_window_params.window_geometry.size = (1400, 800)
    runner_params.app_window_params.resizable = True
    
    runner_params.callbacks.show_gui = app.gui
    
    immapp.run(runner_params=runner_params)
