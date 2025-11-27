import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';

import { useAuth } from '../store/authContext';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { colors } from '../theme';

// Auth Screens
import { WelcomeScreen } from '../screens/WelcomeScreen';
import { LoginScreen } from '../screens/LoginScreen';
import { RegisterScreen } from '../screens/RegisterScreen';
import { OtpVerifyScreen } from '../screens/OtpVerifyScreen';

// Main Screens
import { MyGroupsScreen } from '../screens/MyGroupsScreen';
import { CreateGroupScreen } from '../screens/CreateGroupScreen';
import { GroupDashboardScreen } from '../screens/GroupDashboardScreen';
import { GroupSettingsScreen } from '../screens/GroupSettingsScreen';
import { JoinGroupScreen } from '../screens/JoinGroupScreen';
import { NotificationsScreen } from '../screens/NotificationsScreen';
import { ProfileScreen } from '../screens/ProfileScreen';
import DebugScreen from '../screens/DebugScreen';

import { AuthStackParamList, MainTabParamList, HomeStackParamList } from './types';

const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();
const HomeStack = createNativeStackNavigator<HomeStackParamList>();

// Home Stack Navigator
const HomeStackNavigator = () => {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen
        name="MyGroups"
        component={MyGroupsScreen}
        options={{ headerShown: false }}
      />
      <HomeStack.Screen
        name="CreateGroup"
        component={CreateGroupScreen}
        options={{ headerShown: false }}
      />
      <HomeStack.Screen
        name="JoinGroup"
        component={JoinGroupScreen}
        options={{ headerShown: false }}
      />
      <HomeStack.Screen
        name="GroupDashboard"
        component={GroupDashboardScreen}
        options={{ headerShown: false }}
      />
      <HomeStack.Screen
        name="GroupSettings"
        component={GroupSettingsScreen}
        options={{ headerShown: false }}
      />
      <HomeStack.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{ headerShown: false }}
      />
    </HomeStack.Navigator>
  );
};

// Auth Stack Navigator
const AuthNavigator = () => {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Welcome" component={WelcomeScreen} />
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
      <AuthStack.Screen name="OtpVerify" component={OtpVerifyScreen} />
    </AuthStack.Navigator>
  );
};

// Main Tab Navigator
const MainNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string = 'home';

          if (route.name === 'Home') {
            iconName = 'view-dashboard';
          } else if (route.name === 'Profile') {
            iconName = 'account';
          }

          return <MaterialCommunityIcons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home" component={HomeStackNavigator} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
      <Tab.Screen 
        name="Debug" 
        component={DebugScreen}
        options={{
          tabBarIcon: ({ focused, color, size }) => (
            <MaterialCommunityIcons name="bug" size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

// Root App Navigator
export const AppNavigator = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
};

