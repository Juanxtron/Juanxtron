import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, ScrollView } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { auth, database } from '../config/firebaseConfig'; // Asegúrate de importar tu configuración de Firebase
import { ref, onValue } from 'firebase/database'; // Asegúrate de importar estas funciones
import { Video } from 'expo-av'; // Importar el componente Video de expo-av

const MoodTrackerScreen = () => {
  const [mood, setMood] = useState('');
  const [sentiment, setSentiment] = useState('');
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [emergencyContact, setEmergencyContact] = useState(null);
  const [videoSource, setVideoSource] = useState(require('../assets/videos/Default.mp4'));

  useEffect(() => {
    const user = auth.currentUser;
    if (user) {
      const userRef = ref(database, 'users/' + user.uid);
      onValue(userRef, (snapshot) => {
        const data = snapshot.val();
        if (data) {
          setIsAuthorized(data.isAuthorized);
          setEmergencyContact(data.emergencyContact);
        }
      });
    }
  }, []);

  const handleSubmit = async () => {
    try {
      const response = await fetch('http://192.168.10.19:5000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mood, emergencyContact }),
      });

      const data = await response.json();
      setSentiment(data.sentiment);

      if (data.sentiment.toLowerCase() === 'depressed') {
        setVideoSource(require('../assets/videos/depresivo.mp4'));
        Alert.alert('Message', `We understand your situation and want to tell you that we are with you. Also, your mom is very proud of you(${emergencyContact}). If you need help, contact 123 (Colombian emergency number).`);
      } else if (data.sentiment.toLowerCase() === 'neutral' || data.sentiment.toLowerCase() === 'positive') {
        setVideoSource(require('../assets/videos/sample.mp4'));
        Alert.alert('Message', `La capacidad de entusiasmo es signo de salud espiritual`);
      } else {
        Alert.alert('Message', 'La excelencia no es un acto, es un hábito');
      }
    } catch (error) {
      console.error('Error fetching sentiment:', error);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Video
        source={videoSource} // Cambia la fuente del video según el sentimiento
        rate={1.0}
        volume={0.0} // Desactivar el sonido
        isMuted={true} // Asegurarse de que el sonido está desactivado
        resizeMode="cover"
        shouldPlay
        isLooping
        style={styles.video}
      />
      <View style={styles.formContainer}>
        <Text style={styles.label}>How do you feel today?</Text>
        <TextInput
          style={styles.input}
          value={mood}
          onChangeText={setMood}
          placeholder="Enter your mood"
        />
        <Button title="Submit" onPress={handleSubmit} />
        {sentiment !== '' && sentiment.toLowerCase() !== 'depressed' && (
          <>
          </>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  video: {
    width: '100%',
    height: 300,
  },
  formContainer: {
    marginTop: 20,
    backgroundColor: '#f7f7f7',
    padding: 20,
    borderRadius: 10,
  },
  label: {
    fontSize: 18,
    marginBottom: 10,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 20,
    paddingLeft: 8,
  },
  result: {
    marginTop: 10,
    fontSize: 16,
  },
});

export default MoodTrackerScreen;
