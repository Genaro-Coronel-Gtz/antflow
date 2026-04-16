# utils/core/global_logger.py
"""Logger global compartido para toda la aplicación"""

class UILogger:
    """Logger global que puede ser accedido desde cualquier módulo"""
    
    def __init__(self):
        self._logger = None
    
    def set_logger(self, logger_instance):
        """Establece la instancia del logger"""
        self._logger = logger_instance
    
    def append(self, message: str, msg_type = "default"):
        """Añade un mensaje al logger si está disponible"""
        if self._logger:
            self._logger.append(message, msg_type)
    
    def is_available(self) -> bool:
        """Verifica si el logger está disponible"""
        return self._logger is not None

# Instancia global única
_ui_logger = UILogger()

def get_ui_logger():
    """Retorna el logger global para uso de otros módulos"""
    return _ui_logger

def set_ui_logger(logger_instance):
    """Establece el logger global"""
    _ui_logger.set_logger(logger_instance)
