"""
Virt-A-Mate Bridge
WebSocket server for bidirectional communication between VaM and the game backend
"""
import asyncio
import json
import logging
from typing import Dict, Optional, Callable, Any
from datetime import datetime

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    print("Warning: websockets not installed. Run: pip install websockets")
    websockets = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VaMBridge:
    """Bridge between Virt-A-Mate and the game backend"""

    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients: set = set()
        self.event_handlers: Dict[str, Callable] = {}
        self.game_state = None

    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type from VaM"""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered handler for event: {event_type}")

    def set_game_state(self, game_state):
        """Set reference to game state for synchronization"""
        self.game_state = game_state

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket connection from VaM"""
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"VaM client connected from {client_addr}")

        try:
            # Send initial game state
            if self.game_state:
                await self.send_full_state(websocket)

            # Listen for messages from VaM
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"VaM client disconnected: {client_addr}")
        finally:
            self.clients.remove(websocket)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Process message from VaM"""
        try:
            data = json.loads(message)
            event_type = data.get('type')

            logger.info(f"Received from VaM: {event_type}")

            # Call registered handler if exists
            if event_type in self.event_handlers:
                response = await self.event_handlers[event_type](data.get('data', {}))
                if response:
                    await self.send_to_vam(response, websocket)
            else:
                logger.warning(f"No handler registered for event: {event_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def send_to_vam(self, data: dict, websocket: Optional[WebSocketServerProtocol] = None):
        """Send message to VaM (specific client or broadcast)"""
        message = json.dumps(data)

        if websocket:
            # Send to specific client
            await websocket.send(message)
        else:
            # Broadcast to all connected clients
            if self.clients:
                await asyncio.gather(
                    *[client.send(message) for client in self.clients],
                    return_exceptions=True
                )

    async def send_full_state(self, websocket: WebSocketServerProtocol):
        """Send complete game state to VaM"""
        if not self.game_state:
            return

        # Character states
        characters_data = []
        for name, char in self.game_state.characters.items():
            characters_data.append({
                'name': name,
                'location': self.game_state.get_character_location(name) if hasattr(self.game_state, 'get_character_location') else 'home_living_room',
                'clothing': char.clothing,
                'emotional_state': char.emotional_state,
                'rapport': char.rapport,
                'active_phs_count': len(char.active_phs)
            })

        state_data = {
            'type': 'full_state',
            'data': {
                'game_time': self.game_state.game_time.to_dict() if hasattr(self.game_state, 'game_time') else {},
                'player_location': self.game_state.player.current_location,
                'characters': characters_data,
                'player_stats': {
                    'sp': self.game_state.player.suggestion_points,
                    'money': self.game_state.player.money
                }
            }
        }

        await self.send_to_vam(state_data, websocket)

    async def update_character_state(self, character_name: str, updates: dict):
        """Send character state update to VaM"""
        message = {
            'type': 'update_character',
            'data': {
                'character': character_name,
                **updates
            }
        }
        await self.send_to_vam(message)

    async def update_time(self, time_data: dict):
        """Update in-game time in VaM (affects lighting, schedules)"""
        message = {
            'type': 'update_time',
            'data': time_data
        }
        await self.send_to_vam(message)

    async def show_dialogue(self, character_name: str, text: str, duration: float = 5.0):
        """Display dialogue bubble in VaM"""
        message = {
            'type': 'show_dialogue',
            'data': {
                'character': character_name,
                'text': text,
                'duration': duration
            }
        }
        await self.send_to_vam(message)

    async def show_notification(self, text: str, notification_type: str = 'info'):
        """Show notification to player in VaM"""
        message = {
            'type': 'notification',
            'data': {
                'text': text,
                'type': notification_type,  # 'info', 'success', 'warning', 'error'
                'timestamp': datetime.now().isoformat()
            }
        }
        await self.send_to_vam(message)

    async def trigger_animation(self, character_name: str, animation: str):
        """Trigger character animation in VaM"""
        message = {
            'type': 'play_animation',
            'data': {
                'character': character_name,
                'animation': animation
            }
        }
        await self.send_to_vam(message)

    async def change_location(self, location: str):
        """Change to a different scene/location in VaM"""
        message = {
            'type': 'change_location',
            'data': {
                'location': location
            }
        }
        await self.send_to_vam(message)

    async def start_server(self):
        """Start the WebSocket server"""
        if not websockets:
            logger.error("websockets library not installed!")
            return

        logger.info(f"Starting VaM Bridge on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info("VaM Bridge ready. Waiting for connections...")
            await asyncio.Future()  # Run forever


# Event Handler Examples
# These would be called when VaM sends events

async def handle_click_character(data: dict) -> Optional[dict]:
    """Handle when player clicks on a character in VaM"""
    character_name = data.get('character')
    logger.info(f"Player clicked on {character_name}")

    # Return UI to show in VaM
    return {
        'type': 'show_menu',
        'data': {
            'title': f'Interact with {character_name}',
            'options': [
                {'id': 'talk', 'label': 'Talk'},
                {'id': 'observe', 'label': 'Observe'},
                {'id': 'hypnosis', 'label': 'Use Hypnosis'},
                {'id': 'cancel', 'label': 'Cancel'}
            ]
        }
    }


async def handle_click_object(data: dict) -> Optional[dict]:
    """Handle when player clicks on an object in VaM"""
    object_name = data.get('object')
    logger.info(f"Player clicked on {object_name}")

    # Object-specific menus
    if object_name == 'tv':
        return {
            'type': 'show_menu',
            'data': {
                'title': 'Television',
                'options': [
                    {'id': 'watch', 'label': 'Watch TV'},
                    {'id': 'turn_off', 'label': 'Turn Off'},
                    {'id': 'cancel', 'label': 'Cancel'}
                ]
            }
        }
    elif object_name == 'phone':
        return {
            'type': 'show_menu',
            'data': {
                'title': 'Phone',
                'options': [
                    {'id': 'check_messages', 'label': 'Check Messages'},
                    {'id': 'call', 'label': 'Make Call'},
                    {'id': 'cancel', 'label': 'Cancel'}
                ]
            }
        }
    elif object_name == 'book':
        return {
            'type': 'show_menu',
            'data': {
                'title': 'Hypnosis Book',
                'options': [
                    {'id': 'read', 'label': 'Read (30 min)'},
                    {'id': 'study', 'label': 'Study Technique'},
                    {'id': 'cancel', 'label': 'Cancel'}
                ]
            }
        }

    return None


async def handle_menu_selection(data: dict) -> Optional[dict]:
    """Handle when player selects a menu option in VaM"""
    selection = data.get('selection')
    context = data.get('context', {})

    logger.info(f"Player selected: {selection} with context: {context}")

    # This would trigger the actual game logic
    # For now, just acknowledge
    return {
        'type': 'notification',
        'data': {
            'text': f"Selected: {selection}",
            'type': 'info'
        }
    }


# Standalone server for testing
if __name__ == '__main__':
    bridge = VaMBridge()

    # Register handlers
    bridge.register_handler('click_character', handle_click_character)
    bridge.register_handler('click_object', handle_click_object)
    bridge.register_handler('menu_selection', handle_menu_selection)

    # Start server
    try:
        asyncio.run(bridge.start_server())
    except KeyboardInterrupt:
        logger.info("VaM Bridge shutting down...")
