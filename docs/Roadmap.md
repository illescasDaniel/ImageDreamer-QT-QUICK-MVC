# Roadmap

The following is a list of planned enhancements, features, and current tasks for the ImageDreamer-QT-QUICK-MVC project. We aim to continually improve the application based on user feedback and technological advancements.

## Current TODOs

- [ ] **Unit Testing**
  - Add unit tests with `pytest` to ensure reliability and stability of the application.
  - Update invoke tasks to include a testing workflow that can be easily executed by contributors.

- [ ] **Refactor main.qml**
  - Investigate potential refactoring of `main.qml` to improve performance and maintainability. Consider modularization and componentization of UI elements where possible.

## Future enhancements/tasks

- [ ] Create app installers:
  - [x] Linux AppImage (see `create_appimage` in `/tasks/packaging.py`).
  - [ ] MacOS .app  (use `inv build --no-show-terminal` in `tasks.py`). [WIP] The .app works but it launches itself multiple times after the image generation... that doesn't happen when simply using `inv run`.
  - [ ] Windows signed installer.

- [ ] Release the app at itch.io

## Contributing

We welcome contributions from the community! Whether you're interested in fixing bugs, adding new features, or improving documentation, your help is greatly appreciated.

[Back to main README](../README.md)