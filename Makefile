SHELL := /bin/bash

# Default installation directory for the `todo` command
INSTALL_DIR ?= $(HOME)/.local/bin
TARGET := $(INSTALL_DIR)/todo
REPO_DIR := $(CURDIR)

.PHONY: install uninstall help

install: $(TARGET)

$(TARGET):
	@echo "Installing todo to $(TARGET) (PYTHONPATH=$(REPO_DIR))"
	@mkdir -p "$(INSTALL_DIR)"
	@printf '%s\n' '#!/usr/bin/env bash' 'PYTHONPATH="$(REPO_DIR)" exec python3 -m commands.cli "$$@"' > "$(TARGET)"
	@chmod 0755 "$(TARGET)"
	@echo "Installed $(TARGET)"

uninstall:
	@echo "Removing $(TARGET)"
	@rm -f "$(TARGET)"
	@echo "Removed $(TARGET)"

help:
	@echo "Usage:"
	@echo "  make install    # installs 'todo' to $(INSTALL_DIR) (default)"
	@echo "  make uninstall  # removes the installed 'todo'"
	@echo "Notes:"
	@echo "  - The installer writes a small wrapper that sets PYTHONPATH to the"
	@echo "    repository root so 'todo' finds the bundled commands package."
	@echo "  - If $(INSTALL_DIR) is not on your PATH, either add it or run:"
	@echo "      sudo make install INSTALL_DIR=/usr/local/bin"
