#!/usr/bin/env python3
"""
Sistema de memoria persistente para el agente AI
Agente de memoria para mantener contexto de conversación
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime
from utils.core.translator import t
from utils.core.config_loader import get_max_messages_memory
from utils.core.logg.ui_logger import get_ui_logger
from utils.themes.styles import LOGS

class AgentMemory:
    """Gestor de memoria persistente para el agente"""
    
    def __init__(self, memory_file: str = ".antflow/memory.md", max_messages: int = None):
        self.memory_file = memory_file
        # Si no se especifica max_messages, usar el de la configuración
        self.max_messages = max_messages if max_messages is not None else get_max_messages_memory()
        self.messages: List[Dict[str, Any]] = []
        self.load_from_file()

        self.ui_logger = get_ui_logger()
    
    def add_message(self, role: str, content: str) -> None:
        """
        Añade un mensaje al historial
        
        Args:
            role: 'system', 'user', o 'assistant'
            content: Contenido del mensaje
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.messages.append(message)
        
        # Mantener solo los últimos max_messages
        if len(self.messages) > self.max_messages:
            # Siempre mantener el primer mensaje system si existe
            system_messages = [msg for msg in self.messages if msg["role"] == "system"]
            other_messages = [msg for msg in self.messages if msg["role"] != "system"]
            
            # Mantener el último system_message y los últimos max_messages-1 otros
            if system_messages:
                self.messages = [system_messages[-1]] + other_messages[-(self.max_messages-1):]
            else:
                self.messages = other_messages[-self.max_messages:]
        
        self.save_to_file()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Retorna el historial completo de mensajes
        
        Returns:
            Lista de mensajes en formato para el agente
        """
        return self.messages.copy()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Retorna SOLO el historial de conversación (excluyendo system y context)
        
        Returns:
            Lista de mensajes SOLO user/assistant
        """
        return [msg for msg in self.messages if msg["role"] in ["user", "assistant"]]
    
    def add_conversation_turn(self, user_msg: str, assistant_msg: str) -> None:
        """
        Añade un turno completo de conversación (user + assistant)
        
        Args:
            user_msg: Mensaje del usuario
            assistant_msg: Respuesta del asistente
        """
        self.add_message("user", user_msg)
        self.add_message("assistant", assistant_msg)
    
    def clear(self) -> None:
        """Limpia toda la memoria"""
        self.messages = []
        self.save_to_file()
        self.ui_logger.append(t("memory_cleared"))
        #self.ui_logger.append("[✗] Memoria limpiada")
    
    def save_to_file(self) -> None:
        """Guarda el historial en archivo markdown"""
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                f.write("# Memoria del Agente AI\n\n")
                f.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Total de mensajes:** {len(self.messages)}\n\n")
                f.write("---\n\n")
                
                for i, msg in enumerate(self.messages, 1):
                    emoji = {"system": "⚙️", "user": "👤", "assistant": "🤖"}.get(msg["role"], "📝")
                    f.write(f"## {i}. {emoji} {msg['role'].upper()}\n\n")
                    f.write(f"**Timestamp:** {msg.get('timestamp', 'N/A')}\n\n")
                    f.write(f"```\n{msg['content']}\n```\n\n")
                    f.write("---\n\n")
        except Exception as e:
            self.ui_logger.append(t("memory_save_error").format(error=e), LOGS.error)
    
    def load_from_file(self) -> None:
        """Carga el historial desde archivo markdown"""
        if not os.path.exists(self.memory_file):
            return
        
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parseo robusto del archivo markdown
            self.messages = []
            
            # Dividir por "---" que separan mensajes
            sections = content.split("---")
            
            for section in sections:
                section = section.strip()
                if not section or "## " not in section:
                    continue
                
                # Extraer rol
                role = None
                if "SYSTEM" in section:
                    role = "system"
                elif "USER" in section:
                    role = "user"
                elif "ASSISTANT" in section:
                    role = "assistant"
                
                if role:
                    # Extraer contenido entre ```
                    content_start = section.find("```")
                    if content_start != -1:
                        content_start += 3
                        content_end = section.find("```", content_start)
                        
                        if content_end != -1:
                            message_content = section[content_start:content_end].strip()
                            
                            # Extraer timestamp si existe
                            timestamp = "N/A"
                            if "**Timestamp:**" in section:
                                ts_start = section.find("**Timestamp:**") + 14
                                ts_end = section.find("\n", ts_start)
                                if ts_end != -1:
                                    timestamp = section[ts_start:ts_end].strip()
                            
                            self.messages.append({
                                "role": role,
                                "content": message_content,
                                "timestamp": timestamp
                            })
            
            # Aplicar límite manteniendo lógica actual (system + mensajes más nuevos)
            if len(self.messages) > self.max_messages:
                system_messages = [msg for msg in self.messages if msg["role"] == "system"]
                other_messages = [msg for msg in self.messages if msg["role"] != "system"]
                
                if system_messages:
                    self.messages = [system_messages[-1]] + other_messages[-(self.max_messages-1):]
                else:
                    self.messages = other_messages[-self.max_messages:]
                
        except Exception as e:
            self.ui_logger.append(t("memory_load_error").format(error=e), LOGS.error)
            self.messages = []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas de la memoria
        
        Returns:
            Diccionario con estadísticas
        """
        user_msgs = len([msg for msg in self.messages if msg["role"] == "user"])
        assistant_msgs = len([msg for msg in self.messages if msg["role"] == "assistant"])
        system_msgs = len([msg for msg in self.messages if msg["role"] == "system"])
        
        return {
            "total_messages": len(self.messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "system_messages": system_msgs,
            "max_messages": self.max_messages,
            "memory_file": self.memory_file
        }
    
    def initialize_with_system_prompt(self, system_prompt: str) -> None:
        """
        Inicializa la memoria con un system prompt si está vacía
        
        Args:
            system_prompt: Prompt inicial del sistema
        """
        if not self.messages:
            self.add_message("system", system_prompt)
            self.ui_logger.append("\n")
            self.ui_logger.append(t("memory_initialized"), LOGS.success)

# Instancia global para uso en toda la aplicación
agent_memory = AgentMemory()
