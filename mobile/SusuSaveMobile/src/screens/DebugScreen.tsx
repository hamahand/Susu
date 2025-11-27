import React, { useState, useEffect } from 'react';
import { View, Text, Button, Alert, StyleSheet } from 'react-native';
import { Platform } from 'react-native';
import axios from 'axios';
import { config } from '../config';
import apiClient from '../api/client';

const MobileAppDebugScreen: React.FC = () => {
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Gather debug information
    const info = {
      platform: Platform.OS,
      apiUrl: config.API_BASE_URL,
      isDev: __DEV__,
      timestamp: new Date().toISOString(),
    };
    setDebugInfo(info);
  }, []);

  const testBackendConnection = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/health');
      Alert.alert('Success', `Backend is reachable!\nStatus: ${response.data.status}\nAPI URL: ${apiClient.defaults.baseURL}`);
    } catch (error: any) {
      Alert.alert('Error', `Backend connection failed:\n${error.message}\n\nTrying alternative URLs...`);
      
      // Test alternative URLs
      const alternativeUrls = [
        'http://10.0.2.2:8000',
        'http://localhost:8000',
        'http://127.0.0.1:8000'
      ];
      
      for (const url of alternativeUrls) {
        try {
          const testClient = axios.create({ baseURL: url, timeout: 5000 });
          const testResponse = await testClient.get('/health');
          Alert.alert('Alternative URL Found', `Backend is reachable at:\n${url}\nStatus: ${testResponse.data.status}`);
          break;
        } catch (testError) {
          console.log(`Failed to connect to ${url}`);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    try {
      // Test with a known test user
      const response = await apiClient.post('/auth/login', {
        phone_number: '+233244123456',
        password: 'testpassword123'
      });
      Alert.alert('Login Test', 'Login endpoint is working!');
    } catch (error: any) {
      Alert.alert('Login Test', `Login test failed:\n${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Mobile App Debug</Text>
      
      <View style={styles.infoContainer}>
        <Text style={styles.infoTitle}>Debug Information:</Text>
        <Text style={styles.infoText}>Platform: {debugInfo.platform}</Text>
        <Text style={styles.infoText}>API URL: {debugInfo.apiUrl}</Text>
        <Text style={styles.infoText}>Development Mode: {debugInfo.isDev ? 'Yes' : 'No'}</Text>
        <Text style={styles.infoText}>Timestamp: {debugInfo.timestamp}</Text>
      </View>

      <View style={styles.buttonContainer}>
        <Button
          title="Test Backend Connection"
          onPress={testBackendConnection}
          disabled={loading}
        />
        
        <View style={styles.spacer} />
        
        <Button
          title="Test Login Endpoint"
          onPress={testLogin}
          disabled={loading}
        />
      </View>

      {loading && (
        <Text style={styles.loadingText}>Testing...</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  infoContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  infoText: {
    fontSize: 14,
    marginBottom: 5,
    color: '#666',
    fontFamily: 'monospace',
  },
  buttonContainer: {
    marginBottom: 20,
  },
  spacer: {
    height: 10,
  },
  loadingText: {
    textAlign: 'center',
    fontSize: 16,
    color: '#666',
    fontStyle: 'italic',
  },
});

export default MobileAppDebugScreen;
