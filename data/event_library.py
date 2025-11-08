"""
Event Library - Collection of Dynamic Random Events
"""
from systems.dynamic_events import DynamicEvent, EventOption


# ====== ENCOUNTER EVENTS ======

COFFEE_SPILL = DynamicEvent(
    event_id="encounter_coffee_spill_ruth",
    event_type="encounter",
    title="The Coffee Spill",
    description="You accidentally bump into Ruth while carrying coffee, spilling it on her blouse!",
    icon="☕",
    primary_character="Ruth",
    observers=["Dawn", "Tom"],
    duration_minutes=5,
    weight=15,
    options=[
        EventOption(
            option_id="apologize",
            text="Apologize profusely and offer to pay for dry cleaning",
            rapport_changes={"Ruth": 2},
            social_effect="Others see you're considerate and responsible",
            observers=["Dawn", "Tom"],
            success_text="Ruth smiles. 'Don't worry about it, accidents happen.' Dawn nods approvingly."
        ),
        EventOption(
            option_id="manipulate",
            text="Use this flustered moment to plant a subtle suggestion",
            sp_cost=3,
            allows_phs=True,
            phs_target="Ruth",
            phs_success_bonus=15,
            phs_detection_risk=40,
            social_effect="Dawn is watching closely...",
            observers=["Dawn"],
            success_text="In her flustered state, Ruth is very receptive...",
            failure_text="Dawn interrupts: 'Let me help Ruth clean up.'"
        ),
        EventOption(
            option_id="blame",
            text="'You should watch where you're going!'",
            rapport_changes={"Ruth": -3, "Dawn": -2},
            suspicion_changes={"Dawn": 5},
            social_effect="Dawn witnesses your rudeness and disapproves",
            observers=["Dawn", "Tom"],
            success_text="Ruth looks hurt. Dawn frowns at you."
        )
    ]
)

OVERHEARD_ARGUMENT = DynamicEvent(
    event_id="encounter_overheard_gossip",
    event_type="encounter",
    title="Overheard Gossip",
    description="You overhear Vanessa and Karen talking about you in the next room...",
    icon="👂",
    primary_character="Vanessa",
    secondary_characters=["Karen"],
    min_suspicion={"Vanessa": 20},
    weight=12,
    urgency_level="high",
    options=[
        EventOption(
            option_id="eavesdrop",
            text="Stay quiet and listen (gain SP from observation)",
            sp_gain=2,
            time_cost=10,
            success_text="You learn valuable information about how they perceive you."
        ),
        EventOption(
            option_id="confront",
            text="Walk in and confront them directly",
            requires_rapport=8,
            rapport_changes={"Vanessa": -1, "Karen": -1},
            suspicion_changes={"Vanessa": -5, "Karen": -5},
            success_text="Your directness catches them off guard. They respect it.",
            failure_text="They deflect and become defensive."
        ),
        EventOption(
            option_id="ignore",
            text="Walk away and pretend you didn't hear",
            success_text="Sometimes ignorance is bliss..."
        )
    ]
)

# ====== CHARACTER-INITIATED EVENTS ======

TOM_WORK_CRISIS = DynamicEvent(
    event_id="initiated_tom_work_crisis",
    event_type="initiated",
    title="Tom's Work Problems",
    description="Tom pulls you aside. 'Can we talk? I'm having real trouble at work...'",
    icon="😰",
    primary_character="Tom",
    min_rapport={"Tom": 5},
    required_emotional_states={"Tom": ["stressed", "vulnerable", "anxious"]},
    duration_minutes=30,
    weight=20,
    cooldown_hours=48,
    options=[
        EventOption(
            option_id="listen_empathetically",
            text="Listen with genuine empathy and support",
            rapport_changes={"Tom": 3},
            emotional_state_changes={"Tom": "relieved"},
            social_effect="Ruth notices you being supportive of Tom",
            observers=["Ruth"],
            time_cost=30,
            success_text="Tom opens up completely. 'Thanks... I really needed this.'"
        ),
        EventOption(
            option_id="plant_phs",
            text="Plant PHS: 'When stressed at work, you trust my advice'",
            sp_cost=4,
            allows_phs=True,
            phs_target="Tom",
            phs_success_bonus=25,  # He's vulnerable
            phs_detection_risk=30,
            success_text="Tom nods along, absorbing your words deeply..."
        ),
        EventOption(
            option_id="dismiss",
            text="'Just deal with it, Tom. Everyone has problems.'",
            rapport_changes={"Tom": -4},
            suspicion_changes={"Ruth": 10},
            social_effect="Ruth overhears and is disappointed in you",
            observers=["Ruth"],
            success_text="Tom's face falls. Ruth looks at you disapprovingly."
        )
    ]
)

MELANIE_ADVICE = DynamicEvent(
    event_id="initiated_melanie_seeks_advice",
    event_type="initiated",
    title="Melanie Needs Advice",
    description="Surprisingly, Melanie approaches you. 'I hate asking... but I need an outside perspective.'",
    icon="🤔",
    primary_character="Melanie",
    min_rapport={"Melanie": 10},  # Unusual for proud Melanie
    weight=8,  # Rare event
    one_time=True,
    options=[
        EventOption(
            option_id="help_genuinely",
            text="Give thoughtful, genuine advice",
            rapport_changes={"Melanie": 4},
            suspicion_changes={"Melanie": -10},
            success_text="Melanie actually smiles. 'Thank you. That... actually helps.'"
        ),
        EventOption(
            option_id="exploit",
            text="Give advice that benefits your manipulation goals",
            sp_cost=3,
            suspicion_changes={"Melanie": 15},
            success_chance=60,
            success_text="She follows your advice, though she seems uncertain...",
            failure_text="Melanie's sharp. 'Wait... that doesn't make sense. What are you up to?'"
        )
    ]
)

# ====== OPPORTUNITY WINDOWS ======

DAWN_ALONE_KITCHEN = DynamicEvent(
    event_id="opportunity_dawn_alone",
    event_type="opportunity",
    title="Dawn Alone in Kitchen",
    description="Dawn is alone in the kitchen for the next 10 minutes. This is rare!",
    icon="⏰",
    primary_character="Dawn",
    required_location="kitchen",
    window_expires_in=10,
    weight=12,
    urgency_level="high",
    options=[
        EventOption(
            option_id="build_rapport",
            text="Have a genuine heart-to-heart conversation",
            rapport_changes={"Dawn": 4},  # 2x normal
            time_cost=10,
            success_text="Dawn appreciates the private conversation. 'You're a good listener.'"
        ),
        EventOption(
            option_id="plant_phs_stealth",
            text="Plant PHS with no witnesses around",
            sp_cost=5,
            allows_phs=True,
            phs_target="Dawn",
            phs_success_bonus=20,
            phs_detection_risk=15,  # Low risk, no witnesses
            success_text="With no one watching, you work subtly and effectively..."
        )
    ]
)

VULNERABLE_MOMENT = DynamicEvent(
    event_id="opportunity_vulnerable_vanessa",
    event_type="opportunity",
    title="Vanessa's Vulnerable Moment",
    description="Vanessa just got bad news about a work deal. She's uncharacteristically open right now.",
    icon="💔",
    primary_character="Vanessa",
    required_emotional_states={"Vanessa": ["vulnerable", "sad"]},
    window_expires_in=15,
    weight=10,
    urgency_level="high",
    pressure=True,
    options=[
        EventOption(
            option_id="comfort",
            text="Offer genuine comfort and support",
            rapport_changes={"Vanessa": 5},
            emotional_state_changes={"Vanessa": "grateful"},
            success_text="Vanessa's walls come down. 'I don't usually show this side...'"
        ),
        EventOption(
            option_id="exploit_vulnerability",
            text="Use this vulnerability to plant deep suggestions",
            sp_cost=6,
            allows_phs=True,
            phs_target="Vanessa",
            phs_success_bonus=35,  # Very vulnerable
            phs_detection_risk=50,
            suspicion_changes={"Vanessa": 20},  # High risk of backlash
            success_chance=70,
            success_text="You strike while she's vulnerable. It works...",
            failure_text="Vanessa snaps out of it. 'Wait, what are you doing?'"
        )
    ]
)

# ====== CRISIS EVENTS ======

FAMILY_ARGUMENT = DynamicEvent(
    event_id="crisis_ruth_melanie_fight",
    event_type="crisis",
    title="Family Argument Erupts",
    description="Ruth and Melanie are having a heated argument! Everyone is watching.",
    icon="🔥",
    primary_character="Ruth",
    secondary_characters=["Melanie"],
    observers=["Tom", "Dawn", "Derek"],
    min_suspicion={"Ruth": 20, "Melanie": 20},  # Tension required
    weight=10,
    urgency_level="critical",
    pressure=True,
    options=[
        EventOption(
            option_id="side_ruth",
            text="Take Ruth's side in the argument",
            rapport_changes={"Ruth": 3, "Melanie": -3},
            suspicion_changes={"Melanie": 10},
            social_effect="Melanie remembers this betrayal",
            observers=["Tom", "Dawn", "Derek"],
            success_text="Ruth feels supported, but Melanie glares at you."
        ),
        EventOption(
            option_id="mediate",
            text="Try to mediate and calm everyone down",
            sp_cost=2,
            rapport_changes={"Ruth": 1, "Melanie": 1, "Dawn": 3},
            emotional_state_changes={"Ruth": "neutral", "Melanie": "neutral"},
            social_effect="Dawn approves of your maturity and wisdom",
            observers=["Tom", "Dawn", "Derek"],
            success_chance=70,
            success_text="You successfully de-escalate. Dawn nods approvingly.",
            failure_text="They both turn on you. 'Stay out of this!'"
        ),
        EventOption(
            option_id="manipulate_both",
            text="Plant PHS on both: 'When you argue, you feel foolish'",
            sp_cost=8,
            allows_phs=True,
            phs_detection_risk=80,  # Very risky, everyone watching
            suspicion_changes={"Dawn": 15, "Tom": 10},
            success_chance=40,
            success_text="Incredibly risky... but it works. They both calm down, confused...",
            failure_text="Dawn sees through it. 'What are you saying to them?!'"
        ),
        EventOption(
            option_id="observe",
            text="Stay silent and observe (learn from their dynamics)",
            sp_gain=2,
            rapport_changes={"Ruth": -1, "Melanie": -1},
            social_effect="They notice your detachment",
            success_text="You learn a lot about their relationship... but they noticed you didn't help."
        )
    ]
)

DEREK_MEDICAL_EMERGENCY = DynamicEvent(
    event_id="crisis_derek_injury",
    event_type="crisis",
    title="Derek's Gym Injury",
    description="Derek hurt himself at the gym badly. He needs help NOW.",
    icon="🚑",
    primary_character="Derek",
    weight=8,
    urgency_level="critical",
    pressure=True,
    duration_minutes=45,
    options=[
        EventOption(
            option_id="help_immediately",
            text="Drop everything and help him",
            rapport_changes={"Derek": 5},
            emotional_state_changes={"Derek": "grateful"},
            social_effect="Everyone sees you stepped up in a crisis",
            observers=["Melanie", "Ruth", "Tom"],
            time_cost=45,
            success_text="Derek: 'Thanks, man... I won't forget this.'"
        ),
        EventOption(
            option_id="get_melanie",
            text="Get Melanie (she's a nurse)",
            rapport_changes={"Melanie": 2, "Derek": 1},
            social_effect="Smart decision - you involved the professional",
            observers=["Melanie"],
            success_text="Melanie handles it expertly. She respects your judgment."
        )
    ]
)

# ====== SURPRISE VISITOR EVENTS ======

RUTH_UNEXPECTED_VISIT = DynamicEvent(
    event_id="visitor_ruth_suspicious",
    event_type="visitor",
    title="Ruth's Unexpected Visit",
    description="Ruth shows up at your door unannounced. She looks concerned.",
    icon="🚪",
    primary_character="Ruth",
    min_suspicion={"Ruth": 40},
    weight=12,
    pressure=True,
    options=[
        EventOption(
            option_id="be_honest",
            text="Invite her in and be completely honest",
            rapport_changes={"Ruth": 3},
            suspicion_changes={"Ruth": -15},
            success_text="Ruth: 'Thank you for being straight with me.'"
        ),
        EventOption(
            option_id="deflect",
            text="Deflect and change the subject",
            requires_rapport=10,
            suspicion_changes={"Ruth": 10},
            success_chance=60,
            success_text="You smoothly redirect the conversation...",
            failure_text="Ruth isn't buying it. 'Don't dodge my questions.'"
        ),
        EventOption(
            option_id="use_phs",
            text="Trigger existing PHS to make her forget why she came",
            sp_cost=5,
            phs_detection_risk=70,
            success_chance=50,
            success_text="She blinks, confused. 'Sorry, why did I come here?'",
            failure_text="It doesn't work. She's too focused. Her suspicion grows."
        )
    ]
)

DAWN_TOM_INTERVENTION = DynamicEvent(
    event_id="visitor_intervention",
    event_type="visitor",
    title="The Intervention",
    description="Dawn and Tom show up together. 'We need to talk about your influence on the family.'",
    icon="👥",
    primary_character="Dawn",
    secondary_characters=["Tom"],
    alliance_strength_threshold=60,  # Requires strong alliance
    weight=15,
    urgency_level="critical",
    pressure=True,
    options=[
        EventOption(
            option_id="apologize_reform",
            text="Apologize and promise to 'reform'",
            suspicion_changes={"Dawn": -20, "Tom": -15},
            success_chance=70,
            success_text="They seem satisfied... for now.",
            failure_text="Dawn: 'I don't believe you.'"
        ),
        EventOption(
            option_id="deny_everything",
            text="Deny everything convincingly",
            requires_sp=8,
            sp_cost=5,
            suspicion_changes={"Dawn": 10, "Tom": 5},
            success_chance=50,
            success_text="Your performance is convincing enough to buy time...",
            failure_text="Dawn sees right through you. 'We're watching you.'"
        )
    ]
)

# ====== MEMORY TRIGGER EVENTS ======

PHS_ACTIVATION_PUBLIC = DynamicEvent(
    event_id="memory_phs_public_activation",
    event_type="memory_trigger",
    title="PHS Activates in Public",
    description="One of your planted suggestions activates while everyone is present!",
    icon="💫",
    observers=["Ruth", "Tom", "Dawn", "Melanie"],
    weight=15,
    urgency_level="high",
    options=[
        EventOption(
            option_id="act_natural",
            text="Act completely natural and unsurprised",
            success_chance=60,
            success_text="No one notices anything unusual...",
            failure_text="Dawn: 'That was strange... did you say something to them earlier?'"
        ),
        EventOption(
            option_id="create_distraction",
            text="Create a distraction to redirect attention",
            sp_cost=2,
            success_chance=80,
            success_text="You successfully divert everyone's attention.",
            failure_text="The distraction backfires and draws more attention."
        ),
        EventOption(
            option_id="defensive_phs",
            text="Quickly activate defensive PHS to reduce suspicion",
            sp_cost=6,
            allows_phs=True,
            phs_success_bonus=10,
            success_text="Your defensive suggestion helps cover the moment...",
            failure_text="Too obvious. Suspicion increases."
        )
    ]
)

DEJA_VU_MOMENT = DynamicEvent(
    event_id="memory_deja_vu",
    event_type="memory_trigger",
    title="Déjà Vu Moment",
    description="A character suddenly has a strong feeling they've experienced this before...",
    icon="🌀",
    primary_character="Karen",
    weight=10,
    options=[
        EventOption(
            option_id="acknowledge",
            text="'Yes, we talked about this before. Remember?'",
            rapport_changes={"Karen": 2},
            success_text="Karen: 'Oh yes, that's right. Thanks for reminding me.'"
        ),
        EventOption(
            option_id="use_confusion",
            text="Use the confusion to reinforce existing PHS",
            sp_cost=3,
            allows_phs=True,
            phs_target="Karen",
            phs_success_bonus=20,
            success_text="Her confused state makes her very receptive..."
        )
    ]
)


# ====== EVENT LIBRARY DICTIONARY ======

ALL_EVENTS = {
    # Encounters
    "encounter_coffee_spill_ruth": COFFEE_SPILL,
    "encounter_overheard_gossip": OVERHEARD_ARGUMENT,

    # Character-Initiated
    "initiated_tom_work_crisis": TOM_WORK_CRISIS,
    "initiated_melanie_seeks_advice": MELANIE_ADVICE,

    # Opportunities
    "opportunity_dawn_alone": DAWN_ALONE_KITCHEN,
    "opportunity_vulnerable_vanessa": VULNERABLE_MOMENT,

    # Crises
    "crisis_ruth_melanie_fight": FAMILY_ARGUMENT,
    "crisis_derek_injury": DEREK_MEDICAL_EMERGENCY,

    # Visitors
    "visitor_ruth_suspicious": RUTH_UNEXPECTED_VISIT,
    "visitor_intervention": DAWN_TOM_INTERVENTION,

    # Memory Triggers
    "memory_phs_public_activation": PHS_ACTIVATION_PUBLIC,
    "memory_deja_vu": DEJA_VU_MOMENT,
}


def get_event(event_id: str) -> DynamicEvent:
    """Get event by ID"""
    return ALL_EVENTS.get(event_id)


def get_events_by_type(event_type: str) -> dict:
    """Get all events of a specific type"""
    return {
        event_id: event
        for event_id, event in ALL_EVENTS.items()
        if event.event_type == event_type
    }
