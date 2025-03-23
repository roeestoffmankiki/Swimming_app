import React, {useState} from "react";
import {Alert, Button, Image, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View} from "react-native";
import {Dropdown} from "react-native-element-dropdown";
import {API_URL} from "../constants/api";
import {Checkbox} from "react-native-paper"; // ✅ Using react-native-paper for checkboxes

/**
 * Options for lesson types available in the dropdown menu.
 * Includes flexible preferences that may be resolved based on availability.
 */
const lessonTypeOptions = [
    {label: "Group", value: "group"},
    {label: "Private", value: "private"},
    {label: "Prefer Group", value: "flexible_group"},
    {label: "Prefer Private", value: "flexible_private"},
];

/**
 * Swim styles supported by both students and instructors.
 */
const swimStyleOptions = [
    {label: "Freestyle", value: "freestyle"},
    {label: "Breaststroke", value: "breaststroke"},
    {label: "Butterfly", value: "butterfly"},
    {label: "Backstroke", value: "backstroke"},
];

/**
 * Days of the week that students can choose for their availability.
 */
const daysOfWeek = [
    {label: "Sunday", value: "Sunday"},
    {label: "Monday", value: "Monday"},
    {label: "Tuesday", value: "Tuesday"},
    {label: "Wednesday", value: "Wednesday"},
    {label: "Thursday", value: "Thursday"},
];

const logo = require("../assets/images/cut2.png");

/**
 * StudentSubmissionScreen allows users to submit new students
 * by entering their name, lesson preferences, swim styles, and availability.
 * Once 30 students are submitted or pressing finish, the app switches to the schedule view.
 */
const StudentSubmissionScreen: React.FC<{
    setShowSchedule: (value: boolean) => void;
    fetchStudentCount: () => Promise<void>
}> = ({setShowSchedule, fetchStudentCount}) => {  // ✅ Row 19: Added fetchStudentCount

    // Form state
    const [name, setName] = useState("");
    const [lessonType, setLessonType] = useState(null);
    const [selectedSwimStyles, setSelectedSwimStyles] = useState<string[]>([]);
    const [selectedDay, setSelectedDay] = useState<string | null>(null);
    const [timeRanges, setTimeRanges] = useState<{ day: string; startTime: string; endTime: string }[]>([]);
    const [isTimePickerVisible, setTimePickerVisible] = useState(false);
    const [tempStartTime, setTempStartTime] = useState<string | null>(null);
    const [tempEndTime, setTempEndTime] = useState<string | null>(null);  // ✅ Add end time state

    /**
     * Submits the student form to the backend.
     * Validates that all fields are filled, formats availability,
     * and handles API errors gracefully.
     */
    const submitStudent = async () => {
        if (!name.trim() || !lessonType || selectedSwimStyles.length === 0 || timeRanges.length === 0) {
            Alert.alert("Error", "Please complete all fields.");
            return;
        }

        const formattedAvailability = timeRanges.map(({day, startTime, endTime}) => ({
            day,
            start: startTime,
            end: endTime,
        }));

        try {
            const response = await fetch(`${API_URL}/submit_student`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    name,
                    lesson_type: lessonType,
                    swim_style: selectedSwimStyles,
                    availability: formattedAvailability,
                }),
            });

            const data = await response.json(); // ✅ Parse JSON response

            if (!response.ok || data.message.includes("already in the list")) {
                // ✅ Check if the message is an error
                Alert.alert("Error", data.message);
                return;
            }

            Alert.alert("Success", data.message);
            // Reset all form states
            setName("");
            setLessonType(null);
            setSelectedSwimStyles([]);
            setTimeRanges([]); //  Clear selected time ranges (reset day buttons)
            setSelectedDay(null); //  Ensure no lingering selections
            fetchStudentCount();
        } catch (error) {
            console.error("Error submitting student:", error);
            Alert.alert("Error", "Failed to submit student.");
        }
    };

    /**
     * Opens the time selection modal for a chosen day.
     */
    const handleDayPress = (day: string) => {
        setSelectedDay(day);
        setTempStartTime(null);
        setTempEndTime(null);
        setTimePickerVisible(true);
    };


    return (
        <ScrollView contentContainerStyle={styles.scrollContainer}>
            <View style={styles.container}>
                {/* App Logo */}
                <Image source={logo} style={styles.logo}/>

                <Text style={styles.title}>Submit a Student</Text>

                {/* Name input */}
                <TextInput
                    style={styles.input}
                    placeholder="Enter student full name"
                    placeholderTextColor="gray"
                    value={name}
                    onChangeText={setName}
                />

                {/* Lesson Type Dropdown */}
                <Text style={styles.label}>Lesson Type:</Text>
                <Dropdown
                    style={styles.dropdown}
                    data={lessonTypeOptions}
                    labelField="label"
                    valueField="value"
                    placeholder="Select lesson type"
                    value={lessonType}
                    onChange={(item) => setLessonType(item.value)}
                />


                {/* Swim Style CheckBox */}
                <Text style={styles.label}>Select Swim Styles:</Text>
                <View style={styles.checkboxGrid}>
                    {swimStyleOptions.map((option, index) => (
                        <View key={option.value} style={styles.checkboxItem}>
                            <Checkbox.Android
                                status={selectedSwimStyles.includes(option.value) ? "checked" : "unchecked"}
                                onPress={() => {
                                    setSelectedSwimStyles((prev) =>
                                        prev.includes(option.value)
                                            ? prev.filter((s) => s !== option.value)
                                            : [...prev, option.value]
                                    );
                                }}
                                color="black" //  Checkmark color
                                uncheckedColor="black" //  Ensures white box before selection
                            />
                            <Text style={styles.checkboxLabel}>{option.label}</Text>
                        </View>
                    ))}
                </View>

                {/*  Availability time slots choosing */}
                <Text style={styles.label}>Select Available Days & Time:</Text>
                <View style={styles.checkboxGrid}>
                    {["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"].map((day) => (
                        <TouchableOpacity
                            key={day}
                            style={[
                                styles.dayButton,
                                timeRanges.some((range) => range.day === day) && styles.dayButtonSelected, // ✅ Change color if time is selected
                            ]}
                            onPress={() => handleDayPress(day)}

                            onLongPress={() => {
                                setTimeRanges(timeRanges.filter((range) => range.day !== day)); // ✅ Remove the selected day on long press
                            }}
                        >
                            <Text style={styles.dayText}>{day}</Text>
                        </TouchableOpacity>
                    ))}
                </View>

                {/* Modal time picker for availability */}
                {isTimePickerVisible && (
                    <View style={styles.modalContainer}>
                        <Text style={styles.modalTitle}>Select Time Range for {selectedDay}</Text>

                        {/* Start time dropdown */}
                        <Dropdown
                            data={[...Array(14)].map((_, i) => {
                                const hour = i + 8; // ✅ Start at 8:00
                                return {label: `${hour}:00`, value: `${hour}:00`};
                            })}
                            placeholder="Select Start Time"
                            labelField="label"
                            valueField="value"
                            value={tempStartTime}
                            onChange={(item) => setTempStartTime(item.value)}
                        />

                        {/* End time dropdown */}
                        <Dropdown
                            data={[...Array(14)].map((_, i) => {
                                const hour = i + 8; // ✅ Start at 8:00
                                return {label: `${hour}:00`, value: `${hour}:00`};
                            })}
                            placeholder="Select End Time"
                            labelField="label"
                            valueField="value"
                            value={tempEndTime}  // ✅ Separate state
                            onChange={(item) => {
                                if (tempStartTime && parseInt(item.value) > parseInt(tempStartTime)) {
                                    setTimeRanges([...timeRanges, {
                                        day: selectedDay!,
                                        startTime: tempStartTime,
                                        endTime: item.value
                                    }]);
                                    setTimePickerVisible(false);
                                    setSelectedDay(null);
                                    setTempStartTime(null);
                                    setTempEndTime(null);  // ✅ Reset end time after selection
                                } else {
                                    Alert.alert("Error", "End time must be after start time.");
                                }
                            }}
                        />


                        <Button title="Cancel" onPress={() => setTimePickerVisible(false)}/>
                    </View>
                )}

                {/* Submit + Go to Schedule */}
                <Button title="Submit Student" onPress={submitStudent}/>
                <View style={{marginTop: 20}}>
                    <Button title="Finish & View Schedule" onPress={() => setShowSchedule(true)} color="green"/>
                </View>
            </View>
        </ScrollView>
    );
};

// Improved Styles
const styles = StyleSheet.create({

    // Main container for ScrollView content
    scrollContainer: {flexGrow: 1, paddingBottom: 20,},

    // Core screen layout container
    container: {flex: 1, padding: 20, justifyContent: "center", backgroundColor: "#f5f5f5"},

    // Modal for selecting start/end times
    modalContainer: {
        position: "absolute",
        top: "30%",
        left: "10%",
        right: "10%",
        backgroundColor: "#ddd",
        padding: 20,
        borderRadius: 10,
        elevation: 5,
    },

    // Modal title styling
    modalTitle: {fontSize: 18, fontWeight: "bold", marginBottom: 10},

    // Style for day buttons (e.g., Monday–Friday)
    dayButton: {
        backgroundColor: "#ddd",
        padding: 10,
        borderRadius: 5,
        margin: 5,
        alignItems: "center",
    },

    // Highlight for selected day buttons
    dayButtonSelected: {backgroundColor: "#ADD8E6",},

    // Text inside day buttons
    dayText: {fontSize: 16},

    // Grid layout for checkboxes and day buttons
    checkboxGrid: {
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "space-between",
        marginVertical: 10,
        gap: 2, // ✅ Adds spacing between checkboxes
    },

    // Each swim style checkbox + label
    checkboxItem: {
        flexDirection: "row",
        alignItems: "center",
        width: "48%", // ✅ Two items per row
        marginVertical: 5,
    },

    // Label text for each checkbox
    checkboxLabel: {
        fontSize: 16,
        marginLeft: 20, // ✅ Moves label next to the box
    },

    // Section labels (e.g., “Lesson Type”, “Swim Styles”)
    label: {
        fontSize: 16,
        marginTop: 20,  // ✅ Added spacing
        marginBottom: 10, // ✅ Adds a gap between title and buttons
        fontWeight: "bold",
    },

    // Form title (top of screen)
    title: {fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 20},

    // Logo styling (centered with spacing)
    logo: {width: 366, height: 154, alignSelf: "center", marginBottom: 50, marginTop: 20},

    // Text input field (name)
    input: {borderWidth: 1, padding: 10, marginVertical: 10, borderRadius: 5, backgroundColor: "white"},

    // Dropdown (lesson type, time pickers)
    dropdown: {
        borderWidth: 1,
        borderColor: "#ccc",
        borderRadius: 5,
        padding: 10,
        backgroundColor: "white",
        marginBottom: 10
    },
});

export default StudentSubmissionScreen;