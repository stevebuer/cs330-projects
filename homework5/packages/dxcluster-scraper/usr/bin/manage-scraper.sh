#!/bin/bash

# DX Scraper Service Management Script
SERVICE_NAME="dx-scraper"
SERVICE_FILE="/home/steve/GITHUB/cs330-projects/homework2/dx-scraper.service"
SYSTEM_SERVICE_DIR="/etc/systemd/system"

show_usage() {
    echo "Usage: $0 {install|uninstall|start|stop|restart|status|logs|enable|disable}"
    echo ""
    echo "Commands:"
    echo "  install   - Copy service file to systemd and reload daemon"
    echo "  uninstall - Remove service file from systemd"
    echo "  start     - Start the DX scraper service"
    echo "  stop      - Stop the DX scraper service"
    echo "  restart   - Restart the DX scraper service"
    echo "  status    - Show service status"
    echo "  logs      - Show recent service logs"
    echo "  enable    - Enable service to start on boot"
    echo "  disable   - Disable service from starting on boot"
}

install_service() {
    echo "Installing DX scraper service..."
    
    if [ ! -f "$SERVICE_FILE" ]; then
        echo "Error: Service file not found at $SERVICE_FILE"
        exit 1
    fi
    
    sudo cp "$SERVICE_FILE" "$SYSTEM_SERVICE_DIR/"
    sudo systemctl daemon-reload
    echo "Service installed successfully. Use 'sudo $0 enable' to enable auto-start on boot."
}

uninstall_service() {
    echo "Uninstalling DX scraper service..."
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null
    sudo systemctl disable "$SERVICE_NAME" 2>/dev/null
    sudo rm -f "$SYSTEM_SERVICE_DIR/$SERVICE_NAME.service"
    sudo systemctl daemon-reload
    echo "Service uninstalled successfully."
}

case "$1" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    start)
        echo "Starting DX scraper service..."
        sudo systemctl start "$SERVICE_NAME"
        ;;
    stop)
        echo "Stopping DX scraper service..."
        sudo systemctl stop "$SERVICE_NAME"
        ;;
    restart)
        echo "Restarting DX scraper service..."
        sudo systemctl restart "$SERVICE_NAME"
        ;;
    status)
        sudo systemctl status "$SERVICE_NAME"
        ;;
    logs)
        echo "Recent logs for DX scraper service:"
        sudo journalctl -u "$SERVICE_NAME" -n 50 --no-pager
        ;;
    enable)
        echo "Enabling DX scraper service to start on boot..."
        sudo systemctl enable "$SERVICE_NAME"
        ;;
    disable)
        echo "Disabling DX scraper service from starting on boot..."
        sudo systemctl disable "$SERVICE_NAME"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit 0