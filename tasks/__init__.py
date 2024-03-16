from invoke.collection import Collection

from .execution import run, run_executable, run_appimage, run_mac_app
from .building import build
from .packaging import create_appimage, create_tar_ball, create_7zip, create_mac_dmg
from .utility import generate_requirements


ns = Collection()
ns.add_task(run) #type: ignore
ns.add_task(run_executable) #type: ignore
ns.add_task(run_appimage) #type: ignore
ns.add_task(run_mac_app) #type: ignore
ns.add_task(build) #type: ignore
ns.add_task(create_appimage) #type: ignore
ns.add_task(create_tar_ball) #type: ignore
ns.add_task(create_7zip) #type: ignore
ns.add_task(create_mac_dmg) #type: ignore
ns.add_task(generate_requirements) #type: ignore
