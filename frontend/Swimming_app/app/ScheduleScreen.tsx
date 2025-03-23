import React, {useEffect, useState} from "react";
import {Alert, Button, Modal, ScrollView, Text, TouchableOpacity, View} from "react-native";
import WeekView, {WeekViewEvent} from "react-native-week-view";
import {API_URL} from "../constants/api";
import {Ionicons} from '@expo/vector-icons';

// Defines a color for each instructor, used to differentiate events on the calendar
const instructorColors: { [key: string]: string } = {
    Johnny: "blue",
    Yotam: "red",
    Yoni: "green",
};

/**
 * Converts a weekday and time (hour + optional minutes) into a fixed Date object
 * relative to a known static week (starting from March 3, 2024 – Sunday).
 *
 * This allows us to display recurring weekly lessons without using actual current dates.
 *
 * @param weekday - Day of the week (e.g., "Monday", "Tuesday")
 * @param hour - Hour of the event (24-hour format)
 * @param minutes - Optional minutes value (defaults to 0)
 * @returns A Date object fixed to a reference week
 */
const createFixedWeekDate = (weekday: string, hour: number, minutes: number = 0): Date => {
    const fixedReferenceDate = new Date("2024-03-03T00:00:00Z"); // Fixed Monday reference
    const weekdays: Record<string, number> = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6
    };

    const targetDay = weekdays[weekday];
    if (targetDay === undefined) return new Date(); // Fallback to current date if invalid

    // Adjust to correct weekday
    const eventDate = new Date(fixedReferenceDate);
    eventDate.setDate(fixedReferenceDate.getDate() + (targetDay - fixedReferenceDate.getDay()));

    // Set time
    eventDate.setHours(hour, minutes, 0, 0);
    return eventDate;
};

/**
 * Displays the weekly schedule and allows the user to:
 * - View assigned lessons in a calendar view
 * - View unassigned students in a modal
 * - Navigate back to the student submission screen
 */
const ScheduleScreen: React.FC<{ setShowSchedule: (value: boolean) => void }> = ({setShowSchedule}) => {
    const [events, setEvents] = useState<WeekViewEvent[]>([]);
    const [unassignedLessons, setUnassignedLessons] = useState<any[]>([]);
    const [modalVisible, setModalVisible] = useState(false);
    const [showAll, setShowAll] = useState(false);

    /**
     * Fetches the schedule from the backend on component mount
     * and transforms the lesson data into WeekView-compatible events.
     */
    useEffect(() => {
        const fetchSchedule = async () => {
            try {
                const response = await fetch(`${API_URL}/schedule`);
                const data = await response.json();

                // Transform assigned lessons into events
                const transformedEvents: WeekViewEvent[] = data.assigned_lessons.map((lesson: any) => {
                    const [startHours, startMinutes] = lesson.start_time.split(":").map(Number);
                    const [endHours, endMinutes] = lesson.end_time.split(":").map(Number);

                    return {
                        id: lesson.lesson_id,
                        startDate: createFixedWeekDate(lesson.day, startHours, startMinutes),
                        endDate: createFixedWeekDate(lesson.day, endHours, endMinutes),
                        color: instructorColors[lesson.instructor] || "gray",
                        instructor: lesson.instructor,
                        lesson_type: lesson.lesson_type,
                        swim_style: lesson.swim_style,
                        students: lesson.students || [],
                        day: lesson.day,
                        start_time: lesson.start_time,
                        end_time: lesson.end_time,
                        description: `${lesson.instructor} - ${["private", "flexible_private"].includes(lesson.lesson_type) ? "'P'" : "'G'"}`,
                        eventKind: "standard",
                        resolveOverlap: "lane",
                        stackKey: `lesson-${lesson.lesson_id}`,
                        style: {marginBottom: 5} // Adds separation
                    };
                });

                setEvents(transformedEvents);
                setUnassignedLessons(data.unassigned_lessons);
            } catch (error) {
                console.error("Error fetching schedule:", error);
            }
        };

        fetchSchedule();
    }, []);

    return (
        <ScrollView style={{flex: 1, padding: 10}}>
            {/* Header with Back Button and Title */}
            <View style={{
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "space-between",
                paddingHorizontal: 15,
                marginTop: 10
            }}>
                {/* Back Button */}
                <TouchableOpacity
                    onPress={() => setShowSchedule(false)}
                    style={{
                        backgroundColor: "#e0e0e0",
                        borderRadius: 20,
                        padding: 6,
                    }}
                >
                    <Ionicons name="arrow-back" size={24} color="black"/>
                </TouchableOpacity>

                {/* Title centered in flex space */}
                <View style={{flex: 1, alignItems: "center", marginRight: 40 /* accounts for arrow size */}}>
                    <Text style={{fontSize: 20, fontWeight: "bold", textAlign: "center"}}>
                        Weekly Schedule
                    </Text>
                </View>
            </View>

            {/* Button to show unassigned lessons */}
            <View style={{margin: 15}}>
                <Button title="Show Unassigned Lessons" onPress={() => setModalVisible(true)} color="orange"/>
            </View>

            <View style={{width: "105%", marginLeft: -15}}>
                {/* WeekView with lessons */}
                <WeekView
                    events={events}
                    fixedHorizontally={true}
                    showTitle={false}
                    formatDateHeader="ddd"
                    selectedDate={createFixedWeekDate("Monday", 12)}
                    numberOfDays={5}
                    pageStartAt={{weekday: 1, left: 1}}
                    beginAgendaAt={8 * 60}
                    endAgendaAt={22 * 60}
                    eventContainerStyle={{
                        marginBottom: 8,
                        borderRadius: 5,
                        borderWidth: 1,
                        borderColor: "#ccc",
                    }}
                    onEventPress={(event) => Alert.alert(
                        `Lesson ID: ${event.id}`,
                        `Day: ${event.day}\nTime: ${event.start_time} - ${event.end_time}\n` +
                        `Instructor: ${event.instructor}\nLesson type: ${event.lesson_type} (${["private", "flexible_private"].includes(event.lesson_type) ? "'P'" : "'G'"})\nSwim style: ${event.swim_style}\n` +
                        `Students: ${event.students.length > 0 ? event.students.join(", ") : "None"}`
                    )}
                />
            </View>

            {/* Modal for Unassigned Lessons */}
            <Modal
                animationType="slide"
                transparent={true}
                visible={modalVisible}
                onRequestClose={() => setModalVisible(false)}
            >
                <View style={{
                    flex: 1,
                    justifyContent: "center",
                    alignItems: "center",
                    backgroundColor: "rgba(0,0,0,0.5)"
                }}>
                    <View style={{
                        backgroundColor: "white",
                        padding: 20,
                        borderRadius: 10,
                        width: "80%",
                        maxHeight: "80%"
                    }}>
                        <Text style={{fontSize: 20, fontWeight: "bold", textAlign: "center", marginBottom: 10}}>
                            Unassigned Students
                        </Text>

                        <ScrollView style={{maxHeight: 400}}>
                            {unassignedLessons.length > 0 ? (
                                unassignedLessons.slice(0, showAll ? unassignedLessons.length : 5).map((lesson, index) => (
                                    <View key={index}
                                          style={{marginBottom: 10, padding: 10, borderWidth: 1, borderRadius: 5}}>
                                        <Text>Students: {lesson.students.length > 0 ? lesson.students.join(", ") : "None"}</Text>
                                        <Text>Type: {lesson.lesson_type} - {lesson.swim_style}</Text>
                                    </View>
                                ))
                            ) : (
                                <Text style={{textAlign: "center", fontSize: 16}}>No unassigned students.</Text>
                            )}
                        </ScrollView>

                        {/* Show More / Show Less Button */}
                        {unassignedLessons.length > 5 && (
                            <Button
                                title={showAll ? "Show Less" : "Show More"}
                                onPress={() => setShowAll(!showAll)}
                                color="blue"
                            />
                        )}
                        {/* Close Modal Button */}
                        <View style={{marginTop: 20}}>
                            <Button title="Close" onPress={() => setModalVisible(false)} color="red"/>
                        </View>
                    </View>
                </View>
            </Modal>
        </ScrollView>
    );
};

export default ScheduleScreen;
