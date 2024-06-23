import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, ScrollView } from 'react-native';
import CheckBox from 'expo-checkbox';
import { useRouter } from 'expo-router';
import { auth, database } from '../config/firebaseConfig';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { ref, set, get, child } from 'firebase/database';

const RegisterScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isAddingEmergencyContact, setIsAddingEmergencyContact] = useState(false);
  const [users, setUsers] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const dbRef = ref(database);
        const snapshot = await get(child(dbRef, 'users'));
        if (snapshot.exists()) {
          const userList = Object.values(snapshot.val());
          setUsers(userList);
        } else {
          console.log('No data available');
        }
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };

    fetchUsers();
  }, []);

  const handleRegister = async () => {
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      await set(ref(database, 'users/' + user.uid), {
        email,
        isAuthorized,
        emergencyContact: isAddingEmergencyContact ? emergencyContact : null,
      });

      Alert.alert('Success', 'User registered successfully!');
      router.push('/LoginScreen'); // Redirige a la pantalla de inicio de sesión
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Register Screen</Text>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <TextInput
        style={styles.input}
        placeholder="Confirm Password"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
      />
      <CheckBox
        value={isAddingEmergencyContact}
        onValueChange={setIsAddingEmergencyContact}
        style={styles.checkbox}
      />
      <Text style={styles.label}>Add Emergency Contact?</Text>
      {isAddingEmergencyContact && (
        <>
          <Text style={styles.hint}>
            (Country code followed by the phone number) (e.g., 573157913013)
          </Text>
          <TextInput
            style={styles.input}
            placeholder="Emergency Contact Number"
            value={emergencyContact}
            onChangeText={setEmergencyContact}
          />
        </>
      )}
      <CheckBox
        value={isAuthorized}
        onValueChange={setIsAuthorized}
        style={styles.checkbox}
      />
      <Text style={styles.label}>Authorize Emergency Contact?</Text>
      <Button title="Register" onPress={handleRegister} />
      <Button
        title="Already have an account? Log in"
        onPress={() => router.push('/LoginScreen')}
      />

    </ScrollView>
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
    marginBottom: 20,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginTop: 10,
    paddingLeft: 8,
  },
  checkbox: {
    marginTop: 10,
  },
  label: {
    fontSize: 16,
    marginTop: 10,
  },
  hint: {
    fontSize: 12,
    color: 'gray',
    marginTop: 5,
    marginBottom: 10,
  },
  usersContainer: {
    marginTop: 30,
  },
  userContainer: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'gray',
  },
});

export default RegisterScreen;


