import uvicorn
from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from models import Instructor, Student, Lesson
from test_data import test_students
from datetime import datetime, time

# Initialize FastAPI app
app = FastAPI()

# Allow cross-origin requests (use specific domains in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains (Change this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Global Constants and Variables

max_students = 30  # Maximum number of students allowed in the system

# Dictionary that will hold time slot structure: {day: {hour: {instructors, students}}}
time_slots = {}

# Temporary storage for students before scheduling
students: set[Student] = set()

# Predefined list of instructors and their swim styles + availability
instructors = [
    Instructor(
        name="Yoni",
        swim_style=["breaststroke", "butterfly"],  # Can teach only these
        availability=[
            {"day": "Tuesday", "start": time(8, 0), "end": time(15, 0)},
            {"day": "Wednesday", "start": time(8, 0), "end": time(15, 0)},
            {"day": "Thursday", "start": time(8, 0), "end": time(15, 0)},
        ]
    ),
    Instructor(
        name="Yotam",
        swim_style=["freestyle", "breaststroke", "butterfly", "backstroke"],  # Can teach all styles
        availability=[
            {"day": "Monday", "start": time(16, 0), "end": time(20, 0)},
            {"day": "Thursday", "start": time(16, 0), "end": time(20, 0)}
        ]
    ),
    Instructor(
        name="Johnny",
        swim_style=["freestyle", "breaststroke", "butterfly", "backstroke"],  # Can teach all styles
        availability=[
            {"day": "Sunday", "start": time(10, 0), "end": time(19, 0)},
            {"day": "Tuesday", "start": time(10, 0), "end": time(19, 0)},
            {"day": "Thursday", "start": time(10, 0), "end": time(19, 0)}
        ]
    )
]

# Final results: assigned and unassigned lessons
assigned_lessons: List[Lesson] = []
unassigned_lessons: List[Lesson] = []


def parse_time_field(value) -> time:
    """
       Parses a time value from a string or returns it directly if already a `time` object.

       This utility function ensures consistent handling of time fields
       that may be passed either as strings (e.g., "14:00") or as `datetime.time` objects.

       Args:
           value (str | time): The input time value.

       Returns:
           time: A `datetime.time` object representing the parsed time.

       Raises:
           ValueError: If the input is neither a string in "%H:%M" format nor a `time` object.
       """
    if isinstance(value, time):
        return value
    elif isinstance(value, str):
        return datetime.strptime(value, "%H:%M").time()
    raise ValueError(f"Unsupported time format: {value}")


def initialize_time_slots():
    """
        Initializes the global `time_slots` dictionary based on instructor availability.

        This function builds a schedule grid where each key is a day of the week,
        and each nested key is an hourly time slot (e.g., '10:00'). For each time slot,
        it tracks:
        - which instructors are available
        - which students are available (grouped by swim style)

        Returns:
            dict: The fully constructed `time_slots` dictionary.
        """
    global time_slots, instructors

    # Iterate through each instructor's availability
    for instructor in instructors:
        for availability in instructor.availability:  # Instructor's available slots
            day = availability["day"]
            start_hour = availability["start"].hour  # Extract hour from datetime.time object
            end_hour = availability["end"].hour

            # Initialize the day if not already present
            if day not in time_slots:
                time_slots[day] = {}

            # Add only available hours for this instructor
            for hour in range(start_hour, end_hour):
                time_str = f"{hour}:00"

                # Initialize the hour slot if it doesn't exist
                if time_str not in time_slots[day]:
                    time_slots[day][time_str] = {
                        "students": {
                            "freestyle": [],
                            "breaststroke": [],
                            "butterfly": [],
                            "backstroke": []
                        },
                        "instructors": []
                    }

                # Register the instructor as available in this time slot
                time_slots[day][time_str]["instructors"].append(instructor)

    return time_slots


def assign_students_to_slots(lesson_type_filter):
    """
    Assigns students to available time slots based on their lesson type,
    availability, and swim style compatibility with instructors.

    This function updates the global `time_slots` structure by assigning
    students to swim-style-specific lists under matching time slots.
    It only processes students whose lesson type is in `lesson_type_filter`.

    Args:
        lesson_type_filter (List[str]): A list of allowed lesson types to filter students (e.g. ["group", "private"]).

    Returns:
        dict: The updated `time_slots` dictionary with students assigned.
    """
    global students, time_slots

    for student in students:
        if student.lesson_type not in lesson_type_filter:
            continue  # Skip students who don't match the lesson type

        for availability in student.availability:
            day = availability["day"]
            start_hour = availability["start"].hour
            end_hour = availability["end"].hour

            # Ensure the day exists in the time_slots structure
            if day in time_slots:
                for hour in range(start_hour, end_hour):
                    time_str = f"{hour}:00"

                    # Check if the time slot exists
                    if time_str in time_slots[day]:

                        valid_slot = False  # Used to count assigning_score only once per slot

                        for swim_style in student.swim_style:  # Iterate over each swim style separately
                            # Check if any instructor at this slot supports the swim style
                            instructors_at_slot = time_slots[day][time_str]["instructors"]
                            if any(swim_style in instructor.swim_style for instructor in instructors_at_slot):
                                # Assign the student
                                time_slots[day][time_str]["students"][swim_style].append(student)
                                valid_slot = True
                        if valid_slot:
                            student.assigning_score += 1  # Counted once per time slot

    return time_slots


def assign_group_lessons_from_slots():
    """
    Iteratively assigns group lessons by searching the time_slots structure for the
    swim style group with the highest number of students at any given time.

    Process:
    1. Find the time slot (day and hour) and swim style that has the largest group of students.
    2. Select an instructor who is available at that time and can teach that swim style.
    3. Create a group lesson with all students in that group.
    4. Assign the lesson to those students and update the assigned_lessons list.
    5. Remove the assigned students from the corresponding slot to avoid reassignment.

    Assumptions:
    - `time_slots` is a dictionary structured as:
      { day: { hour: { instructors: [...], students: { swim_style: [Student, ...] } } } }
    - Each swim_style group is independent and students are not shared across styles or slots.
    - Students must be assigned to a slot that has at least one instructor qualified in their swim style.
    """
    global time_slots, assigned_lessons

    while True:
        max_group = []  # Holds the largest group of students found in one slot/style
        max_day = None  # Corresponding day of that group
        max_hour = None  # Corresponding hour (e.g., '10:00') of that group
        max_style = None  # Corresponding swim style of that group

        # Step 1: Find the swim style group with the most students
        for day, slots in time_slots.items():
            for hour, details in slots.items():
                for style, students in details["students"].items():
                    if len(students) > len(max_group):
                        max_group = students
                        max_day = day
                        max_hour = hour
                        max_style = style

        # Step 2: Stop if no groups left to assign
        if not max_group:
            break

        # Step 3: Find the first available instructor at that slot who can teach this style
        instructors = time_slots[max_day][max_hour]["instructors"]
        instructor_for_lesson = next(
            (instr for instr in instructors if max_style in instr.swim_style), None)

        # Step 4: Create a new group lesson
        start_hour_int = int(max_hour.split(":")[0])
        new_lesson = Lesson(
            lesson_id=len(assigned_lessons),
            lesson_type="group",
            swim_style=max_style,
            students=max_group,
            instructor=instructor_for_lesson,
            day=max_day,
            start_time=time(start_hour_int, 0),
            end_time=time(start_hour_int + 1, 0)
        )

        # Assign this lesson to each student in the group
        for student in max_group:
            student.assigned_lesson = new_lesson

        # Step 5: Add the lesson to the assigned list
        assigned_lessons.append(new_lesson)

        # Step 6: Remove these students from the time slot to prevent reassignment
        students_to_remove = time_slots[max_day][max_hour]["students"][max_style].copy()
        modify_assigned_slots(max_day, max_hour, max_style, instructor_for_lesson, students_to_remove)


def assign_private_lessons_from_slots():
    """
    Assigns private lessons by scanning all available time slots and selecting:
    1. The time slot with the fewest total unique students.
    2. From that slot, the student with the lowest assigning_score (i.e., least flexibility).
    3. Matches the student with an instructor who can teach one of their swim styles.
    4. Creates a private lesson and updates all relevant structures.

    Process repeats until no more students can be assigned.
    Assumes:
    - Students and instructors are already registered in the time_slots structure.
    - A single student is assigned per lesson.
    - Private lessons last 45 minutes.
    """
    global assigned_lessons, time_slots, students

    while True:
        selected_day = None  # Day of the selected slot
        selected_time = None  # Time of the selected slot
        selected_slot = None  # Slot object with the fewest students
        min_students_count = float('inf')  # Initialize with a high value

        # Step 1: Find a slot with the smallest number of unique students (but not zero)
        for day, slots in time_slots.items():
            for time_str, slot in slots.items():
                unique_students = set()
                for group in slot["students"].values():
                    unique_students.update(group)
                total_students = len(unique_students)

                # Select only non-empty slots with fewer students than previous best
                if 0 < total_students < min_students_count:
                    min_students_count = total_students
                    selected_day = day
                    selected_time = time_str
                    selected_slot = slot

        # Stop if no valid time slot found
        if selected_slot is None:
            break

        # Step 2: Pick the student in this slot with the least availability (lowest assigning_score)
        unique_students = set()
        for group in selected_slot["students"].values():
            unique_students.update(group)

        selected_student = min(unique_students, key=lambda s: s.assigning_score)

        # Step 3: Find a swim style that both the student wants and an instructor at this slot can teach
        instructor_for_lesson = None
        selected_style = None
        for style in selected_student.swim_style:
            instructor_for_lesson = next(
                (instr for instr in selected_slot["instructors"] if style in instr.swim_style),
                None)

            if instructor_for_lesson:
                selected_style = style
                break

        # Step 4: Create a private lesson (45 minutes) for the selected student
        start_hour_int = int(selected_time.split(":")[0])
        new_lesson = Lesson(
            lesson_id=len(assigned_lessons),
            lesson_type="private",
            swim_style=selected_style,
            students=[selected_student],
            instructor=instructor_for_lesson,
            day=selected_day,
            start_time=time(start_hour_int, 0),
            end_time=time(start_hour_int, 45)
        )

        # Record the lesson
        assigned_lessons.append(new_lesson)
        selected_student.assigned_lesson = new_lesson

        # Step 5: Remove this student from the slot to avoid duplicate assignments
        modify_assigned_slots(selected_day, selected_time, selected_style,
                              instructor_for_lesson, [selected_student])


def modify_assigned_slots(day: str, time_str: str, swim_style: str,
                          instructor_used: Instructor, students_to_remove: List[Student]):
    """
    Updates the time_slots structure after assigning a lesson (group or private).

    Parameters:
    - day: Day of the time slot (e.g., "Tuesday").
    - time_str: Hour of the slot in "HH:00" format (e.g., "10:00").
    - swim_style: Swim style that was just assigned (used to clean up).
    - instructor_used: Instructor assigned to this lesson.
    - students_to_remove: List of students who have been assigned and should be removed from slots.

    Steps:
    1. Remove the assigned students from *all* time slots (regardless of time/style).
    2. If the slot only had one instructor, remove the entire slot.
    3. If multiple instructors remain:
       a. Remove the used instructor from the instructor list.
       b. Clear only the swim style that was just assigned (group case).
       c. Remove any other swim styles that are no longer teachable by remaining instructors.
    """
    global time_slots

    slot = time_slots[day][time_str]

    # Step 1: Remove the assigned students from *all* slots in the schedule
    remove_students_from_their_slots(students_to_remove)

    # Step 2: If this instructor was the only one, delete the entire slot
    if len(slot["instructors"]) == 1:
        del time_slots[day][time_str]
        return

    # Step 3a: Remove the instructor who was just used
    slot["instructors"] = [instr for instr in slot["instructors"] if instr.name != instructor_used.name]

    # Step 3b: Only clear the swim style group if this was a group lesson
    if len(students_to_remove) > 1: slot["students"][swim_style] = []

    # Step 3c: Remove any swim styles that are no longer supported by remaining instructors
    remaining_styles = set()
    for instr in slot["instructors"]:
        remaining_styles.update(instr.swim_style)

    for style in list(slot["students"].keys()):
        if style not in remaining_styles:
            slot["students"][style] = []


def remove_students_from_their_slots(students_to_remove: List[Student]):
    """
    Removes the specified students from all relevant time slots.

    Iterates over each student's availability and removes them from all swim style groups
    in the matching time slots.

    Parameters:
    - students_to_remove: List of Student objects to remove from slots.
    """
    global time_slots

    for student in students_to_remove:
        for availability in student.availability:
            day = availability["day"]
            start_hour = availability["start"].hour
            end_hour = availability["end"].hour

            # Go through every hour in their availability window
            for hour in range(start_hour, end_hour):
                time_str = f"{hour}:00"

                # Check that the day and time exist in the schedule
                if day in time_slots and time_str in time_slots[day]:
                    slot = time_slots[day][time_str]

                    # Remove the student from all swim style lists within that slot
                    for swim_style in slot["students"]:
                        slot["students"][swim_style] = [
                            s for s in slot["students"][swim_style] if s != student
                        ]


def is_student_available_for_lesson(student: Student, lesson: "Lesson") -> bool:
    """
    Checks if the student is available for a given lesson.

    Returns True if the lesson's day and time fit within any of the student's availability slots.

    Parameters:
    - student: A Student object with a list of availability dictionaries.
    - lesson: A Lesson object with specified day, start_time, and end_time.

    Returns:
    - bool: True if the student can attend the lesson, False otherwise.
    """
    if lesson.day is None or lesson.start_time is None or lesson.end_time is None:
        return False

    for avail in student.availability:
        avail_day = avail.get("day")
        # Fallback support for alternative key names
        avail_start = avail.get("start") or avail.get("start_time")
        avail_end = avail.get("end") or avail.get("end_time")
        if avail_day == lesson.day and avail_start and avail_end:
            # Check if lesson fully fits within the availability window
            if avail_start <= lesson.start_time and lesson.end_time <= avail_end:
                return True
    return False


def assign_flexible_private_fallback():
    """
    Handles students who haven't been assigned a lesson yet.

    For each unassigned student:
    - If they are of type 'flexible_private':
        Try to find an existing group lesson that:
          • Matches one of their swim styles
          • Fits within one of their availability windows
        If found, assign the student to that group lesson.
    - If still unassigned after the attempt:
        Create a fallback "unassigned" lesson and add them there.

    Updates:
    - student.assigned_lesson
    - assigned_lessons (only through adding to existing lessons)
    - unassigned_lessons (if no suitable group found)
    """
    global students, assigned_lessons, unassigned_lessons

    for student in students:
        if student.assigned_lesson is None:
            # First attempt: merge flexible_private into group lessons
            if student.lesson_type == "flexible_private":
                for lesson in assigned_lessons:
                    if lesson.lesson_type == "group" and lesson.swim_style in student.swim_style:
                        if is_student_available_for_lesson(student, lesson):
                            lesson.students.append(student)
                            student.assigned_lesson = lesson
                            break

            # Fallback: create an unassigned lesson entry
            if student.assigned_lesson is None:
                new_lesson = Lesson(
                    lesson_id=len(assigned_lessons) + len(unassigned_lessons),
                    lesson_type=student.lesson_type,
                    swim_style=", ".join(student.swim_style),  # Comma-separated if multiple styles
                    students=[student],
                )
                unassigned_lessons.append(new_lesson)
                student.assigned_lesson = new_lesson


@app.get("/len_students")
def get_len_students():
    """
    Returns the current number of submitted students.
    Useful for frontend logic (e.g., enabling/disabling views).
    """
    return len(students)


@app.post("/submit_student")
def submit_student(student: Student):
    """
    Receives a new student from the frontend and adds them to the system.

    Steps:
    - Prevents duplicate submissions
    - Ensures the max number of students isn't exceeded
    - Converts string-based availability times to `datetime.time` objects
    - Adds the student to the `students` set

    Returns:
    - A message indicating success, duplication, or overflow
    """
    global students

    # Check if student already exists
    if student in students:
        return {"message": f"Student {student.name} is already in the list."}

    # Prevent exceeding the maximum allowed students
    if len(students) >= max_students:
        return {"message": "Maximum student limit reached. No more students can be added."}

    # Convert time strings (from frontend) to datetime.time objects
    for slot in student.availability:
        if isinstance(slot["start"], str):
            slot["start"] = datetime.strptime(slot["start"], "%H:%M").time()
        if isinstance(slot["end"], str):
            slot["end"] = datetime.strptime(slot["end"], "%H:%M").time()

    students.add(student)

    return {"message": f"Student {student.name} added. {max_students - len(students)} more student spots available."}


@app.get("/students")
def get_students():
    """
    Returns a list of all currently submitted students.

    Used for debugging or showing a summary in the frontend.
    """
    return {"students": students}


@app.get("/schedule")
def get_schedule():
    """
    Triggers the full scheduling algorithm and returns all assigned and unassigned lessons.

    Steps:
    - Resets prior schedules and slot allocations
    - Loads test students if empty (for dev purposes)
    - Assigns students by lesson type (group → private → flexible_private)
    - Returns both assigned and unassigned lessons in a structured format
    """
    global students, assigned_lessons, unassigned_lessons, time_slots

    reset_state()

    # Load test students automatically if empty (for easier testing)
    if not students:
        students = set(test_students)

    # Assign students in scheduling phases
    assign_students_to_slots(["group", "flexible_group"])
    assign_group_lessons_from_slots()
    assign_students_to_slots(["private"])
    assign_private_lessons_from_slots()
    assign_students_to_slots(["flexible_private"])
    assign_private_lessons_from_slots()
    assign_flexible_private_fallback()

    # Format and return results
    return {
        "assigned_lessons": [
            {
                "lesson_id": lesson.lesson_id,
                "lesson_type": lesson.lesson_type,
                "swim_style": lesson.swim_style,
                "instructor": lesson.instructor.name if lesson.instructor else None,
                "students": [student.name for student in lesson.students],
                "day": lesson.day,
                "start_time": lesson.start_time.strftime("%H:%M") if lesson.start_time else None,
                "end_time": lesson.end_time.strftime("%H:%M") if lesson.end_time else None,
            }
            for lesson in assigned_lessons
        ],
        "unassigned_lessons": [
            {
                "lesson_id": lesson.lesson_id,
                "lesson_type": lesson.lesson_type,
                "swim_style": lesson.swim_style,
                "students": [student.name for student in lesson.students],
            }
            for lesson in unassigned_lessons
        ],
    }


@app.get("/reset")
def reset_state():
    """
    Resets all runtime data structures: lessons and time slots.
    Does not clear the `students` set — that must be cleared explicitly.

    Called internally before scheduling, or externally for manual resets.
    """
    global students, assigned_lessons, unassigned_lessons, time_slots

    # Clear assigned_lesson for all students before starting scheduling
    for student in students:
        student.assigned_lesson = None

    assigned_lessons.clear()
    unassigned_lessons.clear()
    time_slots.clear()
    initialize_time_slots()
    return {"message": "State has been reset."}


@app.on_event("startup")
def reset_data_on_startup():
    """
    FastAPI hook: clears and resets all data when the server starts.

    Ensures the backend starts with a clean state every time (for local dev).
    """
    global students, assigned_lessons, unassigned_lessons
    students.clear()
    assigned_lessons.clear()
    unassigned_lessons.clear()
    time_slots.clear()
    print("🔄 Backend restarted: Cleared all students and lessons")
    initialize_time_slots()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
