#!/bin/sh

# Detect OS platform
UNAME=$(uname | tr "[:upper:]" "[:lower:]")

# Linux
if [ "$UNAME" = "linux" ]; then
	conda env create -f environment_linux_dev.yml
# macOS
elif [ "$UNAME" = "darwin" ]; then
	conda env create -f environment_macOS_dev.yml
# BSD
elif [ "$UNAME" = "freebsd" ] || [ "$UNAME" = "netbsd" ] || [ "$UNAME" = "openbsd" ]; then
	echo "Maybe Unsupported"
	conda env create -f environment_linux_dev.yml
else
	echo "Windows? Please use install-windows-dev.ps1 with Anaconda Powershell Prompt, outside of VSCode"
fi
