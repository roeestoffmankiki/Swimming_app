#classes
# from pydantic import BaseModel
# from typing import List, Optional, Dict, Union
# from datetime import datetime, time, timedelta
#
#
# class Student(BaseModel):
#     name: str
#     lesson_type: str  # "group", "private", or "flexible"
#     swim_style: List[str]  # e.g., "freestyle", "butterfly", etc.
#     availability: List[Dict[str, Union[str, time]]]
#     assigning_score: int = 0
#     assigned_lesson: Optional["Lesson"] = None  # Will be assigned later
#
#     def __hash__(self):
#         return hash(self.name)  # Assuming 'name' uniquely identifies a student
#
#     def __eq__(self, other):
#         if isinstance(other, Student):
#             return self.name == other.name
#         return False
#
#
# class Instructor(BaseModel):
#     name: str
#     swim_style: List[str]  # e.g., "freestyle", "butterfly", etc.
#     lessons: List["Lesson"] = []  # Will be assigned later
#     availability: List[Dict[str, Union[str, time]]]  # Each entry has a day, start, and end time
#
#     def find_available_slot(self, lesson_duration: timedelta) -> Optional[Dict[str, time]]:
#         """
#         Find an available time slot that can accommodate a lesson.
#         Returns the matching slot or None if no slot is available.
#         """
#         for slot in self.availability:
#             available_duration = datetime.combine(datetime.today(), slot["end"]) - datetime.combine(datetime.today(),
#                                                                                                     slot["start"])
#             if available_duration >= lesson_duration:
#                 return slot  # Found a suitable slot
#         return None  # No available slot found
#
#     def assign_lesson(self, lesson: "Lesson") -> bool:
#         """
#         Assign a lesson to the instructor if it fits within availability.
#         Returns True if assigned, False if no available slot was found.
#         """
#         lesson_duration = timedelta(minutes=lesson.get_duration())
#         available_slot = self.find_available_slot(lesson_duration)
#
#         if not available_slot:
#             return False  # No slot available, exit early
#
#         # ✅ Assign the lesson within the available slot
#         lesson_time = available_slot["start"]
#         lesson.assign_instructor_and_time(self, available_slot["day"],
#                                           available_slot["start"])  # Assign time, day, instructor
#
#         # ✅ Update instructor's availability
#         available_slot["start"] = (datetime.combine(datetime.today(), lesson_time) + lesson_duration).time()
#
#         self.lessons.append(lesson)
#         return True  # Successfully assigned
#
#
# class Lesson(BaseModel):
#     lesson_id: int
#     lesson_type: str  # "group" or "private"
#     swim_style: str  # e.g., "freestyle", "breaststroke"
#     students: List[Student] = []
#     instructor: Optional[Instructor] = None
#     day: Optional[str] = None  # "Monday", "Tuesday", etc.
#     start_time: Optional[time] = None  # Stores only HH:MM, frontend will handle conversion
#     end_time: Optional[time] = None
#
#     def get_duration(self) -> int:
#         """Returns duration in minutes based on lesson type"""
#         return 60 if self.lesson_type == "group" else 45
#
#     def assign_instructor_and_time(self, instructor: Instructor, day: str, start_time: time):
#         """
#         Assigns an instructor, day, and time when the lesson is scheduled.
#         """
#         self.instructor = instructor
#         self.day = day
#         self.start_time = start_time
#         duration = self.get_duration()
#
#         lesson_duration = timedelta(minutes=duration)
#         self.end_time = (datetime.combine(datetime.today(), start_time) + lesson_duration).time()
#
#     def add_student(self, student: Student):
#         self.students.append(student)



# version 1

# import uvicorn
# from fastapi import FastAPI
# from typing import List
# from datetime import time
# from fastapi.middleware.cors import CORSMiddleware
# from models import Instructor, Student, Lesson
# from test_data import test_students
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all domains (Change this in production)
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )
#
# #Global variables
#
# max_students = 30
# # Temporary storage for students before scheduling
# students: List[Student] = []
#
# # Instructor Data
# instructors = [
#     Instructor(
#         name="Yoni",
#         swim_style=["breaststroke", "butterfly"],  # Can teach only these
#         availability=[
#             {"day": "Tuesday", "start": time(8, 0), "end": time(15, 0)},
#             {"day": "Wednesday", "start": time(8, 0), "end": time(15, 0)},
#             {"day": "Thursday", "start": time(8, 0), "end": time(15, 0)},
#         ]
#     ),
#     Instructor(
#         name="Yotam",
#         swim_style=["freestyle", "breaststroke", "butterfly", "backstroke"],  # Can teach all styles
#         availability=[
#             {"day": "Monday", "start": time(16, 0), "end": time(20, 0)},
#             {"day": "Thursday", "start": time(16, 0), "end": time(20, 0)}
#         ]
#     ),
#     Instructor(
#         name="Johnny",
#         swim_style=["freestyle", "breaststroke", "butterfly", "backstroke"],  # Can teach all styles
#         availability=[
#             {"day": "Sunday", "start": time(10, 0), "end": time(19, 0)},
#             {"day": "Tuesday", "start": time(10, 0), "end": time(19, 0)},
#             {"day": "Thursday", "start": time(10, 0), "end": time(19, 0)}
#         ]
#     )
# ]
#
# assigned_lessons: List[Lesson] = []
# unassigned_lessons: List[Lesson] = []
#
#
# def create_lesson_buckets():
#     """
#     Organizes students into categorized lesson buckets.
#     - group_lessons: Lessons with 1-10 students.
#     - private_lessons: Lessons with exactly 1 student.
#     - flexible_private_lessons: Students who prefer private but might be moved to a group.
#     """
#     global students  # Use the global student list
#     group_lessons = []  # Holds all grouped lessons
#     private_lessons = []  # Holds strictly private lessons
#     flexible_private_lessons = []  # Holds private-preferred students
#     total_lessons = 0
#
#     for student in students:
#         assigned = False  # Track whether the student has been placed in a lesson
#
#         # 🟢 Group Lessons: Try to fit student into an existing lesson
#         if student.lesson_type in ["group", "flexible_group"]:
#             for lesson in group_lessons:
#                 if lesson.swim_style == student.swim_style and len(lesson.students) < 10:  # Group limit: 10 students
#                     lesson.students.append(student)
#                     student.assigned_lesson = lesson
#                     assigned = True
#                     break  # Stop once assigned
#
#             # If no suitable group found, create a new group lesson
#             if not assigned:
#                 new_group = Lesson(
#                     lesson_id=total_lessons,
#                     lesson_type="group",
#                     swim_style=student.swim_style,
#                     students=[student],
#                 )
#                 total_lessons += 1
#                 group_lessons.append(new_group)
#                 student.assigned_lesson = new_group
#
#         # 🔵 Private Lessons: Directly create a private lesson
#         if student.lesson_type in ["private", "flexible_private"]:
#             new_private = Lesson(
#                 lesson_id=total_lessons,
#                 lesson_type=student.lesson_type,
#                 swim_style=student.swim_style,
#                 students=[student],
#             )
#             total_lessons += 1
#             student.assigned_lesson = new_private
#             (private_lessons if student.lesson_type == "private" else flexible_private_lessons).append(new_private)
#
#     return group_lessons, private_lessons, flexible_private_lessons
#
# def get_prioritized_instructors(swim_style):
#     """
#     Returns the prioritized order of instructors:
#     - If **breaststroke or butterfly**, prioritize **Yoni first**.
#     - Otherwise, prioritize **Johnny and Yotam first**.
#     """
#     if swim_style in ["breaststroke", "butterfly"]:
#         return sorted(instructors, key=lambda i: i.name != "Yoni")  # Yoni first
#     return sorted(instructors, key=lambda i: i.name == "Yoni")  # Johnny & Yotam first
#
#
# def assign_lessons():
#     """Assigns lessons to instructors based on availability."""
#     global assigned_lessons, unassigned_lessons
#     assigned_lessons.clear()
#     unassigned_lessons.clear()
#     group_lessons, private_lessons, flexible_private_lessons = create_lesson_buckets()
#
#     # 🟢 Step 1: Assign Group Lessons (Priority)
#     for lesson in group_lessons:
#         instructor_found = False
#         prioritized_instructors = get_prioritized_instructors(lesson.swim_style)
#         for instructor in prioritized_instructors:
#             if lesson.swim_style in instructor.swim_style and instructor.assign_lesson(lesson):
#                 assigned_lessons.append(lesson)
#                 instructor_found = True
#                 break  # Stop searching once assigned
#
#         if not instructor_found:
#             unassigned_lessons.append(lesson)  # No available instructor → Move to unassigned list
#
#     # 🔵 Step 2: Assign Private Lessons (Strictly Private)
#     for lesson in private_lessons:
#         instructor_found = False
#         prioritized_instructors = get_prioritized_instructors(lesson.swim_style)
#         for instructor in prioritized_instructors:
#             if lesson.swim_style in instructor.swim_style and instructor.assign_lesson(lesson):
#                 assigned_lessons.append(lesson)
#                 instructor_found = True
#                 break
#
#         if not instructor_found:
#             unassigned_lessons.append(lesson)
#
#     # 🔴 Step 3: Assign Flexible Private Lessons
#     for lesson in flexible_private_lessons:
#         instructor_found = False
#         prioritized_instructors = get_prioritized_instructors(lesson.swim_style)
#
#         # 🔹 First, try to assign as private
#         for instructor in prioritized_instructors:
#             if lesson.swim_style in instructor.swim_style and instructor.assign_lesson(lesson):
#                 assigned_lessons.append(lesson)
#                 instructor_found = True
#                 break
#
#                 # 🔹 If no private slot → Try to merge with a group lesson
#         if not instructor_found:
#             for group in group_lessons:
#                 if group.swim_style == lesson.swim_style and len(group.students) < 10:  # Max group size: 10
#                     group.students.extend(lesson.students)
#                     lesson.students[0].assigned_lesson = group
#                     instructor_found = True
#                     break
#
#         if not instructor_found:
#             unassigned_lessons.append(lesson)  # No slot available
#
#
# @app.get("/len_students")
# def get_len_students():
#     return len(students)
#
#
# @app.post("/submit_student")
# def submit_student(student: Student):
#     # Check if student already exists (avoid duplicates)
#     if any(s.name == student.name for s in students):
#         return {"message": f"Student {student.name} is already in the list."}
#
#     # Prevent exceeding the maximum allowed students
#     if len(students) >= max_students:
#         return {"message": "Maximum student limit reached. No more students can be added."}
#
#     students.append(student)
#
#     return {"message": f"Student {student.name} added. {max_students - len(students)} more student spots available."}
#
# @app.get("/schedule")
# def get_schedule():
#     """
#     Returns the assigned and unassigned lessons.
#     """
#     global students
#
#     # 🟢 Load test students automatically if empty (for easier testing)
#     if not students:
#         students.extend(test_students)
#
#     assign_lessons()
#     return {
#         "assigned_lessons": [
#             {
#                 "lesson_id": lesson.lesson_id,
#                 "lesson_type": lesson.lesson_type,
#                 "swim_style": lesson.swim_style,
#                 "instructor": lesson.instructor.name if lesson.instructor else None,
#                 "students": [student.name for student in lesson.students],
#                 "day": lesson.day,
#                 "start_time": lesson.start_time.strftime("%H:%M") if lesson.start_time else None,
#                 "end_time": lesson.end_time.strftime("%H:%M") if lesson.end_time else None,
#             }
#             for lesson in assigned_lessons
#         ],
#         "unassigned_lessons": [
#             {
#                 "lesson_id": lesson.lesson_id,
#                 "lesson_type": lesson.lesson_type,
#                 "swim_style": lesson.swim_style,
#                 "students": [student.name for student in lesson.students],
#             }
#             for lesson in unassigned_lessons
#         ],
#     }
#
# @app.on_event("startup")
# def reset_data_on_startup():
#     """
#     This function runs automatically when the backend starts.
#     It resets all stored data to ensure nothing persists from previous runs.
#     """
#     global students, assigned_lessons, unassigned_lessons
#     students.clear()
#     assigned_lessons.clear()
#     unassigned_lessons.clear()
#     print("🔄 Backend restarted: Cleared all students and lessons")
#
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# version 2

# import json
# import uvicorn
# from fastapi import FastAPI
# from typing import List
# from datetime import time
# from fastapi.middleware.cors import CORSMiddleware
# from models import Instructor, Student, Lesson
# from test_data import test_students
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all domains (Change this in production)
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )
#
# #Global variables
#
# max_students = 30
# # Temporary storage for students before scheduling
# students: set[Student] = set()
# # Global variable for storing students by their lesson preference
# students_by_preference = {
#     "private": [],
#     "flexible_private": [],
#     "group": [],
#     "flexible_group": []
# }
#
#
# # Instructor Data
# instructors = [
#     Instructor(
#         name="Yoni",
#         swim_style=["breaststroke", "butterfly"],  # Can teach only these
#         availability=[
#             {"day": "Tuesday", "start": time(8, 0), "end": time(15, 0)},
#             {"day": "Wednesday", "start": time(8, 0), "end": time(15, 0)},
#             {"day": "Thursday", "start": time(8, 0), "end": time(15, 0)},
#         ]
#     ),
#     Instructor(
#         name="Yotam",
#         swim_style=["freestyle", "breaststroke", "butterfly", "backstroke"],  # Can teach all styles
#         availability=[
#             {"day": "Monday", "start": time(16, 0), "end": time(20, 0)},
#             {"day": "Thursday", "start": time(16, 0), "end": time(20, 0)}
#         ]
#     ),
#     Instructor(
#         name="Johnny",
#         swim_style=["freestyle", "breaststroke", "butterfly", "backstroke"],  # Can teach all styles
#         availability=[
#             {"day": "Sunday", "start": time(10, 0), "end": time(19, 0)},
#             {"day": "Tuesday", "start": time(10, 0), "end": time(19, 0)},
#             {"day": "Thursday", "start": time(10, 0), "end": time(19, 0)}
#         ]
#     )
# ]
#
# assigned_lessons: List[Lesson] = []
# unassigned_lessons: List[Lesson] = []
#
#
# def create_lesson_buckets():
#     """
#     Organizes students into categorized lesson buckets.
#     - group_lessons: Lessons with 1-10 students.
#     - private_lessons: Lessons with exactly 1 student.
#     - flexible_private_lessons: Students who prefer private but might be moved to a group.
#     """
#     global students_by_preference  # Use the global student list
#
#     group_lessons = []  # Holds all grouped lessons
#     private_lessons = []  # Holds strictly private lessons
#     temporary_flexible_groups = []  # Holds private-preferred students
#     total_lessons = 0
#
#     for student in (students_by_preference["group"] +
#                     students_by_preference["flexible_group"] +
#                     students_by_preference["flexible_private"]):
#         assigned = False  # Track whether the student has been placed in a lesson
#
#         # Group Lessons: Try to fit student into an existing lesson
#         for lesson in group_lessons:
#             if lesson.swim_style == student.swim_style and len(lesson.students) < 10:  # Group limit: 10 students
#                 lesson.students.append(student)
#                 student.assigned_lesson = lesson
#                 assigned = True
#                 break  # Stop once assigned
#
#         # If no suitable group found, create a new group lesson
#         if not assigned:
#             new_group = Lesson(
#                 lesson_id=total_lessons,
#                 lesson_type="group",
#                 swim_style=student.swim_style,
#                 students=[student],
#             )
#             total_lessons += 1
#             student.assigned_lesson = new_group
#
#             if student.lesson_type == "flexible_private":
#                 temporary_flexible_groups.append(new_group)
#             else:
#                 group_lessons.append(new_group)
#
#     # Step 2: Assign private lessons only for strict private students
#     for student in students_by_preference["private"]:
#         new_private = Lesson(
#             lesson_id=total_lessons,
#             lesson_type=student.lesson_type,
#             swim_style=student.swim_style,
#             students=[student],
#         )
#         total_lessons += 1
#         student.assigned_lesson = new_private
#         private_lessons.append(new_private)
#
#     return group_lessons, private_lessons, temporary_flexible_groups
#
#
# def get_prioritized_instructors(swim_style):
#     """
#     Returns the prioritized order of instructors:
#     - If **breaststroke or butterfly**, prioritize **Yoni first**.
#     - Otherwise, prioritize **Johnny and Yotam first**, but balance their workload:
#       - If Johnny has more than twice the lessons of Yotam, Yotam gets prioritized.
#       - Otherwise, Johnny is prioritized.
#     """
#     # Get instructor references
#     yotam = next((i for i in instructors if i.name == "Yotam"), None)
#     johnny = next((i for i in instructors if i.name == "Johnny"), None)
#
#     # Condition: If Johnny has more than twice the lessons of Yotam, switch priority
#     if johnny and yotam and len(johnny.lessons) > 2 * len(yotam.lessons):
#         johnny, yotam = yotam, johnny  # Swap their order
#
#     if swim_style in ["breaststroke", "butterfly"]:
#         # Prioritize Yoni first, followed by the balanced order of Johnny and Yotam
#         return sorted(instructors, key=lambda i: (i.name != "Yoni", i != johnny))
#     else:
#         # Prioritize Johnny and Yotam first (with workload balancing), then Yoni
#         return sorted(instructors, key=lambda i: (i.name == "Yoni", i != johnny))
#
#
# def second_iteration_assign_lessons(temporary_flexible_groups):
#     """Optimize flexible private students by moving them into private lessons when possible."""
#     global assigned_lessons
#
#     # 🟢 Sort groups by size (smallest first)
#     sorted_flexible_groups = sorted(temporary_flexible_groups, key=lambda g: len(g.students))
#
#     for group in sorted_flexible_groups:
#         if group not in assigned_lessons: continue
#
#         while group.students:
#             student = group.students[0]
#
#             # 🔵 Try to assign a private lesson
#             new_private = Lesson(
#                 lesson_id=len(assigned_lessons) + 1,
#                 lesson_type="private",
#                 swim_style=student.swim_style,
#                 students=[student],
#             )
#
#             if assign_lesson_to_instructor(new_private):  # ✅ Private lesson assigned
#                 student.assigned_lesson = new_private
#                 group.students.pop(0)  # Remove student immediately
#
#
#                 # 🔴 If only one student remains, convert group to private lesson
#                 if len(group.students) == 1:
#                     last_student = group.students.pop()
#                     new_private_last = Lesson(
#                         lesson_id=len(assigned_lessons) + 1,
#                         lesson_type="private",
#                         swim_style=last_student.swim_style,
#                         students=[last_student],
#                     )
#                     new_private_last.assign_instructor_and_time(group.instructor, group.day, group.start_time)
#                     last_student.assigned_lesson = new_private_last
#                     assigned_lessons.remove(group)
#                     group.instructor.lessons.remove(group)
#                     break  # Stop checking this group since it no longer exists
#
#                 continue  # Check next student without increasing i
#             else:
#                 unassigned_lessons.remove(new_private)
#                 break
#
#
# def assign_lesson_to_instructor(lesson):
#     """Tries to assign a lesson to an instructor based on prioritization.
#        Returns True if assigned, False otherwise."""
#     prioritized_instructors = get_prioritized_instructors(lesson.swim_style)
#
#     for instructor in prioritized_instructors:
#         if lesson.swim_style in instructor.swim_style and instructor.assign_lesson(lesson):
#             assigned_lessons.append(lesson)
#             return True  # ✅ Lesson successfully assigned
#
#     unassigned_lessons.append(lesson)  # ❌ No available instructor
#     return False  # Assignment failed
#
#
# def first_iteration_assign_lessons(group_lessons, private_lessons, temporary_flexible_groups):
#     """First pass: Assign group lessons, then temporary flexible groups, then private lessons."""
#     global assigned_lessons, unassigned_lessons
#     assigned_lessons.clear()
#     unassigned_lessons.clear()
#
#     # 🟢 Step 1: Assign Group Lessons (Priority)
#     for lesson in group_lessons:
#         assign_lesson_to_instructor(lesson)
#
#     # 🔴 Step 2: Assign Temporary Flexible Groups (Created from Flexible Private Students)
#     for lesson in temporary_flexible_groups:
#         assign_lesson_to_instructor(lesson)
#
#     # 🔵 Step 3: Assign Strictly Private Lessons
#     for lesson in private_lessons:
#         assign_lesson_to_instructor(lesson)
#
#
# def assign_lessons():
#     """Step 1: First-pass assignment (group → flexible groups → private).
#        Step 2: Second-pass optimization (adjust flexible private students into private lessons)."""
#
#     group_lessons, private_lessons, temporary_flexible_groups = create_lesson_buckets()
#     first_iteration_assign_lessons(group_lessons, private_lessons, temporary_flexible_groups)
#
#     # Second iteration (we will implement this separately)
#     second_iteration_assign_lessons(temporary_flexible_groups)
#
#
# @app.get("/len_students")
# def get_len_students():
#     return len(students)
#
#
# @app.post("/submit_student")
# def submit_student(student: Student):
#
#     global students, students_by_preference
#
#     # Ensure lesson_type is valid
#     valid_lesson_types = {"private", "flexible_private", "group", "flexible_group"}
#     if student.lesson_type not in valid_lesson_types:
#         return {"message": "Invalid lesson type provided."}
#
#     # Check if student already exists (avoid duplicates)
#     if student in students:
#         return {"message": f"Student {student.name} is already in the list."}
#
#     # Prevent exceeding the maximum allowed students
#     if len(students) >= max_students:
#         return {"message": "Maximum student limit reached. No more students can be added."}
#
#     students.add(student)
#
#     # Categorize student based on lesson type safely
#     students_by_preference.setdefault(student.lesson_type, []).append(student)
#
#     print("\n📌 Updated students_by_preference:")
#     print(json.dumps({k: [s.name for s in v] for k, v in students_by_preference.items()}, indent=4))
#
#     return {"message": f"Student {student.name} added. {max_students - len(students)} more student spots available."}
#
# @app.get("/schedule")
# def get_schedule():
#     """
#     Returns the assigned and unassigned lessons.
#     """
#     global students
#
#     # 🟢 Load test students automatically if empty (for easier testing)
#     if not students:
#         students.extend(test_students)
#
#     assign_lessons()
#     return {
#         "assigned_lessons": [
#             {
#                 "lesson_id": lesson.lesson_id,
#                 "lesson_type": lesson.lesson_type,
#                 "swim_style": lesson.swim_style,
#                 "instructor": lesson.instructor.name if lesson.instructor else None,
#                 "students": [student.name for student in lesson.students],
#                 "day": lesson.day,
#                 "start_time": lesson.start_time.strftime("%H:%M") if lesson.start_time else None,
#                 "end_time": lesson.end_time.strftime("%H:%M") if lesson.end_time else None,
#             }
#             for lesson in assigned_lessons
#         ],
#         "unassigned_lessons": [
#             {
#                 "lesson_id": lesson.lesson_id,
#                 "lesson_type": lesson.lesson_type,
#                 "swim_style": lesson.swim_style,
#                 "students": [student.name for student in lesson.students],
#             }
#             for lesson in unassigned_lessons
#         ],
#     }
#
# @app.on_event("startup")
# def reset_data_on_startup():
#     """
#     This function runs automatically when the backend starts.
#     It resets all stored data to ensure nothing persists from previous runs.
#     """
#     global students, assigned_lessons, unassigned_lessons
#     students.clear()
#     assigned_lessons.clear()
#     unassigned_lessons.clear()
#     print("🔄 Backend restarted: Cleared all students and lessons")
#
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
