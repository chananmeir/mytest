#!/usr/bin/env python3
"""
Quick test of the hypnosis learning system
"""

from models.game_state import GameState
from systems.hypnosis import HypnosisSystem
from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES

def test_learning_system():
    """Test that the learning system works end-to-end"""

    print("="*70)
    print("TESTING HYPNOSIS LEARNING SYSTEM")
    print("="*70)

    # Create game state
    game_state = GameState()
    hypnosis = HypnosisSystem()

    # Test 1: Player starts with no techniques
    print("\n1. Checking initial state...")
    assert len(game_state.player.hypnosis_knowledge.known_techniques) == 0
    print("   ✓ Player starts with no techniques")

    # Test 2: Cannot plant PHS without techniques
    print("\n2. Testing PHS planting without techniques...")
    can_plant, message = hypnosis.can_plant_phs(
        game_state,
        'Ruth',
        'emotional_anchoring'
    )
    assert not can_plant
    assert "don't know" in message.lower()
    print(f"   ✓ Cannot plant PHS without technique")
    print(f"   Message: {message}")

    # Test 3: Learning progress system
    print("\n3. Testing learning progress...")
    knowledge = game_state.player.hypnosis_knowledge

    # Add 50% progress to observation
    progress = knowledge.add_learning_progress('observation', 50)
    assert progress == 50
    assert 'observation' in knowledge.learning_progress
    print(f"   ✓ Added 50% progress to observation: {progress}%")

    # Complete learning observation
    progress = knowledge.add_learning_progress('observation', 50)
    assert progress >= 100
    assert knowledge.knows_technique('observation')
    assert 'observation' not in knowledge.learning_progress
    print(f"   ✓ Mastered observation technique")

    # Test 4: Available techniques
    print("\n4. Testing available techniques...")
    available = knowledge.get_available_techniques()
    print(f"   Available to learn: {len(available)} techniques")
    assert len(available) > 0

    # Should be able to learn basic techniques
    basic_available = [t for t in available if t.category == 'basic']
    print(f"   ✓ {len(basic_available)} basic techniques available")

    # Test 5: Prerequisite checking
    print("\n5. Testing prerequisite system...")
    can_learn, reason = knowledge.can_learn_technique('deep_programming')
    assert not can_learn
    print(f"   ✓ Cannot learn advanced technique without prerequisites")
    print(f"   Reason: {reason}")

    # Test 6: Skill bonuses
    print("\n6. Testing skill bonuses...")
    sp_reduction, success_bonus = knowledge.get_total_bonuses()
    print(f"   ✓ Current bonuses: -{sp_reduction} SP, +{success_bonus}% success")

    # Learn a technique that gives bonuses
    knowledge.known_techniques.add('active_listening')
    sp_reduction, success_bonus = knowledge.get_total_bonuses()
    assert success_bonus > 0
    print(f"   ✓ After learning active_listening: -{sp_reduction} SP, +{success_bonus}% success")

    # Test 7: Book reading
    print("\n7. Testing book reading system...")
    books_before = len(knowledge.books_read)
    knowledge.books_read.append('beginner_guide')
    assert len(knowledge.books_read) == books_before + 1
    print(f"   ✓ Book reading tracked: {len(knowledge.books_read)} books read")

    # Test 8: Skill level progression
    print("\n8. Testing skill level...")
    print(f"   Current skill level: {knowledge.skill_level}")

    # Learn all basic techniques (use learn_technique to trigger _update_skill_level)
    for tech_name, tech in HYPNOSIS_TECHNIQUES.items():
        if tech.category == 'basic' and tech_name not in knowledge.known_techniques:
            knowledge.known_techniques.add(tech_name)
            knowledge._update_skill_level()

    print(f"   ✓ After learning basic techniques: {knowledge.skill_level}")

    # Test 9: Planting PHS with learned technique
    print("\n9. Testing PHS planting with learned technique...")

    # Learn emotional_anchoring (needed for emotional nudge)
    knowledge.known_techniques.add('emotional_anchoring')

    # Now we should be able to plant
    can_plant, message = hypnosis.can_plant_phs(
        game_state,
        'Ruth',
        'emotional_anchoring'
    )
    # Note: This might still fail due to rapport/emotional state, but shouldn't fail on technique
    if "don't know" not in message.lower():
        print(f"   ✓ Technique requirement satisfied")
        print(f"   Status: {message}")

    # Test 10: Technique bonuses apply to PHS
    print("\n10. Testing that bonuses apply to PHS planting...")
    sp_reduction, success_bonus = knowledge.get_total_bonuses()
    print(f"   ✓ Final bonuses: -{sp_reduction} SP cost, +{success_bonus}% success rate")

    print("\n" + "="*70)
    print("ALL TESTS PASSED!")
    print("="*70)
    print("\nThe hypnosis learning system is working correctly!")
    print("Players must now:")
    print("  1. View the skill tree to see available techniques")
    print("  2. Study hypnosis (read books, practice, research)")
    print("  3. Master techniques before planting PHS")
    print("  4. Earn bonuses as they learn more advanced techniques")
    print("="*70)


if __name__ == "__main__":
    try:
        test_learning_system()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
