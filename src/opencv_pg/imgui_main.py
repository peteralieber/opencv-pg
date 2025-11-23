"""
Main ImGui-based GUI for OpenCV Playground

This is a complete rewrite of the Qt6-based GUI using imgui_bundle.
"""
import logging
from pathlib import Path
import numpy as np
import cv2
from imgui_bundle import imgui, hello_imgui, immapp
from imgui_bundle import imgui_md

log = logging.getLogger(__name__)


class ImGuiApp:
    """Main ImGui Application for OpenCV Playground"""
    
    def __init__(self, img_path=None):
        self.img_path = img_path
        self.image = None
        self.texture_id = None
        self.selected_transform = 0
        self.transform_names = [
            "Blur",
            "GaussianBlur", 
            "Canny",
            "Threshold",
            "InRange",
        ]
        
        # Parameters for transforms (example)
        self.gaussian_kernel_size = 5
        self.gaussian_sigma = 1.0
        self.canny_threshold1 = 100
        self.canny_threshold2 = 200
        
        # Load initial image
        if img_path and Path(img_path).exists():
            self.load_image(img_path)
    
    def load_image(self, path):
        """Load an image from file"""
        self.image = cv2.imread(str(path))
        if self.image is not None:
            log.info(f"Loaded image: {path}, shape: {self.image.shape}")
    
    def apply_transform(self):
        """Apply the selected transform to the image"""
        if self.image is None:
            return None
            
        result = self.image.copy()
        transform_name = self.transform_names[self.selected_transform]
        
        try:
            if transform_name == "GaussianBlur":
                ksize = self.gaussian_kernel_size
                if ksize % 2 == 0:
                    ksize += 1  # Must be odd
                result = cv2.GaussianBlur(result, (ksize, ksize), self.gaussian_sigma)
            elif transform_name == "Canny":
                gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY) if len(result.shape) == 3 else result
                result = cv2.Canny(gray, self.canny_threshold1, self.canny_threshold2)
                if len(result.shape) == 2:
                    result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            elif transform_name == "Blur":
                result = cv2.blur(result, (5, 5))
            elif transform_name == "Threshold":
                gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY) if len(result.shape) == 3 else result
                _, result = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                if len(result.shape) == 2:
                    result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        except Exception as e:
            log.error(f"Error applying transform {transform_name}: {e}")
            return self.image
            
        return result
    
    def image_to_texture(self, img):
        """Convert OpenCV image (BGR) to texture for ImGui"""
        if img is None:
            return None
        
        # Convert BGR to RGB for display
        if len(img.shape) == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        
        return img_rgb
    
    def gui(self):
        """Main GUI rendering function"""
        # Left panel: Transform list
        imgui.begin_child("TransformList", imgui.ImVec2(200, 0), border=True)
        imgui.text("Transforms")
        imgui.separator()
        
        for i, name in enumerate(self.transform_names):
            if imgui.selectable(name, self.selected_transform == i)[0]:
                self.selected_transform = i
        
        imgui.end_child()
        imgui.same_line()
        
        # Center panel: Image display
        imgui.begin_child("ImageDisplay", imgui.ImVec2(0, -200), border=True)
        imgui.text("Image Output")
        imgui.separator()
        
        if self.image is not None:
            result_img = self.apply_transform()
            if result_img is not None:
                img_rgb = self.image_to_texture(result_img)
                if img_rgb is not None:
                    # Display the image
                    h, w = img_rgb.shape[:2]
                    # Scale to fit window
                    avail = imgui.get_content_region_avail()
                    scale = min(avail.x / w, (avail.y - 20) / h, 1.0)
                    display_w = int(w * scale)
                    display_h = int(h * scale)
                    
                    # Create texture from numpy array
                    imgui.image(
                        hello_imgui.image_from_asset(img_rgb),
                        imgui.ImVec2(display_w, display_h)
                    )
        else:
            imgui.text("No image loaded")
        
        imgui.end_child()
        
        # Bottom panel: Transform parameters
        imgui.begin_child("Parameters", imgui.ImVec2(0, 0), border=True)
        imgui.text("Transform Parameters")
        imgui.separator()
        
        transform_name = self.transform_names[self.selected_transform]
        if transform_name == "GaussianBlur":
            changed, self.gaussian_kernel_size = imgui.slider_int(
                "Kernel Size", self.gaussian_kernel_size, 1, 31
            )
            changed, self.gaussian_sigma = imgui.slider_float(
                "Sigma", self.gaussian_sigma, 0.1, 10.0
            )
        elif transform_name == "Canny":
            changed, self.canny_threshold1 = imgui.slider_int(
                "Threshold 1", self.canny_threshold1, 0, 255
            )
            changed, self.canny_threshold2 = imgui.slider_int(
                "Threshold 2", self.canny_threshold2, 0, 255
            )
        else:
            imgui.text(f"No parameters for {transform_name}")
        
        imgui.end_child()


def run_imgui_playground(img_path=None):
    """Launch the ImGui-based playground"""
    app = ImGuiApp(img_path)
    
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "OpenCV Playground (ImGui)"
    runner_params.app_window_params.window_geometry.size = (1200, 800)
    
    runner_params.callbacks.show_gui = app.gui
    
    immapp.run(runner_params=runner_params)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_imgui_playground()
