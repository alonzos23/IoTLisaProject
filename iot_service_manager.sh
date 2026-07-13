#!/bin/bash
#
# Script de gestión del servicio IoT Sensor System
# Uso: ./iot_service_manager.sh {start|stop|restart|status|enable|disable|logs|install}
#

SERVICE_NAME="iot-sensor-system"
SERVICE_FILE="iot-sensor-system.service"
PYTHON_SCRIPT="iot_sensor_system.py"
INSTALL_DIR="/home/pi/iot_sensors"
LOG_FILE="/var/log/iot_sensor_system.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar si el script se ejecuta como root (para algunas operaciones)
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Esta operación requiere privilegios de root. Use: sudo $0 $1"
        exit 1
    fi
}

# Instalar el servicio
install_service() {
    check_root
    
    print_info "Instalando servicio IoT Sensor System..."
    
    # Crear directorio si no existe
    if [ ! -d "$INSTALL_DIR" ]; then
        print_info "Creando directorio $INSTALL_DIR..."
        mkdir -p "$INSTALL_DIR"
        chown pi:pi "$INSTALL_DIR"
    fi
    
    # Copiar archivos
    if [ -f "$PYTHON_SCRIPT" ]; then
        print_info "Copiando script Python..."
        cp "$PYTHON_SCRIPT" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/$PYTHON_SCRIPT"
        chown pi:pi "$INSTALL_DIR/$PYTHON_SCRIPT"
    else
        print_error "No se encuentra el archivo $PYTHON_SCRIPT"
        exit 1
    fi
    
    # Copiar archivo de servicio
    if [ -f "$SERVICE_FILE" ]; then
        print_info "Instalando archivo de servicio systemd..."
        cp "$SERVICE_FILE" /etc/systemd/system/
        chmod 644 "/etc/systemd/system/$SERVICE_FILE"
    else
        print_error "No se encuentra el archivo $SERVICE_FILE"
        exit 1
    fi
    
    # Crear archivo de log si no existe
    if [ ! -f "$LOG_FILE" ]; then
        touch "$LOG_FILE"
        chown pi:pi "$LOG_FILE"
        chmod 644 "$LOG_FILE"
    fi
    
    # Recargar systemd
    print_info "Recargando configuración de systemd..."
    systemctl daemon-reload
    
    print_success "Servicio instalado correctamente!"
    print_info "Para habilitar el inicio automático: sudo $0 enable"
    print_info "Para iniciar el servicio: sudo $0 start"
}

# Iniciar el servicio
start_service() {
    print_info "Iniciando servicio $SERVICE_NAME..."
    sudo systemctl start "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        print_success "Servicio iniciado correctamente"
        sleep 2
        status_service
    else
        print_error "Error al iniciar el servicio"
        exit 1
    fi
}

# Detener el servicio
stop_service() {
    print_info "Deteniendo servicio $SERVICE_NAME..."
    sudo systemctl stop "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        print_success "Servicio detenido correctamente"
    else
        print_error "Error al detener el servicio"
        exit 1
    fi
}

# Reiniciar el servicio
restart_service() {
    print_info "Reiniciando servicio $SERVICE_NAME..."
    sudo systemctl restart "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        print_success "Servicio reiniciado correctamente"
        sleep 2
        status_service
    else
        print_error "Error al reiniciar el servicio"
        exit 1
    fi
}

# Ver estado del servicio
status_service() {
    print_info "Estado del servicio $SERVICE_NAME:"
    echo ""
    sudo systemctl status "$SERVICE_NAME" --no-pager
    echo ""
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "El servicio está ACTIVO"
    else
        print_warning "El servicio NO está activo"
    fi
    
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        print_info "Inicio automático: HABILITADO"
    else
        print_info "Inicio automático: DESHABILITADO"
    fi
}

# Habilitar inicio automático
enable_service() {
    check_root
    print_info "Habilitando inicio automático del servicio..."
    systemctl enable "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        print_success "Inicio automático habilitado"
    else
        print_error "Error al habilitar inicio automático"
        exit 1
    fi
}

# Deshabilitar inicio automático
disable_service() {
    check_root
    print_info "Deshabilitando inicio automático del servicio..."
    systemctl disable "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        print_success "Inicio automático deshabilitado"
    else
        print_error "Error al deshabilitar inicio automático"
        exit 1
    fi
}

# Ver logs del servicio
view_logs() {
    echo ""
    print_info "Logs del servicio (últimas 50 líneas):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Mostrar logs del journal
    sudo journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_info "Para ver logs en tiempo real: sudo journalctl -u $SERVICE_NAME -f"
    print_info "Para ver archivo de log: tail -f $LOG_FILE"
}

# Mostrar ayuda
show_help() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🔧 GESTOR DEL SERVICIO IOT SENSOR SYSTEM"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Uso: $0 {comando}"
    echo ""
    echo "Comandos disponibles:"
    echo "  install   - Instalar el servicio (requiere sudo)"
    echo "  start     - Iniciar el servicio"
    echo "  stop      - Detener el servicio"
    echo "  restart   - Reiniciar el servicio"
    echo "  status    - Ver estado del servicio"
    echo "  enable    - Habilitar inicio automático (requiere sudo)"
    echo "  disable   - Deshabilitar inicio automático (requiere sudo)"
    echo "  logs      - Ver logs del servicio"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  sudo $0 install     # Primera vez: instalar el servicio"
    echo "  sudo $0 start       # Iniciar el servicio"
    echo "  sudo $0 status      # Ver si está funcionando"
    echo "  sudo $0 logs        # Ver qué está haciendo"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Menú principal
case "$1" in
    install)
        install_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    logs)
        view_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Comando no reconocido: $1"
        show_help
        exit 1
        ;;
esac

exit 0
