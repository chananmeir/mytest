using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using SimpleJSON;
using WebSocketSharp;

namespace FamilyDynamicsRPG
{
    /// <summary>
    /// Virt-A-Mate plugin for Family Dynamics RPG
    /// Handles interactions and communicates with Python backend via WebSocket
    /// </summary>
    public class FamilyDynamicsPlugin : MVRScript
    {
        // WebSocket connection
        private WebSocket ws;
        private string serverUrl = "ws://localhost:8765";

        // UI Elements
        private UIDynamicButton btnConnect;
        private UIDynamicButton btnDisconnect;
        private UIDynamicTextField statusText;

        // Game State
        private Dictionary<string, Atom> characterAtoms = new Dictionary<string, Atom>();
        private Dictionary<string, Atom> interactableObjects = new Dictionary<string, Atom>();

        public override void Init()
        {
            try
            {
                // Create UI
                CreateUI();

                // Find all character atoms
                FindCharacterAtoms();

                // Find all interactable objects
                FindInteractableObjects();

                // Set up click detection
                SetupClickDetection();

                LogMessage("Family Dynamics RPG Plugin initialized!");
            }
            catch (Exception e)
            {
                SuperController.LogError($"Plugin Init Error: {e}");
            }
        }

        void CreateUI()
        {
            // Connection status
            statusText = CreateTextField(new JSONStorableString("status", "Not connected"));

            // Connect button
            btnConnect = CreateButton("Connect to Game Server");
            btnConnect.button.onClick.AddListener(ConnectToServer);

            // Disconnect button
            btnDisconnect = CreateButton("Disconnect");
            btnDisconnect.button.onClick.AddListener(DisconnectFromServer);
            btnDisconnect.button.interactable = false;

            // Server URL input
            JSONStorableString serverUrlParam = new JSONStorableString("serverUrl", serverUrl);
            CreateTextField(serverUrlParam);
            RegisterString(serverUrlParam);
        }

        void FindCharacterAtoms()
        {
            // Find atoms with specific names (Ruth, Tom, Melanie, etc.)
            string[] characterNames = { "Ruth", "Tom", "Melanie", "Dawn", "Vanessa", "Derek", "Karen" };

            foreach (string name in characterNames)
            {
                Atom atom = SuperController.singleton.GetAtomByUid(name);
                if (atom != null)
                {
                    characterAtoms[name] = atom;
                    LogMessage($"Found character: {name}");

                    // Add collider trigger for clicks
                    AddClickTrigger(atom, () => OnCharacterClicked(name));
                }
            }
        }

        void FindInteractableObjects()
        {
            // Find objects by name or tag
            string[] objectNames = { "TV", "Phone", "Book", "Coffee_Maker", "Couch", "Mirror" };

            foreach (string objName in objectNames)
            {
                Atom atom = SuperController.singleton.GetAtomByUid(objName);
                if (atom != null)
                {
                    interactableObjects[objName] = atom;
                    LogMessage($"Found object: {objName}");

                    // Add click trigger
                    AddClickTrigger(atom, () => OnObjectClicked(objName));
                }
            }
        }

        void SetupClickDetection()
        {
            // VaM uses raycasts for selection
            // We'll hook into the selection system
            StartCoroutine(MonitorSelection());
        }

        IEnumerator MonitorSelection()
        {
            Atom lastSelected = null;

            while (true)
            {
                // Check what user is looking at/selecting
                Atom currentSelected = SuperController.singleton.GetSelectedAtom();

                if (currentSelected != lastSelected && currentSelected != null)
                {
                    string atomName = currentSelected.name;

                    // Check if it's a character
                    if (characterAtoms.ContainsValue(currentSelected))
                    {
                        LogMessage($"Selected character: {atomName}");
                    }
                    // Check if it's an object
                    else if (interactableObjects.ContainsValue(currentSelected))
                    {
                        LogMessage($"Selected object: {atomName}");
                    }

                    lastSelected = currentSelected;
                }

                yield return new WaitForSeconds(0.1f);
            }
        }

        void AddClickTrigger(Atom atom, Action callback)
        {
            // In VaM, we can add triggers to atoms
            // This is simplified - actual implementation may vary
            // You might need to add colliders and use OnTriggerEnter
        }

        #region WebSocket Communication

        void ConnectToServer()
        {
            try
            {
                ws = new WebSocket(serverUrl);

                ws.OnOpen += (sender, e) =>
                {
                    LogMessage("Connected to game server!");
                    UpdateStatus("Connected");
                    btnConnect.button.interactable = false;
                    btnDisconnect.button.interactable = true;
                };

                ws.OnMessage += (sender, e) =>
                {
                    HandleServerMessage(e.Data);
                };

                ws.OnError += (sender, e) =>
                {
                    LogError($"WebSocket error: {e.Message}");
                    UpdateStatus($"Error: {e.Message}");
                };

                ws.OnClose += (sender, e) =>
                {
                    LogMessage("Disconnected from server");
                    UpdateStatus("Disconnected");
                    btnConnect.button.interactable = true;
                    btnDisconnect.button.interactable = false;
                };

                ws.Connect();
            }
            catch (Exception e)
            {
                LogError($"Connection failed: {e.Message}");
            }
        }

        void DisconnectFromServer()
        {
            if (ws != null && ws.IsAlive)
            {
                ws.Close();
            }
        }

        void SendToServer(JSONNode data)
        {
            if (ws != null && ws.IsAlive)
            {
                ws.Send(data.ToString());
            }
            else
            {
                LogError("Not connected to server!");
            }
        }

        void HandleServerMessage(string message)
        {
            try
            {
                JSONNode data = JSON.Parse(message);
                string messageType = data["type"];

                switch (messageType)
                {
                    case "update_character":
                        UpdateCharacter(data["data"]);
                        break;

                    case "show_dialogue":
                        ShowDialogue(data["data"]);
                        break;

                    case "show_menu":
                        ShowMenu(data["data"]);
                        break;

                    case "notification":
                        ShowNotification(data["data"]);
                        break;

                    case "update_time":
                        UpdateTime(data["data"]);
                        break;

                    case "play_animation":
                        PlayAnimation(data["data"]);
                        break;

                    case "change_location":
                        ChangeLocation(data["data"]);
                        break;

                    default:
                        LogMessage($"Unknown message type: {messageType}");
                        break;
                }
            }
            catch (Exception e)
            {
                LogError($"Error handling message: {e.Message}");
            }
        }

        #endregion

        #region Event Handlers

        void OnCharacterClicked(string characterName)
        {
            LogMessage($"Clicked on character: {characterName}");

            JSONNode message = new JSONObject();
            message["type"] = "click_character";
            message["data"]["character"] = characterName;

            SendToServer(message);
        }

        void OnObjectClicked(string objectName)
        {
            LogMessage($"Clicked on object: {objectName}");

            JSONNode message = new JSONObject();
            message["type"] = "click_object";
            message["data"]["object"] = objectName;

            SendToServer(message);
        }

        #endregion

        #region Game State Updates

        void UpdateCharacter(JSONNode data)
        {
            string characterName = data["character"];

            if (!characterAtoms.ContainsKey(characterName))
                return;

            Atom characterAtom = characterAtoms[characterName];

            // Update emotional state (facial expression)
            if (data["emotional_state"] != null)
            {
                string emotionalState = data["emotional_state"];
                SetCharacterExpression(characterAtom, emotionalState);
            }

            // Update clothing
            if (data["clothing"] != null)
            {
                // This would change the character's outfit
                // Implementation depends on your clothing system
            }

            // Update location
            if (data["location"] != null)
            {
                string location = data["location"];
                MoveCharacterToLocation(characterAtom, location);
            }
        }

        void ShowDialogue(JSONNode data)
        {
            string characterName = data["character"];
            string text = data["text"];
            float duration = data["duration"].AsFloat;

            // Create floating text bubble above character
            // This would use VaM's UI system or a custom prefab
            LogMessage($"{characterName}: {text}");
        }

        void ShowMenu(JSONNode data)
        {
            string title = data["title"];
            JSONArray options = data["options"].AsArray;

            // Create UI menu with options
            // When player selects, send back to server
            LogMessage($"Showing menu: {title}");
        }

        void ShowNotification(JSONNode data)
        {
            string text = data["text"];
            string type = data["type"];

            // Show notification overlay
            LogMessage($"[{type.ToUpper()}] {text}");
        }

        void UpdateTime(JSONNode data)
        {
            int hour = data["hour"].AsInt;
            int minute = data["minute"].AsInt;
            string period = data["period"];

            // Update scene lighting based on time
            UpdateLighting(hour);

            LogMessage($"Time updated: {hour}:{minute:00} {period}");
        }

        void PlayAnimation(JSONNode data)
        {
            string characterName = data["character"];
            string animationName = data["animation"];

            if (characterAtoms.ContainsKey(characterName))
            {
                // Trigger animation on character
                // This would use VaM's animation system
                LogMessage($"Playing animation '{animationName}' on {characterName}");
            }
        }

        void ChangeLocation(JSONNode data)
        {
            string location = data["location"];

            // Load different scene/location
            LogMessage($"Changing to location: {location}");
        }

        #endregion

        #region Helper Methods

        void SetCharacterExpression(Atom character, string emotionalState)
        {
            // Map emotional states to facial morphs
            // This is simplified - you'd use VaM's morph system

            Dictionary<string, string> expressionMap = new Dictionary<string, string>
            {
                { "happy", "Smile" },
                { "sad", "Frown" },
                { "angry", "Anger" },
                { "curious", "Interest" },
                { "neutral", "Default" },
                { "embarrassed", "Blush" },
                { "aroused", "Pleasure" },
                { "anxious", "Fear" },
            };

            if (expressionMap.ContainsKey(emotionalState))
            {
                string morphName = expressionMap[emotionalState];
                // Apply morph to character face
            }
        }

        void MoveCharacterToLocation(Atom character, string location)
        {
            // Move character to predefined position based on location
            // You'd have spawn points set up in each scene
        }

        void UpdateLighting(int hour)
        {
            // Adjust scene lighting based on time of day
            // Morning (6-12): Bright, warm
            // Afternoon (12-18): Bright, neutral
            // Evening (18-21): Dim, warm
            // Night (21-6): Very dim, cool
        }

        void UpdateStatus(string status)
        {
            if (statusText != null)
            {
                statusText.text = $"Status: {status}";
            }
        }

        void LogMessage(string message)
        {
            SuperController.LogMessage($"[Family Dynamics] {message}");
        }

        void LogError(string message)
        {
            SuperController.LogError($"[Family Dynamics] {message}");
        }

        #endregion

        void OnDestroy()
        {
            if (ws != null && ws.IsAlive)
            {
                ws.Close();
            }
        }
    }
}
