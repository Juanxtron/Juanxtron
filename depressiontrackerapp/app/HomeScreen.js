import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons'; // Asegúrate de que tienes esta biblioteca instalada
import { auth } from '../config/firebaseConfig'; // Asegúrate de que la ruta sea correcta

const HomeScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { isAuthorized, emergencyContact } = route.params || {};

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Sweet Home</Text>
        <TouchableOpacity onPress={() => navigation.navigate('SettingsScreen', { email: auth.currentUser.email, isAuthorized, oldEmergencyContact: emergencyContact })}>
          <Ionicons name="settings-outline" size={30} color="black" />
        </TouchableOpacity>
      </View>
      <ScrollView horizontal={true} showsHorizontalScrollIndicator={false} style={styles.scrollView}>
        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('MoodTrackerScreen', { isAuthorized, emergencyContact })}>
          <Ionicons name="happy-outline" size={40} color="black" />
          <Text style={styles.menuText}>Mood Tracker</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('MedicationScreen', { isAuthorized, emergencyContact })}>
          <Ionicons name="medkit-outline" size={40} color="black" />
          <Text style={styles.menuText}>Medication</Text>
        </TouchableOpacity>
      </ScrollView>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  scrollView: {
    marginVertical: 20,
  },
  menuItem: {
    justifyContent: 'center',
    alignItems: 'center',
    width: 100,
    height: 100,
    marginRight: 20,
    backgroundColor: '#f5f5f5',
    borderRadius: 50,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.8,
    shadowRadius: 2,
    elevation: 1,
  },
  menuText: {
    marginTop: 10,
    fontSize: 14,
    textAlign: 'center',
  },
});

export default HomeScreen;
