import React from 'react';
import { Card as PaperCard } from 'react-native-paper';
import { StyleSheet, TouchableOpacity } from 'react-native';
import { spacing, borderRadius } from '../theme';

interface CardProps {
  children: React.ReactNode;
  onPress?: () => void;
  style?: any;
  elevation?: number;
}

export const Card: React.FC<CardProps> = ({
  children,
  onPress,
  style,
  elevation = 2,
}) => {
  const content = (
    <PaperCard style={[styles.card, style]} elevation={elevation}>
      <PaperCard.Content>{children}</PaperCard.Content>
    </PaperCard>
  );

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
        {content}
      </TouchableOpacity>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  card: {
    borderRadius: borderRadius.md,
    marginBottom: spacing.md,
  },
});

