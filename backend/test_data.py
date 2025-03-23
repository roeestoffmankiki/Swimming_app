from datetime import time
from models import Student

test_students = [

    # 🎯 Iris: Group lesson; available exactly at the start of Tuesday (8:00–9:00) for breaststroke.
    Student(
        name="Iris",
        lesson_type="group",
        swim_style=["breaststroke"],
        availability=[{"day": "Tuesday", "start": time(8, 0), "end": time(9, 0)}]
    ),

    # 🎯 Jack: Private lesson; available in two windows (Tuesday 10–11 and Wednesday 14–15) for freestyle.
    # The algorithm should choose the optimal slot (e.g., Tuesday 10–11 if available).
    Student(
        name="Jack",
        lesson_type="private",
        swim_style=["freestyle"],
        availability=[
            {"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)},
            {"day": "Wednesday", "start": time(14, 0), "end": time(15, 0)}
        ]
    ),

    # 🎯 Karen: Flexible private; available exactly one slot on Thursday (10–11) with two swim styles.
    # She should either join a matching group lesson or get a fallback unassigned lesson.
    Student(
        name="Karen",
        lesson_type="flexible_private",
        swim_style=["backstroke", "freestyle"],
        availability=[{"day": "Thursday", "start": time(10, 0), "end": time(11, 0)}]
    ),

    # 🎯 Leo: Group lesson; available on Tuesday (10–12) and Wednesday (10–12) with multiple swim styles.
    # Tests multi-day and multi-style availability for grouping.
    Student(
        name="Leo",
        lesson_type="group",
        swim_style=["freestyle", "breaststroke"],
        availability=[
            {"day": "Tuesday", "start": time(10, 0), "end": time(12, 0)},
            {"day": "Wednesday", "start": time(10, 0), "end": time(12, 0)}
        ]
    ),

    # 🎯 Mia: Private lesson; available exactly at the edge of an instructor's slot.
    # For butterfly on Thursday, available from 15:00 to 16:00.
    Student(
        name="Mia",
        lesson_type="private",
        swim_style=["butterfly"],
        availability=[{"day": "Thursday", "start": time(15, 0), "end": time(16, 0)}]
    ),

    # 🎯 Nina: Flexible private; available exactly within a common slot for freestyle on Tuesday (10–11).
    Student(
        name="Nina",
        lesson_type="flexible_private",
        swim_style=["freestyle"],
        availability=[{"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}]
    ),

    # 🎯 Oscar: Group lesson; available only on Wednesday from 8:00 to 9:00 for breaststroke.
    Student(
        name="Oscar",
        lesson_type="group",
        swim_style=["breaststroke"],
        availability=[{"day": "Wednesday", "start": time(8, 0), "end": time(9, 0)}]
    ),

    # 🎯 Pam: Private lesson; available on two windows for backstroke:
    # Monday 16:00–17:00 and Thursday 16:00–17:00. Tests selection when multiple windows are offered.
    Student(
        name="Pam",
        lesson_type="private",
        swim_style=["backstroke"],
        availability=[
            {"day": "Monday", "start": time(16, 0), "end": time(17, 0)},
            {"day": "Thursday", "start": time(16, 0), "end": time(17, 0)}
        ]
    ),

    # 🎯 Quinn: Flexible private; available exactly on Tuesday (10–11) for freestyle.
    # Tests if the fallback correctly merges her into an existing group lesson or creates a fallback.
    Student(
        name="Quinn",
        lesson_type="flexible_private",
        swim_style=["freestyle"],
        availability=[{"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}]
    ),

    # 🎯 Ryan: Group lesson; available exactly within an instructor slot for butterfly on Wednesday (8–9).
    Student(
        name="Ryan",
        lesson_type="group",
        swim_style=["butterfly"],
        availability=[{"day": "Wednesday", "start": time(8, 0), "end": time(9, 0)}]
    ),

    # A student with two possible time slots
    Student(
        name="Private1",
        lesson_type="private",
        swim_style=["freestyle"],
        availability=[
            {"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)},
            {"day": "Wednesday", "start": time(11, 0), "end": time(12, 0)},
        ]
    ),

    # A student with only one available slot
    Student(
        name="Private2",
        lesson_type="private",
        swim_style=["breaststroke"],
        availability=[
            {"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)},
        ]
    ),

    # A student with two swim styles
    Student(
        name="Private3",
        lesson_type="private",
        swim_style=["butterfly", "backstroke"],
        availability=[
            {"day": "Thursday", "start": time(14, 0), "end": time(15, 0)},
        ]
    ),

    # A student who cannot be matched (style not supported by instructors)
    Student(
        name="NoMatch",
        lesson_type="private",
        swim_style=["synchronized-swimming"],
        availability=[
            {"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)},
        ]
    ),

    # Backstroke group at 10:00
    Student(name="Back1", lesson_type="private", swim_style=["backstroke"],
            availability=[{"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}]),
    Student(name="Back2", lesson_type="private", swim_style=["backstroke"],
            availability=[{"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}]),
    Student(name="Back3", lesson_type="private", swim_style=["backstroke"],
            availability=[{"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}]),

    # Freestyle group at same slot
    Student(name="Free1", lesson_type="private", swim_style=["freestyle"],
            availability=[{"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}]),
    Student(name="Free2", lesson_type="private", swim_style=["freestyle"],
            availability=[{"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}]),

    # Breaststroke only at one available time
    *[Student(name=f"BreastY{i}", lesson_type="group", swim_style=["breaststroke"],
              availability=[
                  {"day": "Tuesday", "start": time(10, 0), "end": time(11, 0)}
              ]) for i in range(1, 4)],

    # Mixed styles (freestyle + butterfly)
    *[Student(name=f"MixZ{i}", lesson_type="group", swim_style=["freestyle", "butterfly"],
              availability=[
                  {"day": "Tuesday", "start": time(11, 0), "end": time(12, 0)},
                  {"day": "Wednesday", "start": time(9, 0), "end": time(10, 0)}
              ]) for i in range(1, 3)],
]
