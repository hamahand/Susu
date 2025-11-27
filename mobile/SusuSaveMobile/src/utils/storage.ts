import AsyncStorage from '@react-native-async-storage/async-storage';
import { User } from '../types/api';

const KEYS = {
  TOKEN: '@sususave:token',
  USER: '@sususave:user',
};

// Token storage
export const saveToken = async (token: string): Promise<void> => {
  try {
    await AsyncStorage.setItem(KEYS.TOKEN, token);
  } catch (error) {
    console.error('Error saving token:', error);
  }
};

export const getToken = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem(KEYS.TOKEN);
  } catch (error) {
    console.error('Error getting token:', error);
    return null;
  }
};

export const removeToken = async (): Promise<void> => {
  try {
    await AsyncStorage.removeItem(KEYS.TOKEN);
  } catch (error) {
    console.error('Error removing token:', error);
  }
};

// User storage
export const saveUser = async (user: User): Promise<void> => {
  try {
    await AsyncStorage.setItem(KEYS.USER, JSON.stringify(user));
  } catch (error) {
    console.error('Error saving user:', error);
  }
};

export const getUser = async (): Promise<User | null> => {
  try {
    const userJson = await AsyncStorage.getItem(KEYS.USER);
    return userJson ? JSON.parse(userJson) : null;
  } catch (error) {
    console.error('Error getting user:', error);
    return null;
  }
};

export const removeUser = async (): Promise<void> => {
  try {
    await AsyncStorage.removeItem(KEYS.USER);
  } catch (error) {
    console.error('Error removing user:', error);
  }
};

// Clear all storage
export const clearStorage = async (): Promise<void> => {
  try {
    await AsyncStorage.multiRemove([KEYS.TOKEN, KEYS.USER]);
  } catch (error) {
    console.error('Error clearing storage:', error);
  }
};

