# ImageDreamer-QT-QUICK-MVC
Simple app to generate images from text. Currently, it is using "DreamShaperXL v2 model" as the SDXL Turbo model.

<p align="center">
	<img src="assets/program_gnome.png" alt="linux GNOME program screenshot" width="300" />
</p>


## Requirements
- DreamShaperXL v2 model
	- SFW v2 Turbo DPM++ SDE: https://civitai.com/models/112902?modelVersionId=341981
- invoke (Optional, but recommended to easily build and run the app)
- HuggingFace's accelerate, diffusers and transformers
- Pytorch
- PySide6
- xformers (optimizations for diffusers)
- GPU required. It works with NVIDIA GPUs (tested on 8GB 4070 Laptop) and Apple Silicon chips (untested).

## Development requirements
- pytest (unit tests)
- pyinstaller (create executable in tasks.py)
- pipreqs (genereate requirements.txt in tasks.py)

## Easy installation using conda (Anaconda/miniconda)
1. Clone the repo. `git clone https://github.com/illescasDaniel/ImageDreamer-QT-QUICK-MVC.git`
`cd ImageDreamer-QT-QUICK-MVC`
2. Download [DreamShaperXL SFW v2 Turbo DPM++ SDE](https://civitai.com/models/112902?modelVersionId=341981) and move it inside the project here: "resources/models/dreamshaperXL_sfwV2TurboDPMSDE.safetensors".
3. Install conda (anaconda or miniconda).
https://www.anaconda.com/download
https://docs.anaconda.com/free/miniconda/
4. Create a conda environment with all its dependencies.
	- Ubuntu/macOS: `./install.sh`
	- Windows (**Anaconda Powershell Prompt**, outside of VSCode): `.\install.ps1`
5. Activate the new environment: `conda activate ImageDreamer`
6. Run the app: `invoke run`
7. Images will be saved to the output folder automatically.

**Note:** this is the preferred way, since using pip won't use your system theme.

**NOTE:** The first time you run it, after you press the "Generate" button it will download the model, please be patient, you can see the progress in the terminal where you run the command.

## Easy installation using pip
1. Clone the repo. `git clone https://github.com/illescasDaniel/ImageDreamer-QT-QUICK-MVC.git`
`cd ImageDreamer-QT-QUICK-MVC`
2. Download [DreamShaperXL SFW v2 Turbo DPM++ SDE](https://civitai.com/models/112902?modelVersionId=341981) and move it inside the project here: "resources/models/dreamshaperXL_sfwV2TurboDPMSDE.safetensors".
3. Create a virtual environment: `python3 -m venv imagedreamer-env`
4. Activate the new environment: `source imagedreamer-env/bin/activate` (`deactivate` to deactivate it)
5. Install dependencies: `pip3 install -r requirements.txt`
6. Run the app with `python3 src/main.py` or install `invoke` with `pip3 install invoke` and then `invoke run`.

**Note**: <sup>"Having Qt installed in your system will not interfere with your PySide6 installation if you do it via pip install, because the Python packages (wheels) include already Qt binaries. Most notably, style plugins from the system won’t have any effect on PySide applications." source: https://doc.qt.io/qtforpython-6/quickstart.html </sup> This means you won't use your system's default style if you use pip to install pyside6, AFAIK.


## Execution
Use `invoke run` to run the python app.

You can use `invoke --list` for all available tasks, use `invoke --help <command>` to get help about a specific command.

### TODOs:
- [ ] Test on different devices.
	- [x] Test on linux
	- [x] Test on windows
	- [ ] Test on macOS
- [ ] Add unit tests with `pytest`.
- [ ] Test pyinstaller and add instructions if necessary.
- [ ] Update tasks.py
- [ ] Maybe refactor main.qml

---

#### Acknowledgments

<sup>This project uses the **DreamShaperXL v2 model** checkpoint from [Civitai](https://civitai.com/models/112902?modelVersionId=341981). We appreciate the efforts of the creators for making this model available, enhancing our application's capabilities.</sup>
- <sup> **Source:** [Civitai - SDXL Turbo Checkpoint](https://civitai.com/models/112902?modelVersionId=341981)</sup>
- <sup>**Usage:** Integrated to generate images from text descriptions in a Python GUI application, which operates locally on the user's device.</sup>
- <sup>**License:** [LICENSE-SDXL-Turbo](https://raw.githubusercontent.com/Stability-AI/generative-models/main/model_licenses/LICENSE-SDXL-Turbo)</sup>

<sup>This application is built using the **Qt framework via PySide6**, the official set of Python bindings. The versatility and power of Qt have enabled us to create a robust, cross-platform user interface. Our thanks go to the Qt Company and the open-source contributors for making such a valuable resource available to the developer community.</sup>

<sup>Additionally, this project utilizes several frameworks from [Hugging Face](https://huggingface.co/), including **Accelerate**, **Transformers**, and **Diffusers**. These tools provide essential functionality for efficient model training, implementation, and image generation from text. Their integration plays a critical role in the operation and efficiency of our application.</sup>

#### License

<sup>This software is released under the **MIT License**. See the LICENSE file for more details.</sup>

<sup>This project incorporates an SDXL Turbo model for generating images from text descriptions. The SDXL Turbo model is developed by Stability AI and hosted on Hugging Face, available under a non-commercial license. Users interested in integrating the model with this application must comply with the terms of the non-commercial license. **While the source code of this application is released under the MIT License, allowing for wide-ranging use, modification, and distribution, it is important to note that the use of an SDXL Turbo model itself for any commercial purposes is subject to the restrictions of its non-commercial license.** We highly recommend reviewing the model's license terms [here](https://huggingface.co/stabilityai/sdxl-turbo) before using it with this application.</sup>

<sup>Additionally, this application makes use of the **Qt framework and PySide6**, licensed under the GNU Lesser General Public License (LGPL) version 3. We adhere to the licensing terms specified by these projects and appreciate the opportunity to build upon the work provided by the broader open-source community. For more information on Qt and its licensing, please visit [Qt Licensing](https://www.qt.io/licensing/).</sup>
