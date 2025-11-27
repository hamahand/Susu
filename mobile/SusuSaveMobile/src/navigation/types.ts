// Navigation type definitions

export type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  OtpVerify: { phoneNumber: string };
};

export type MainTabParamList = {
  Home: undefined;
  Profile: undefined;
};

export type HomeStackParamList = {
  MyGroups: undefined;
  CreateGroup: undefined;
  JoinGroup: undefined;
  GroupDashboard: { groupId: number };
  GroupSettings: { groupId: number };
  Notifications: undefined;
  Transactions: undefined;
};

export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

