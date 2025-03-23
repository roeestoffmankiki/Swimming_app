import React, {useState} from "react";
import {Text, View} from "react-native";
import {Picker} from "@react-native-picker/picker";

const TestPicker = () => {
    const [selectedValue, setSelectedValue] = useState("group");

    return (
        <View>
            <Text>Select an Option:</Text>
            <Picker
                selectedValue={selectedValue}
                onValueChange={(itemValue) => setSelectedValue(itemValue)}
            >
                <Picker.Item label="Group" value="group"/>
                <Picker.Item label="Private" value="private"/>
            </Picker>
        </View>
    );
};

export default TestPicker;
