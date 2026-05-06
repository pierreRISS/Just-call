import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { Todo } from '../api/todos';

type TodoItemProps = {
  todo: Todo;
  isDeleting: boolean;
  onDelete: (todoId: number) => void;
};

export function TodoItem({ todo, isDeleting, onDelete }: TodoItemProps) {
  return (
    <View style={styles.item}>
      <Text style={styles.title}>{todo.title}</Text>
      <Pressable
        accessibilityRole="button"
        disabled={isDeleting}
        onPress={() => onDelete(todo.id)}
        style={({ pressed }) => [
          styles.deleteButton,
          pressed && styles.pressed,
          isDeleting && styles.disabled,
        ]}
      >
        <Text style={styles.deleteButtonText}>
          {isDeleting ? '...' : 'Supprimer'}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  item: {
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderColor: '#e2e8f0',
    borderRadius: 8,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 12,
    justifyContent: 'space-between',
    minHeight: 58,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  title: {
    color: '#1f2937',
    flex: 1,
    fontSize: 16,
    lineHeight: 22,
  },
  deleteButton: {
    alignItems: 'center',
    backgroundColor: '#dc2626',
    borderRadius: 6,
    minHeight: 42,
    justifyContent: 'center',
    paddingHorizontal: 14,
  },
  deleteButtonText: {
    color: '#ffffff',
    fontWeight: '700',
  },
  disabled: {
    opacity: 0.6,
  },
  pressed: {
    opacity: 0.8,
  },
});

