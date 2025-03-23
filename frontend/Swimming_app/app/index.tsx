import React, {useEffect, useState} from "react";
import {View} from "react-native";
import StudentSubmissionScreen from "./StudentSubmissionScreen";
import ScheduleScreen from "./ScheduleScreen";
import {API_URL} from "../constants/api";

/**
 * Root component of the application.
 *
 * Controls the conditional rendering between the student submission form
 * and the final schedule screen.
 */
const App: React.FC = () => {
    const [studentsCount, setStudentsCount] = useState(0);
    const [showSchedule, setShowSchedule] = useState(false);

    /**
     * Fetches the current number of submitted students from the backend.
     * If the number reaches 30, the schedule screen is automatically shown.
     */
    const fetchStudentCount = async () => {
        try {
            const response = await fetch(`${API_URL}/len_students`);
            const count = await response.json();
            setStudentsCount(count);

            if (count >= 30) {
                setShowSchedule(true);
            }
        } catch (error) {
            console.error("Error fetching student count:", error);
        }
    };

    // Fetch the student count once when the app mounts
    useEffect(() => {
        fetchStudentCount();
    }, []);

    return (
        <View style={{flex: 1}}>
            {showSchedule ? (
                <ScheduleScreen setShowSchedule={setShowSchedule}/>
            ) : (
                <StudentSubmissionScreen
                    setShowSchedule={setShowSchedule}
                    fetchStudentCount={fetchStudentCount}
                />
            )}
        </View>
    );
};

export default App;
