# OpenCV Playground
The OpenCV Playground is an ImGui-based application that brings together improved documentation alongside OpenCV functions with the ability to explore the effects of function parameters on an image in real time.

It also comes with a custom `Pipeline Launcher` that allows you to build and interact with your own sequence of image transformations along with custom build functions.

Full documentation can be found on [Read the Docs](https://opencv-pg.readthedocs.io/en/latest/).

## Recent Changes (v2.0)
**The GUI has been rewritten using imgui_bundle (replacing Qt6).** This provides a more modern immediate-mode GUI experience and better cross-platform compatibility. Dependencies have also been updated to the latest versions of numpy and opencv.

## Demo
<a href="https://drive.google.com/uc?export=view&id=1i4jmCHebu1_ognIwj2n4vtpCaT8BHWGI"><img src="https://media.giphy.com/media/GQj3aod8oKoxpJ4sC3/giphy.gif" style="width: 500px; height: auto;" /></a>


## Installation
Currently tested with Python 3.12 and opencv-contrib-python-headless 4.12.0.88.

**Requirements:**
- Python >= 3.7
- imgui-bundle >= 1.92.0
- opencv-contrib-python-headless >= 4.12.0
- numpy >= 2.2.0

From PyPi:

```shell
pip install opencv-pg
```

From Github Repo:

```shell
pip install git+https://github.com/opencv-pg/opencv-pg
```

### Note for Linux Users
With the migration to imgui_bundle, the previous Qt-related dependencies and issues on Linux are no longer relevant. The application should work out of the box on most Linux distributions with Python 3.7+.


## Usage
### Playground
To launch the OpenCV Playground with:
* The built-in image:

```shell
opencvpg
```

* An image of your choice:

```shell
opencvpg --image <path-to-image.png>
```

* Without the documentation window:

```shell
opencvpg --no-docs
```

### Custom Pipeline
The following is an example of building a custom Pipeline.

```python
from opencv_pg import Pipeline, Window, launch_pipeline
from opencv_pg import support_transforms as supt
from opencv_pg import transforms as tf

if __name__ == '__main__':
    my_image = '/path/to/image.png'

    # Creates two windows
    pipeline = Pipeline([
        Window([
            supt.LoadImage(my_image),
            supt.CvtColor(),
            tf.InRange(),
            supt.BitwiseAnd(),
        ]),
        Window([
            tf.Canny(),
        ]),
    ])

    launch_pipeline(pipeline)
```

Then run the file.

## Development
### Installation
To install in development mode:

```shell
git clone https://github.com/opencv-pg/opencv-pg
pip install -e opencv-pg/[dev]
```

### Running Tests
```shell
cd tests
pytest
```

### Generating Docs
* Go into the top level `docs` directory
* run `sphinx-apidoc -f -o source/ ../src/opencv_pg`
* run `make html`

Output will be in the `docs/build/html/` directory.
