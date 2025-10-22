# Simple Makefile to render PlantUML diagrams to docs directory

# Default target
all: docs/plantuml_er_diagram.png

# Render PNG from PlantUML source using system PlantUML
docs/plantuml_er_diagram.png: docs/plantuml_er_diagram.puml
	plantuml $<

# Alternative target using JAR file (if PlantUML not installed system-wide)
jar: docs/plantuml_er_diagram.puml
	@if [ -f plantuml.jar ]; then \
		java -jar plantuml.jar -o . $<; \
	else \
		echo "plantuml.jar not found. Download from https://plantuml.com/download"; \
		exit 1; \
	fi

# Clean generated files
clean:
	rm -f docs/*.png docs/*.svg docs/*.eps

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Render the ER diagram as PNG in docs/ (default)"
	@echo "  jar     - Render using plantuml.jar in current directory to docs/"
	@echo "  clean   - Remove generated image files from docs/"
	@echo "  help    - Show this help message"
	@echo ""
	@echo "PlantUML is already installed on your system at /usr/bin/plantuml"