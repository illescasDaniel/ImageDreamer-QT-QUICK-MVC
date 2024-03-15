from invoke.collection import Collection
from .execution import run, run_executable, run_app_image
from .building import build
from .packaging import create_appimage, create_tar_ball, create_7zip
from .utility import generate_requirements

ns = Collection()
ns.add_task(run) #type: ignore
ns.add_task(run_executable) #type: ignore
ns.add_task(run_app_image) #type: ignore
ns.add_task(build) #type: ignore
ns.add_task(create_appimage) #type: ignore
ns.add_task(create_tar_ball) #type: ignore
ns.add_task(create_7zip) #type: ignore
ns.add_task(generate_requirements) #type: ignore
