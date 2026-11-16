import React from 'react';
import {StyleSheet, Text, View} from 'react-native';

type Props = {
  label: string;
  tone: 'good' | 'warn' | 'bad' | 'neutral';
};

const colors = {
  good: {bg: '#DDF7E7', fg: '#0F6B3D'},
  warn: {bg: '#FFF2C2', fg: '#745400'},
  bad: {bg: '#FFE1DF', fg: '#9E241C'},
  neutral: {bg: '#E9EEF5', fg: '#344054'},
};

export function StatusPill({label, tone}: Props) {
  const palette = colors[tone];
  return (
    <View style={[styles.pill, {backgroundColor: palette.bg}]}>
      <Text style={[styles.text, {color: palette.fg}]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    alignSelf: 'flex-start',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  text: {
    fontSize: 12,
    fontWeight: '700',
  },
});
