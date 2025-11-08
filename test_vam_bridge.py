#!/usr/bin/env python3
"""
Test script for VaM Bridge WebSocket connection
Tests the communication between Python backend and simulated VaM client
"""
import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("ERROR: websockets not installed!")
    print("Run: pip install websockets")
    sys.exit(1)

from systems.vam_bridge import VaMBridge


# Simulated VaM client for testing
async def test_vam_client():
    """Simulate a Virt-A-Mate client connecting to the bridge"""
    uri = "ws://localhost:8765"

    print("\n[VaM Client] Attempting to connect to bridge...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[VaM Client] Connected!")

            # Test 1: Send character click
            print("\n=== Test 1: Click on Ruth ===")
            message = {
                "type": "click_character",
                "data": {
                    "character": "Ruth",
                    "player_position": {"x": 1.5, "y": 0, "z": 2.0}
                }
            }
            await websocket.send(json.dumps(message))
            print(f"[VaM Client] Sent: {message}")

            # Wait for response
            response = await websocket.recv()
            print(f"[VaM Client] Received: {response}")

            # Wait a bit
            await asyncio.sleep(1)

            # Test 2: Send object click
            print("\n=== Test 2: Click on TV ===")
            message = {
                "type": "click_object",
                "data": {
                    "object": "tv"
                }
            }
            await websocket.send(json.dumps(message))
            print(f"[VaM Client] Sent: {message}")

            response = await websocket.recv()
            print(f"[VaM Client] Received: {response}")

            await asyncio.sleep(1)

            # Test 3: Send menu selection
            print("\n=== Test 3: Select menu option ===")
            message = {
                "type": "menu_selection",
                "data": {
                    "selection": "talk",
                    "context": {"character": "Ruth"}
                }
            }
            await websocket.send(json.dumps(message))
            print(f"[VaM Client] Sent: {message}")

            response = await websocket.recv()
            print(f"[VaM Client] Received: {response}")

            print("\n[VaM Client] Tests completed successfully!")

    except ConnectionRefusedError:
        print("[VaM Client] ERROR: Could not connect to bridge!")
        print("             Make sure the bridge server is running.")
    except Exception as e:
        print(f"[VaM Client] ERROR: {e}")


async def test_bridge_server():
    """Run the bridge server and test it"""
    print("="*60)
    print("VaM Bridge Test")
    print("="*60)

    # Create bridge instance
    bridge = VaMBridge()

    # Register test handlers
    async def test_click_character(data):
        char_name = data.get('character')
        print(f"[Bridge] Handler called: Character '{char_name}' clicked")
        return {
            'type': 'show_menu',
            'data': {
                'title': f'Interact with {char_name}',
                'options': [
                    {'id': 'talk', 'label': 'Talk'},
                    {'id': 'observe', 'label': 'Observe'}
                ]
            }
        }

    async def test_click_object(data):
        obj_name = data.get('object')
        print(f"[Bridge] Handler called: Object '{obj_name}' clicked")
        return {
            'type': 'show_menu',
            'data': {
                'title': obj_name.upper(),
                'options': [
                    {'id': 'use', 'label': 'Use'}
                ]
            }
        }

    async def test_menu_selection(data):
        selection = data.get('selection')
        print(f"[Bridge] Handler called: Menu option '{selection}' selected")
        return {
            'type': 'notification',
            'data': {
                'text': f"You selected: {selection}",
                'type': 'info'
            }
        }

    bridge.register_handler('click_character', test_click_character)
    bridge.register_handler('click_object', test_click_object)
    bridge.register_handler('menu_selection', test_menu_selection)

    print("\n[Bridge] Starting server on localhost:8765...")
    print("[Bridge] Waiting for VaM client to connect...\n")

    # Start server in background
    server_task = asyncio.create_task(
        websockets.serve(bridge.handle_client, bridge.host, bridge.port)
    )

    # Give server time to start
    await asyncio.sleep(0.5)

    # Run test client
    await test_vam_client()

    # Clean up
    server_task.cancel()

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


async def manual_bridge_server():
    """Run bridge server manually (no automated tests)"""
    print("="*60)
    print("VaM Bridge Server - Manual Testing Mode")
    print("="*60)

    bridge = VaMBridge()

    # Register handlers
    from systems.vam_bridge import (
        handle_click_character,
        handle_click_object,
        handle_menu_selection
    )

    bridge.register_handler('click_character', handle_click_character)
    bridge.register_handler('click_object', handle_click_object)
    bridge.register_handler('menu_selection', handle_menu_selection)

    print("\nServer ready!")
    print("Connect your VaM plugin to: ws://localhost:8765")
    print("\nPress Ctrl+C to stop\n")

    try:
        await bridge.start_server()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        # Run manual server mode
        asyncio.run(manual_bridge_server())
    else:
        # Run automated tests
        try:
            asyncio.run(test_bridge_server())
        except KeyboardInterrupt:
            print("\n\nTest interrupted.")
