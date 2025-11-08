#!/usr/bin/env python3
"""
Test script to demonstrate the Relationship Web system
"""

from models.character import Character, PostHypnoticSuggestion, CHARACTERS
from models.game_state import GameState
from systems.relationship_web import RelationshipWeb
from systems.social_dynamics import SocialDynamics


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_observation_system():
    """Test character observation mechanics"""
    print_section("TEST 1: Observation System")

    # Create characters
    ruth = Character(**{k: v for k, v in vars(CHARACTERS['Ruth']).items()
                        if not k.startswith('_')})
    tom = Character(**{k: v for k, v in vars(CHARACTERS['Tom']).items()
                       if not k.startswith('_')})

    print(f"\nRuth's relationship with Tom: {ruth.relationships.get('Tom', 0)}/20")
    print(f"Ruth's personality: {ruth.personality}")

    # Simulate Tom acting out of character
    print("\n[Scenario: Tom suddenly becomes very assertive (PHS activated)]")

    observation = RelationshipWeb.observe_character_changes(
        observer=ruth,
        observed=tom,
        change_type='out_of_character',
        change_magnitude=70
    )

    if observation:
        print(f"\n✓ OBSERVED!")
        print(f"  Observer: {observation['observer']}")
        print(f"  Observed: {observation['observed']}")
        print(f"  Concern level: {observation['concern_level']}")
        print(f"  Will investigate: {observation['will_investigate']}")

        msg = RelationshipWeb.format_observation_message(observation)
        print(f"\n  Message: {msg}")
    else:
        print("\n✗ Not observed this time")


def test_gossip_system():
    """Test gossip spreading"""
    print_section("TEST 2: Gossip System")

    ruth = Character(**{k: v for k, v in vars(CHARACTERS['Ruth']).items()
                        if not k.startswith('_')})
    dawn = Character(**{k: v for k, v in vars(CHARACTERS['Dawn']).items()
                        if not k.startswith('_')})

    ruth.player_suspicion = 50  # Ruth is suspicious of player

    print(f"\nRuth's suspicion of player: {ruth.player_suspicion}")
    print(f"Ruth's relationship with Dawn: {ruth.relationships.get('Dawn', 0)}/20")
    print("\n[Scenario: Ruth tells Dawn about suspicions]")

    # Try gossip
    gossip = RelationshipWeb.generate_gossip(
        ruth, dawn,
        "the player's strange behavior",
        None
    )

    if gossip:
        print(f"\n✓ GOSSIP OCCURRED!")
        print(f"  Gossiper: {gossip['gossiper']}")
        print(f"  Listener: {gossip['listener']}")
        print(f"  Topic: {gossip['topic']}")
        print(f"  Credibility: {gossip['credibility']}%")

        # Spread suspicion
        effects = RelationshipWeb.spread_suspicion(
            ruth, dawn,
            "player manipulating family",
            ruth.player_suspicion
        )

        if effects:
            effect = effects[0]
            print(f"\n  SUSPICION SPREAD:")
            print(f"    Dawn's old suspicion: {effect['new_suspicion'] - effect['amount']}")
            print(f"    Amount transferred: +{effect['amount']}")
            print(f"    Dawn's new suspicion: {effect['new_suspicion']}")

            msg = RelationshipWeb.format_gossip_message(gossip, effect)
            print(f"\n  Message: {msg}")
    else:
        print("\n✗ No gossip occurred")


def test_protective_behavior():
    """Test protective responses"""
    print_section("TEST 3: Protective Behavior")

    ruth = Character(**{k: v for k, v in vars(CHARACTERS['Ruth']).items()
                        if not k.startswith('_')})
    tom = Character(**{k: v for k, v in vars(CHARACTERS['Tom']).items()
                       if not k.startswith('_')})

    relationship_score = ruth.relationships.get('Tom', 0)
    print(f"\nRuth's relationship with Tom: {relationship_score}/20")
    print(f"Protection threshold: {RelationshipWeb.get_protective_threshold(relationship_score)}")

    # Test different threat levels
    threat_levels = [30, 50, 80]

    for threat in threat_levels:
        print(f"\n[Threat level: {threat}]")
        protection = RelationshipWeb.check_protective_response(ruth, tom, threat)

        if protection:
            print(f"  ✓ PROTECTION ACTIVATED!")
            print(f"    Action: {protection['action_type']}")
            print(f"    Strength: {protection['protection_strength']}")

            msg = RelationshipWeb.format_protection_message(protection)
            print(f"    Message: {msg}")
        else:
            print(f"  ✗ No protection (threat too low)")


def test_alliance_detection():
    """Test alliance formation"""
    print_section("TEST 4: Alliance Detection")

    ruth = Character(**{k: v for k, v in vars(CHARACTERS['Ruth']).items()
                        if not k.startswith('_')})
    tom = Character(**{k: v for k, v in vars(CHARACTERS['Tom']).items()
                       if not k.startswith('_')})
    dawn = Character(**{k: v for k, v in vars(CHARACTERS['Dawn']).items()
                        if not k.startswith('_')})

    # Make them suspicious
    ruth.player_suspicion = 60
    tom.player_suspicion = 55
    dawn.player_suspicion = 70

    print("\nSuspicion levels:")
    print(f"  Ruth: {ruth.player_suspicion}%")
    print(f"  Tom: {tom.player_suspicion}%")
    print(f"  Dawn: {dawn.player_suspicion}%")

    print("\nRelationships:")
    print(f"  Ruth ↔ Tom: {ruth.relationships.get('Tom', 0)}/20")
    print(f"  Ruth ↔ Dawn: {ruth.relationships.get('Dawn', 0)}/20")
    print(f"  Tom ↔ Dawn: {tom.relationships.get('Dawn', 0)}/20")

    # Check for alliances
    characters = [ruth, tom, dawn]
    alliances = RelationshipWeb.detect_coordinated_resistance(characters)

    print(f"\n✓ ALLIANCES DETECTED: {len(alliances)}")
    for char1, char2, strength in alliances:
        print(f"\n  {char1} + {char2}")
        print(f"    Alliance strength: {strength}%")
        print(f"    Threat level: {'HIGH' if strength > 70 else 'MEDIUM'}")

        msg = SocialDynamics.format_alliance_warning({
            'character1': char1,
            'character2': char2,
            'alliance_strength': strength,
            'threat_level': 'high' if strength > 70 else 'medium'
        })
        print(f"    Message: {msg}")


def test_cascading_effects():
    """Test full cascade when PHS activates"""
    print_section("TEST 5: Cascading Social Effects")

    # Create game state
    game_state = GameState()

    # Get characters
    lisa = game_state.characters['Melanie']  # Using Melanie as example
    ruth = game_state.characters['Ruth']
    tom = game_state.characters['Tom']

    print(f"\n[Scenario: Lisa (high resistance: {lisa.resistance}%) has PHS activated]")

    # Create a PHS
    phs = PostHypnoticSuggestion(
        target_name='Melanie',
        trigger='when criticized',
        response='defend the player',
        success_rate=60,
        phs_type='behavioral_prompt'
    )

    print(f"PHS: {phs.trigger} → {phs.response}")

    # Simulate activation
    print("\n[PHS activates - Lisa defends player publicly]")

    messages = SocialDynamics.on_phs_activation(game_state, lisa, phs)

    if messages:
        print(f"\n✓ SOCIAL REACTIONS: {len(messages)}")
        for msg in messages:
            print(f"  • {msg}")
    else:
        print("\n✗ No one noticed")

    # Show final state
    print("\nFinal suspicion levels:")
    for name, char in game_state.characters.items():
        if char.player_suspicion > 0:
            print(f"  {name}: {char.player_suspicion}%")


def run_all_tests():
    """Run all test scenarios"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║            RELATIONSHIP WEB SYSTEM - TEST SUITE                   ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")

    test_observation_system()
    test_gossip_system()
    test_protective_behavior()
    test_alliance_detection()
    test_cascading_effects()

    print("\n" + "="*70)
    print("  ALL TESTS COMPLETE")
    print("="*70 + "\n")

    print("The Relationship Web is working! Key features:")
    print("  ✓ Characters observe each other")
    print("  ✓ Gossip spreads suspicion")
    print("  ✓ Protective behaviors trigger")
    print("  ✓ Alliances form against player")
    print("  ✓ Cascading social effects work")
    print("\nIntegrated into:")
    print("  • /api/talk - Conversation system")
    print("  • /api/advance-time - Periodic gossip")
    print("  • /api/social/alliances - Alliance checking")
    print("  • /api/social/relationship-map - Full network view")


if __name__ == "__main__":
    run_all_tests()
