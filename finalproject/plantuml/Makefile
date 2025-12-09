# Makefile for generating PlantUML diagrams

# Source files
PUML_FILES = $(wildcard *.puml)
JPG_FILES = $(PUML_FILES:.puml=.jpg)
PNG_FILES = $(PUML_FILES:.puml=.png)
SVG_FILES = $(PUML_FILES:.puml=.svg)

# Default target - generate JPG
all: jpg

# Generate JPG files
jpg: $(JPG_FILES)

# Generate PNG files
png: $(PNG_FILES)

# Generate SVG files
svg: $(SVG_FILES)

# Pattern rules for different formats
%.jpg: %.puml
	plantuml -tjpg $<

%.png: %.puml
	plantuml -tpng $<

%.svg: %.puml
	plantuml -tsvg $<

# Clean generated files
clean:
	rm -f *.jpg *.png *.svg

# Generate all formats
all-formats: jpg png svg

# Help target
help:
	@echo "Available targets:"
	@echo "  make         - Generate JPG files (default)"
	@echo "  make jpg     - Generate JPG files"
	@echo "  make png     - Generate PNG files"
	@echo "  make svg     - Generate SVG files"
	@echo "  make all-formats - Generate all formats"
	@echo "  make clean   - Remove generated files"
	@echo ""
	@echo "PlantUML files found:"
	@echo "  $(PUML_FILES)"

.PHONY: all jpg png svg clean all-formats help
