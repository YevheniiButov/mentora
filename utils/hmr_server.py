"""
Hot Module Replacement Server для Advanced Dental Editor
Обрабатывает WebSocket соединения и отслеживает изменения файлов
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Set, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

logger = logging.getLogger(__name__)

class HMRFileWatcher(FileSystemEventHandler):
    """Отслеживает изменения файлов и уведомляет клиентов"""
    
    def __init__(self, hmr_server):
        self.hmr_server = hmr_server
        self.watched_files = set()
        self.ignored_patterns = {
            '.git', '__pycache__', '.pyc', '.DS_Store',
            'node_modules', '.env', '.tmp', '.cache'
        }
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        if self.should_ignore_file(file_path):
            return
        
        logger.info(f"File modified: {file_path}")
        self.hmr_server.notify_file_change(file_path, 'modified')
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        if self.should_ignore_file(file_path):
            return
        
        logger.info(f"File created: {file_path}")
        self.hmr_server.notify_file_change(file_path, 'created')
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        if self.should_ignore_file(file_path):
            return
        
        logger.info(f"File deleted: {file_path}")
        self.hmr_server.notify_file_change(file_path, 'deleted')
    
    def should_ignore_file(self, file_path: str) -> bool:
        """Проверяет, нужно ли игнорировать файл"""
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        
        # Игнорируем файлы по паттернам
        for pattern in self.ignored_patterns:
            if pattern in file_path:
                return True
        
        # Игнорируем временные файлы
        if file_name.startswith('.') or file_name.endswith('~'):
            return True
        
        return False
    
    def add_watch(self, file_path: str):
        """Добавляет файл для отслеживания"""
        self.watched_files.add(file_path)
        logger.info(f"Added to watch: {file_path}")
    
    def remove_watch(self, file_path: str):
        """Удаляет файл из отслеживания"""
        self.watched_files.discard(file_path)
        logger.info(f"Removed from watch: {file_path}")


class HMRServer:
    """Сервер Hot Module Replacement"""
    
    def __init__(self, app=None):
        self.app = app
        self.clients: Dict[str, dict] = {}
        self.file_watcher = HMRFileWatcher(self)
        self.observer = None
        self.watch_thread = None
        self.is_running = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Инициализация HMR сервера для Flask приложения"""
        self.app = app
        
        # Настройка логирования
        logger.setLevel(logging.INFO)
        
        # Регистрируем WebSocket маршруты
        self.register_websocket_routes(app)
        
        # Запускаем файловый наблюдатель
        self.start_file_watcher()
        
        logger.info("HMR Server initialized")
    
    def register_websocket_routes(self, app):
        """Регистрирует WebSocket маршруты"""
        try:
            from flask_socketio import SocketIO, emit, join_room, leave_room
            
            # Создаем SocketIO экземпляр
            self.socketio = SocketIO(app, cors_allowed_origins="*")
            
            @self.socketio.on('connect')
            def handle_connect():
                client_id = self.generate_client_id()
                self.clients[client_id] = {
                    'id': client_id,
                    'connected_at': datetime.now(),
                    'capabilities': [],
                    'rooms': set()
                }
                logger.info(f"Client connected: {client_id}")
                emit('connected', {'client_id': client_id})
            
            @self.socketio.on('disconnect')
            def handle_disconnect():
                client_id = request.sid
                if client_id in self.clients:
                    del self.clients[client_id]
                    logger.info(f"Client disconnected: {client_id}")
            
            @self.socketio.on('register')
            def handle_register(data):
                client_id = request.sid
                if client_id in self.clients:
                    self.clients[client_id].update({
                        'capabilities': data.get('capabilities', []),
                        'user_agent': data.get('user_agent', ''),
                        'timestamp': data.get('timestamp', time.time())
                    })
                    logger.info(f"Client registered: {client_id}")
                    emit('registered', {'status': 'ok'})
            
            @self.socketio.on('watch_file')
            def handle_watch_file(data):
                client_id = request.sid
                file_path = data.get('file_path')
                
                if client_id in self.clients and file_path:
                    self.file_watcher.add_watch(file_path)
                    self.clients[client_id]['rooms'].add(f'file_{file_path}')
                    join_room(f'file_{file_path}')
                    emit('file_watched', {'file_path': file_path})
            
            @self.socketio.on('unwatch_file')
            def handle_unwatch_file(data):
                client_id = request.sid
                file_path = data.get('file_path')
                
                if client_id in self.clients and file_path:
                    self.file_watcher.remove_watch(file_path)
                    self.clients[client_id]['rooms'].discard(f'file_{file_path}')
                    leave_room(f'file_{file_path}')
                    emit('file_unwatched', {'file_path': file_path})
            
            @self.socketio.on('ping')
            def handle_ping(data):
                emit('pong', {'timestamp': time.time()})
            
        except ImportError:
            logger.warning("Flask-SocketIO not available, using fallback WebSocket")
            self.setup_fallback_websocket(app)
    
    def setup_fallback_websocket(self, app):
        """Настройка fallback WebSocket без Flask-SocketIO"""
        try:
            import websockets
            import threading
            
            class FallbackWebSocketHandler:
                def __init__(self, hmr_server):
                    self.hmr_server = hmr_server
                    self.clients = set()
                
                async def handle_websocket(self, websocket, path):
                    if path == '/ws/hmr':
                        await self.handle_hmr_connection(websocket)
                
                async def handle_hmr_connection(self, websocket):
                    client_id = self.hmr_server.generate_client_id()
                    self.clients.add(websocket)
                    
                    try:
                        async for message in websocket:
                            data = json.loads(message)
                            await self.handle_message(websocket, data)
                    except websockets.exceptions.ConnectionClosed:
                        pass
                    finally:
                        self.clients.discard(websocket)
                
                async def handle_message(self, websocket, data):
                    message_type = data.get('type')
                    
                    if message_type == 'register':
                        await websocket.send(json.dumps({
                            'type': 'registered',
                            'data': {'client_id': self.hmr_server.generate_client_id()}
                        }))
                    elif message_type == 'ping':
                        await websocket.send(json.dumps({
                            'type': 'pong',
                            'data': {'timestamp': time.time()}
                        }))
            
            self.fallback_handler = FallbackWebSocketHandler(self)
            
            # Запускаем WebSocket сервер в отдельном потоке
            def run_websocket_server():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                start_server = websockets.serve(
                    self.fallback_handler.handle_websocket,
                    "localhost",
                    8765
                )
                
                loop.run_until_complete(start_server)
                loop.run_forever()
            
            self.ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
            self.ws_thread.start()
            
        except ImportError:
            logger.error("WebSocket libraries not available")
    
    def start_file_watcher(self):
        """Запускает файловый наблюдатель"""
        if self.observer is None:
            self.observer = Observer()
            self.observer.schedule(
                self.file_watcher,
                path='.',
                recursive=True
            )
            self.observer.start()
            self.is_running = True
            logger.info("File watcher started")
    
    def stop_file_watcher(self):
        """Останавливает файловый наблюдатель"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("File watcher stopped")
    
    def notify_file_change(self, file_path: str, change_type: str):
        """Уведомляет клиентов об изменении файла"""
        try:
            # Читаем содержимое файла
            content = self.read_file_content(file_path)
            
            message = {
                'type': 'file-changed',
                'data': {
                    'filePath': file_path,
                    'changeType': change_type,
                    'content': content,
                    'timestamp': time.time()
                }
            }
            
            # Отправляем уведомление клиентам
            self.broadcast_message(message, f'file_{file_path}')
            
            logger.info(f"Notified clients about {change_type}: {file_path}")
            
        except Exception as e:
            logger.error(f"Error notifying file change: {e}")
    
    def read_file_content(self, file_path: str) -> str:
        """Читает содержимое файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    def broadcast_message(self, message: dict, room: str = None):
        """Отправляет сообщение всем клиентам или в комнату"""
        try:
            if hasattr(self, 'socketio'):
                if room:
                    self.socketio.emit('hmr_message', message, room=room)
                else:
                    self.socketio.emit('hmr_message', message)
            elif hasattr(self, 'fallback_handler'):
                # Fallback для простого WebSocket
                message_str = json.dumps(message)
                for client in self.fallback_handler.clients:
                    try:
                        asyncio.create_task(client.send(message_str))
                    except Exception as e:
                        logger.error(f"Error sending to client: {e}")
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    def generate_client_id(self) -> str:
        """Генерирует уникальный ID клиента"""
        import uuid
        return str(uuid.uuid4())
    
    def get_status(self) -> dict:
        """Возвращает статус HMR сервера"""
        return {
            'is_running': self.is_running,
            'clients_count': len(self.clients),
            'watched_files_count': len(self.file_watcher.watched_files),
            'uptime': time.time() - getattr(self, '_start_time', time.time())
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop_file_watcher()
        self.clients.clear()
        logger.info("HMR Server cleaned up")


# Глобальный экземпляр HMR сервера
hmr_server = HMRServer()


def init_hmr_server(app):
    """Инициализация HMR сервера для Flask приложения"""
    hmr_server.init_app(app)
    return hmr_server


def get_hmr_server():
    """Возвращает глобальный экземпляр HMR сервера"""
    return hmr_server 