from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from datetime import time


class Student(BaseModel):
    """
    Represents a student requesting a swimming lesson.

    Attributes:
        name: Unique name identifying the student.
        lesson_type: One of "group", "private", "flexible_group", or "flexible_private".
        swim_style: List of swim styles the student wants (e.g., ["freestyle"]).
        availability: List of time slots, each with keys "day", "start", and "end".
        assigning_score: Score based on how many slots the student matched (used for scheduling).
        assigned_lesson: The lesson the student is ultimately assigned to.
    """
    name: str
    lesson_type: str
    swim_style: List[str]
    availability: List[Dict[str, Union[str, time]]]
    assigning_score: int = 0
    assigned_lesson: Optional["Lesson"] = None  # Will be assigned later

    def __hash__(self):
        # Allows Student instances to be used in sets by using name as unique ID
        return hash(self.name)

    def __eq__(self, other):
        # Two students are considered equal if they have the same name
        if isinstance(other, Student):
            return self.name == other.name
        return False


class Instructor(BaseModel):
    """
    Represents a swimming instructor.

    Attributes:
        name: Name of the instructor.
        swim_style: List of swim styles the instructor can teach.
        lessons: List of lessons the instructor has been assigned to.
        availability: List of available time slots, each with "day", "start", and "end".
    """
    name: str
    swim_style: List[str]
    lessons: List["Lesson"] = []
    availability: List[Dict[str, Union[str, time]]]


class Lesson(BaseModel):
    """
    Represents a scheduled swimming lesson.

    Attributes:
        lesson_id: Unique identifier for the lesson.
        lesson_type: "group", "private", or fallback "flexible_private".
        swim_style: The swim style being taught.
        students: List of students attending this lesson.
        instructor: The assigned instructor.
        day: The weekday the lesson occurs.
        start_time: Start time of the lesson (datetime.time object).
        end_time: End time of the lesson (datetime.time object).
    """
    lesson_id: int
    lesson_type: str
    swim_style: str
    students: List[Student] = []
    instructor: Optional[Instructor] = None
    day: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    def add_student(self, student: Student):
        """
        Adds a student to the lesson's student list.
        """
        self.students.append(student)
