# 🏊 Swimming Lesson Scheduler App

A full-stack scheduling system for managing swimming lessons.
Students can submit their availability and preferences (group/private/flexible and swim styles),
and the app intelligently assigns them to lessons based on instructor availability,
swim style, and group size.

---

## 📁 Project Structure

```
.
├── backend                # FastAPI server and scheduling logic
│   ├── main.py            # Main API logic
│   ├── models.py          # Student, Instructor, Lesson models
│   └── test_data.py       # Test student data
├── frontend/Swimming_app  # React Native (Expo) frontend
│   └── App.tsx, screens, styles
```

---

## 🚀 How to Run the App

### 1. Backend (FastAPI)

Open a terminal and run:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> The server will start at: `http://localhost:8000`

---

### 2. Frontend (React Native with Expo)

Open a **separate terminal** and run:

```bash
cd frontend/Swimming_app
npx expo start -c
```

> This opens the Expo dev tools. You can run the app on your phone using the Expo Go app,
> or launch an emulator.

---

## 🧠 Assignment Logic Explained

The backend scheduling algorithm assigns students to swim lessons using the following steps:

### Step 1: Student Submission
Students are submitted via the frontend, including:
- Full name
- Desired lesson type: `group`, `private`, `flexible_group`, or `flexible_private`
- Preferred swim styles (e.g., freestyle, butterfly)
- Weekly availability (day and time ranges)

### Step 2: Reset & Schedule
When the `/schedule` endpoint is called:
1. All previously assigned lessons are cleared.
2. Students remain in memory.
3. Scheduling begins from scratch.

### Step 3: Group Lesson Assignment
- The system finds time slots with the **largest groups of students** by swim style.
- A lesson is created for each large group and an instructor who can teach that style.
- Students in that lesson are removed from all other time slots.

### Step 4: Private Lesson Assignment
- The system finds time slots with **fewest students**.
- Chooses the student with the **lowest availability score**.
- Matches them with an available instructor and swim style.
- Creates a private lesson.

### Step 5: Flexible Private Fallback
- Students who asked for `flexible_private` are first assigned to private lessons.
- For those who haven't found a slot trys to get matched to any existing group lesson that fits:
  - Swim style
  - Availability
- If no match is found, they're marked as **unassigned**.

---

## ✅ Features

- Smart assignment based on availability and preferences
- Flexible lesson types with option to prefer (group, private, flexible)
- Handles up to 30 students (could handle more no problem)
- Beautiful weekly schedule view
- Real-time preview of unassigned students
- Can go back to submit page, and add new students

---
