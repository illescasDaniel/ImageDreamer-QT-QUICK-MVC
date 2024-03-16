import os
import shutil
from pathlib import Path

from invoke.tasks import task
from invoke.context import Context

from .building import build
from .common import cleanup_compressed_files, app_name, app_version


@task(pre=[build])
def create_appimage(ctx: Context):
	'''
	Creates an AppImage, make sure to download AppImageKit from: https://github.com/AppImage/AppImageKit/releases
	Place it in "resources/" as appimagetool-x86_64.AppImage
	'''
	appdir_path = Path(f'{app_name}-{app_version}.AppDir')
	dist_path = Path('dist')
	# cleanup
	output_file = f'{app_name}-x86_64.AppImage'
	if Path(output_file).exists():
		os.remove(output_file)
	if appdir_path.exists():
		shutil.rmtree(appdir_path)
	# Step 1: Prepare the AppDir structure
	appdir_path.mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/bin').mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/lib').mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/share/applications').mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/share/icons/hicolor/scalable/apps').mkdir(parents=True, exist_ok=True)
	# Step 2: Copy files to AppDir
	# Assuming the executable and all dependencies are in the 'dist' directory
	for item in (dist_path / app_name).iterdir():
		if item.is_dir():
			shutil.copytree(item, appdir_path / 'usr/bin' / item.name, dirs_exist_ok=True)
		else:
			shutil.copy(item, appdir_path / 'usr/bin')
	# Copying the desktop and icon files
	shutil.copy(f'resources/{app_name}.desktop', appdir_path / 'usr/share/applications')
	shutil.copy(f'resources/{app_name}.desktop', appdir_path)
	shutil.copy('src/assets/app_icon.png', appdir_path / f'{app_name}.png')
	shutil.copy('src/assets/app_icon.png', appdir_path / f'usr/share/icons/hicolor/scalable/apps/{app_name}.png')
	# Making a symbolic link for the AppRun (this is required by AppImage)
	(appdir_path / 'AppRun').symlink_to(Path('usr/bin') / app_name)
	# Step 3: Use appimagetool to generate the AppImage
	# download the appropiate file from: https://github.com/AppImage/AppImageKit/releases
	cmd = f'resources/appimagetool-x86_64.AppImage {appdir_path}'
	ctx.run(cmd, echo=True)
	# remove appdir folder
	shutil.rmtree(appdir_path)
	# make the AppImage executable
	make_it_executable = f'chmod +x {output_file}'
	ctx.run(make_it_executable)
	# move it to the dist folder
	shutil.move(output_file, 'dist')
	# success message
	print(f'AppImage for {app_name} has been created.')

@task(pre=[build])
def create_tar_ball(ctx: Context):
	'''
	Compress program and its folders.
	'''
	output_file_path = f'dist/{app_name}/image_dreamer_no_model.tar.gz'
	cleanup_compressed_files()
	ctx.run(f'tar -czvf "{output_file_path}" dist/{app_name}/')

@task(pre=[build])
def create_7zip(ctx: Context):
	'''
	Compress program and its folders. You need p7zip-full.
	'''
	output_file_path = f'dist/{app_name}/image_dreamer_no_model.7z'
	cleanup_compressed_files()
	ctx.run(f'7z a -t7z -m0=lzma2 -mx=9 -ms=on {output_file_path} dist/{app_name}/')

@task(pre=[build])
def create_mac_dmg(ctx: Context):
	'''
	Compresses the .app folder inside dist (generated using inv build) into a dmg.
	'''
	app_to_dmg = f'hdiutil create -volname "{app_name}" -srcfolder dist/{app_name}.app -ov -format UDZO -imagekey zlib-level=9 dist/{app_name}.dmg'
	ctx.run(app_to_dmg)
