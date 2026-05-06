import { useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  RefreshControl,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

import { TodoItem } from '../components/TodoItem';
import { apiUrl } from '../config';
import { useCreateTodo, useDeleteTodo, useTodos } from '../hooks/useTodos';

export function TodosScreen() {
  const [title, setTitle] = useState('');

  const todosQuery = useTodos();
  const createTodoMutation = useCreateTodo();
  const deleteTodoMutation = useDeleteTodo();

  const isCreating = createTodoMutation.isPending;
  const trimmedTitle = title.trim();

  function handleCreateTodo() {
    if (!trimmedTitle || isCreating) return;

    createTodoMutation.mutate(trimmedTitle, {
      onSuccess: () => {
        setTitle('');
      },
    });
  }

  const error =
    todosQuery.error?.message ||
    createTodoMutation.error?.message ||
    deleteTodoMutation.error?.message;

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.container}
      >
        <View style={styles.header}>
          <Text style={styles.eyebrow}>FastAPI + PostgreSQL</Text>
          <Text style={styles.heading}>Todo mobile</Text>
          <Text style={styles.apiUrl}>API: {apiUrl}</Text>
        </View>

        <View style={styles.form}>
          <Text style={styles.label}>Nouvelle todo</Text>
          <View style={styles.inputRow}>
            <TextInput
              autoCapitalize="sentences"
              editable={!isCreating}
              maxLength={255}
              onChangeText={setTitle}
              onSubmitEditing={handleCreateTodo}
              placeholder="Ajouter un élément"
              returnKeyType="done"
              style={styles.input}
              value={title}
            />
            <Pressable
              accessibilityRole="button"
              disabled={!trimmedTitle || isCreating}
              onPress={handleCreateTodo}
              style={({ pressed }) => [
                styles.addButton,
                pressed && styles.pressed,
                (!trimmedTitle || isCreating) && styles.disabled,
              ]}
            >
              <Text style={styles.addButtonText}>
                {isCreating ? '...' : 'Ajouter'}
              </Text>
            </Pressable>
          </View>
        </View>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        {todosQuery.isLoading ? (
          <View style={styles.loading}>
            <ActivityIndicator color="#2563eb" />
            <Text style={styles.muted}>Chargement...</Text>
          </View>
        ) : (
          <FlatList
            contentContainerStyle={styles.listContent}
            data={todosQuery.data ?? []}
            keyExtractor={(item) => String(item.id)}
            refreshControl={
              <RefreshControl
                onRefresh={todosQuery.refetch}
                refreshing={todosQuery.isRefetching}
                tintColor="#2563eb"
              />
            }
            renderItem={({ item }) => (
              <TodoItem
                isDeleting={
                  deleteTodoMutation.isPending &&
                  deleteTodoMutation.variables === item.id
                }
                onDelete={(todoId) => deleteTodoMutation.mutate(todoId)}
                todo={item}
              />
            )}
            ListEmptyComponent={
              <Text style={styles.empty}>Aucune todo pour le moment.</Text>
            }
          />
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: '#f5f7fb',
    flex: 1,
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 24,
  },
  header: {
    gap: 8,
    marginBottom: 28,
  },
  eyebrow: {
    color: '#64748b',
    fontSize: 13,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  heading: {
    color: '#0f172a',
    fontSize: 40,
    fontWeight: '800',
    lineHeight: 44,
  },
  apiUrl: {
    color: '#64748b',
    fontSize: 13,
  },
  form: {
    gap: 10,
    marginBottom: 18,
  },
  label: {
    color: '#1f2937',
    fontSize: 16,
    fontWeight: '700',
  },
  inputRow: {
    gap: 10,
  },
  input: {
    backgroundColor: '#ffffff',
    borderColor: '#cbd5e1',
    borderRadius: 6,
    borderWidth: 1,
    color: '#1f2937',
    fontSize: 16,
    minHeight: 48,
    paddingHorizontal: 14,
  },
  addButton: {
    alignItems: 'center',
    backgroundColor: '#2563eb',
    borderRadius: 6,
    minHeight: 48,
    justifyContent: 'center',
    paddingHorizontal: 18,
  },
  addButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  disabled: {
    opacity: 0.55,
  },
  pressed: {
    opacity: 0.84,
  },
  error: {
    color: '#b91c1c',
    fontWeight: '700',
    marginBottom: 14,
  },
  loading: {
    alignItems: 'center',
    gap: 10,
    paddingVertical: 32,
  },
  muted: {
    color: '#64748b',
  },
  listContent: {
    gap: 10,
    paddingBottom: 32,
  },
  empty: {
    color: '#64748b',
    marginTop: 8,
  },
});

