import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, FlatList, TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Notifications from 'expo-notifications';
import axios from 'axios';

const MedicationScreen = () => {
  const [name, setName] = useState('');
  const [interval, setInterval] = useState('');
  const [dose, setDose] = useState('');
  const [pillsLeft, setPillsLeft] = useState('');
  const [medications, setMedications] = useState([]);
  const timerRef = useRef(null);

  useEffect(() => {
    const initializeNotifications = async () => {
      await Notifications.requestPermissionsAsync();
    };

    const loadMedications = async () => {
      const storedMedications = await AsyncStorage.getItem('medications');
      if (storedMedications) {
        setMedications(JSON.parse(storedMedications));
      }
    };

    initializeNotifications();
    loadMedications();
  }, []);

  useEffect(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    timerRef.current = setInterval(() => {
      setMedications(prevMedications => {
        const now = new Date();
        const updatedMedications = prevMedications.map(med => {
          const timeDiff = Math.max(0, Math.floor((new Date(med.nextDose) - now) / 1000));
          if (timeDiff === 0) {
            sendSms(`It's time to take your ${med.name}.`);
            med.nextDose = new Date(now.getTime() + med.interval * 60000).toISOString();
            med.pillsLeft -= med.dose;
            if (med.pillsLeft < 3) {
              sendSms(`You have less than 3 pills of ${med.name} left. Please buy more.`);
            }
          }
          return { ...med, timeDiff };
        });
        AsyncStorage.setItem('medications', JSON.stringify(updatedMedications));
        return updatedMedications;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, []);

  const handleAddReminder = async () => {
    if (!name || !interval || !dose || !pillsLeft) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    const newMedication = {
      id: Date.now().toString(),
      name,
      interval: parseInt(interval, 10), // minutes
      dose: parseInt(dose, 10),
      pillsLeft: parseInt(pillsLeft, 10),
      nextDose: new Date().toISOString(),
      timeDiff: parseInt(interval, 10) * 60, // initial countdown
    };

    const updatedMedications = [...medications, newMedication];
    setMedications(updatedMedications);
    await AsyncStorage.setItem('medications', JSON.stringify(updatedMedications));

    Alert.alert('Success', 'Reminder added successfully!');
    setName('');
    setInterval('');
    setDose('');
    setPillsLeft('');
  };

  const sendSms = async (message) => {
    try {
      await axios.post('http://192.168.10.19:8080/send-sms', { message, to: "573157913013" });
    } catch (error) {
      console.error('Error sending SMS:', error);
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.row}>
      <Text style={styles.text}>{item.name}</Text>
      <Text style={styles.text}>{formatTime(item.timeDiff)}</Text>
      <TouchableOpacity onPress={() => deleteItem(item)}>
        <Text style={styles.deleteButton}>Delete</Text>
      </TouchableOpacity>
    </View>
  );

  const deleteItem = async (item) => {
    const updatedMedications = medications.filter((med) => med.id !== item.id);
    setMedications(updatedMedications);
    await AsyncStorage.setItem('medications', JSON.stringify(updatedMedications));
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Add Medication Reminder</Text>
      <TextInput
        style={styles.input}
        placeholder="Medication Name"
        value={name}
        onChangeText={setName}
      />
      <TextInput
        style={styles.input}
        placeholder="Interval (minutes)"
        value={interval}
        onChangeText={setInterval}
        keyboardType="numeric"
      />
      <TextInput
        style={styles.input}
        placeholder="Dose (pills per dose)"
        value={dose}
        onChangeText={setDose}
        keyboardType="numeric"
      />
      <TextInput
        style={styles.input}
        placeholder="Pills Left"
        value={pillsLeft}
        onChangeText={setPillsLeft}
        keyboardType="numeric"
      />
      <Button title="Add Reminder" onPress={handleAddReminder} />
      <FlatList
        data={medications}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
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
    marginBottom: 20,
    paddingLeft: 8,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 10,
    backgroundColor: '#f8f8f8',
    borderBottomWidth: 1,
    borderColor: '#eee',
  },
  text: {
    fontSize: 18,
  },
  deleteButton: {
    color: 'red',
  },
});

export default MedicationScreen;
