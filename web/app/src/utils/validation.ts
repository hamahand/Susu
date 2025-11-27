export const validatePhoneNumber = (phone: string): boolean => {
  // E.164 format: +[country code][number]
  const e164Regex = /^\+[1-9]\d{6,14}$/;
  return e164Regex.test(phone);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): boolean => {
  // At least 6 characters
  return password.length >= 6;
};

export const formatPhoneNumber = (phone: string): string => {
  // If it doesn't start with +, add +233 (Ghana)
  if (!phone.startsWith('+')) {
    // Remove leading 0 if present
    const cleaned = phone.startsWith('0') ? phone.substring(1) : phone;
    return `+233${cleaned}`;
  }
  return phone;
};

export const formatCurrency = (amount: number, currency: string = 'GHS'): string => {
  return `${currency} ${amount.toFixed(2)}`;
};

