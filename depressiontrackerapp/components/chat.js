import React, { useState } from 'react';
import { View, Text, TextInput, Button } from 'react-native';

const Chat = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');

  const handleSubmit = async () => {
    const res = await fetch('http://localhost:5000/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mood: message }),
    });
    const data = await res.json();
    setResponse(data.sentiment);

    if (data.sentiment === "Depresivo") {
      alert("Se ha notificado a tu contacto de emergencia.");
      // Aquí podrías agregar la lógica para enviar un mensaje al contacto de emergencia
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Describe cómo te sientes hoy:</Text>
      <TextInput
        style={{ height: 40, borderColor: 'gray', borderWidth: 1, marginBottom: 20 }}
        onChangeText={setMessage}
        value={message}
      />
      <Button title="Enviar" onPress={handleSubmit} />
      {response && <Text>Respuesta del servidor: {response}</Text>}
    </View>
  );
};

export default Chat;
