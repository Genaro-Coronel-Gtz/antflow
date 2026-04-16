#!/usr/bin/env python3
"""
Sistema de eventos centralizado para desacoplar componentes
"""

from typing import Dict, List, Callable, Any
import threading
import time


class EventBus:
    """
    Bus de eventos centralizado para comunicación desacoplada
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._responses: Dict[str, Any] = {}
        self._response_events: Dict[str, threading.Event] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Suscribe una función a un tipo de evento
        
        Args:
            event_type: Tipo de evento
            callback: Función a ejecutar cuando se publique el evento
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
    
    def publish(self, event_type: str, data=None):
        """
        Publica un evento de forma asíncrona (fire and forget)
        
        Args:
            event_type: Tipo de evento
            data: Datos a pasar al callback
        """
        with self._lock:
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    try:
                        # Ejecutar en un thread separado para no bloquear
                        threading.Thread(target=callback, args=(data,), daemon=True).start()
                    except Exception as e:
                        print(f"Error en callback del evento {event_type}: {e}")
    
    def publish_sync(self, event_type: str, data=None):
        """
        Publica un evento de forma síncrona y espera respuesta
        
        Args:
            event_type: Tipo de evento
            data: Datos a pasar al callback
            
        Returns:
            Respuesta del primer callback que responda
        """
        response = None
        with self._lock:
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    try:
                        result = callback(data)
                        if result is not None:
                            response = result
                            break
                    except Exception as e:
                        print(f"Error en callback del evento {event_type}: {e}")
        return response
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Elimina una suscripción
        
        Args:
            event_type: Tipo de evento
            callback: Función a eliminar
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                except ValueError:
                    pass


# Instancia global del bus de eventos
event_bus = EventBus()
