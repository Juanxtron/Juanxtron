import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { auth, database } from '../config/firebaseConfig'; // Asegúrate de que la ruta sea correcta
import { updatePassword, reauthenticateWithCredential, EmailAuthProvider } from 'firebase/auth';
import { ref, set } from 'firebase/database';

const SettingsScreen = () => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [emergencyContact, setEmergencyContact] = useState('');
  const route = useRoute();
  const navigation = useNavigation();
  const { email, isAuthorized, oldEmergencyContact } = route.params;

  const handleChangePassword = async () => {
    try {
      const user = auth.currentUser;
      const credential = EmailAuthProvider.credential(user.email, currentPassword);

      await reauthenticateWithCredential(user, credential);
      await updatePassword(user, newPassword);
      Alert.alert('Success', 'Password updated successfully!');
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  const handleChangeEmergencyContact = async () => {
    try {
      const user = auth.currentUser;
      const userRef = ref(database, 'users/' + user.uid + '/emergencyContact');

      await set(userRef, emergencyContact);
      Alert.alert('Success', 'Emergency contact updated successfully!');
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Settings</Text>
      <TextInput
        style={styles.input}
        placeholder="Current Password"
        value={currentPassword}
        onChangeText={setCurrentPassword}
        secureTextEntry
      />
      <TextInput
        style={styles.input}
        placeholder="New Password"
        value={newPassword}
        onChangeText={setNewPassword}
        secureTextEntry
      />
      <Button title="Change Password" onPress={handleChangePassword} />
      <TextInput
        style={styles.input}
        placeholder="New Emergency Contact"
        value={emergencyContact}
        onChangeText={setEmergencyContact}
      />
      <Text style={styles.hint}>
        Country code followed by the phone number (e.g., 573157913013)
      </Text>
      <Button title="Change Emergency Contact" onPress={handleChangeEmergencyContact} />
    </View>
  );
};
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginTop: 10,
    paddingLeft: 8,
  },
});

export default SettingsScreen;

