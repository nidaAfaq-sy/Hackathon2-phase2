# UI Components Specification

## 🎨 Component Architecture

### Core Components
```
components/
├── TaskList.tsx          → Main task list display
├── TaskForm.tsx          → Create/edit task form
├── TaskItem.tsx          → Individual task card
├── AuthForm.tsx          → Login/registration form
├── Layout.tsx           → Main application layout
├── Navigation.tsx       → App navigation
└── ErrorBoundary.tsx    → Error handling wrapper
```

## 📱 TaskList Component

### Props Interface
```typescript
interface TaskListProps {
  tasks: Task[];
  onTaskUpdate: (task: Task) => void;
  onTaskDelete: (taskId: string) => void;
  loading?: boolean;
  error?: string | null;
}
```

### Features
- **Task Display**: Grid/list view of tasks
- **Status Filtering**: Show all, pending, or completed
- **Search**: Filter tasks by title/description
- **Sorting**: By creation date, title, or status
- **Empty State**: Message when no tasks exist

### UI Elements
```tsx
<div className="task-list">
  {/* Header with controls */}
  <div className="task-list-header">
    <TaskFilter onFilterChange={...} />
    <TaskSearch onSearch={...} />
  </div>

  {/* Task items */}
  <div className="task-items">
    {tasks.map(task => (
      <TaskItem
        key={task.id}
        task={task}
        onUpdate={onTaskUpdate}
        onDelete={onTaskDelete}
      />
    ))}
  </div>

  {/* Empty state */}
  {tasks.length === 0 && !loading && (
    <EmptyState onAddTask={...} />
  )}

  {/* Loading state */}
  {loading && <LoadingSpinner />}
</div>
```

## 📝 TaskForm Component

### Props Interface
```typescript
interface TaskFormProps {
  task?: Task | null;
  onSubmit: (taskData: TaskFormData) => void;
  onCancel: () => void;
  loading?: boolean;
}
```

### Features
- **Form Fields**: Title, description, completed checkbox
- **Validation**: Real-time validation feedback
- **Submit States**: Loading, success, error
- **Mode Toggle**: Create vs edit mode

### UI Elements
```tsx
<form onSubmit={handleSubmit} className="task-form">
  <div className="form-group">
    <label htmlFor="title">Title</label>
    <input
      id="title"
      type="text"
      value={formData.title}
      onChange={(e) => setFormData({...formData, title: e.target.value})}
      className={errors.title ? 'error' : ''}
      required
    />
    {errors.title && <span className="error-message">{errors.title}</span>}
  </div>

  <div className="form-group">
    <label htmlFor="description">Description</label>
    <textarea
      id="description"
      value={formData.description || ''}
      onChange={(e) => setFormData({...formData, description: e.target.value})}
      rows={4}
    />
  </div>

  <div className="form-group">
    <label className="checkbox-label">
      <input
        type="checkbox"
        checked={formData.completed}
        onChange={(e) => setFormData({...formData, completed: e.target.checked})}
      />
      Mark as completed
    </label>
  </div>

  <div className="form-actions">
    <button type="button" onClick={onCancel} disabled={loading}>
      Cancel
    </button>
    <button type="submit" disabled={loading || !isValid}>
      {loading ? 'Saving...' : task ? 'Update Task' : 'Create Task'}
    </button>
  </div>
</form>
```

## 🎯 TaskItem Component

### Props Interface
```typescript
interface TaskItemProps {
  task: Task;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: string) => void;
}
```

### Features
- **Task Display**: Title, description, status
- **Actions**: Edit, delete, toggle complete
- **Status Indicators**: Visual completion status
- **Hover Effects**: Interactive feedback

### UI Elements
```tsx
<div className={`task-item ${task.completed ? 'completed' : ''}`}>
  <div className="task-content">
    <h3 className="task-title">{task.title}</h3>
    {task.description && (
      <p className="task-description">{task.description}</p>
    )}
    <div className="task-meta">
      <span className="task-date">
        Created: {formatDate(task.created_at)}
      </span>
      {task.updated_at !== task.created_at && (
        <span className="task-date">
          Updated: {formatDate(task.updated_at)}
        </span>
      )}
    </div>
  </div>

  <div className="task-actions">
    <button
      className="task-toggle"
      onClick={() => onUpdate({...task, completed: !task.completed})}
      aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
    >
      <TaskStatusIcon completed={task.completed} />
    </button>

    <button
      className="task-edit"
      onClick={() => onEdit(task)}
      aria-label="Edit task"
    >
      <EditIcon />
    </button>

    <button
      className="task-delete"
      onClick={() => onDelete(task.id)}
      aria-label="Delete task"
    >
      <DeleteIcon />
    </button>
  </div>
</div>
```

## 🔐 AuthForm Component

### Props Interface
```typescript
interface AuthFormProps {
  mode: 'login' | 'register';
  onSubmit: (credentials: AuthCredentials) => void;
  loading?: boolean;
  error?: string | null;
}
```

### Features
- **Mode Switching**: Login vs registration
- **Form Validation**: Email format, password strength
- **Error Handling**: Clear error messages
- **Remember Me**: Optional session persistence

### UI Elements
```tsx
<form onSubmit={handleSubmit} className="auth-form">
  <div className="form-header">
    <h2>{mode === 'login' ? 'Sign In' : 'Register'}</h2>
    <p>{mode === 'login' ? 'Welcome back!' : 'Create your account'}</p>
  </div>

  {error && <div className="error-message">{error}</div>}

  <div className="form-group">
    <label htmlFor="email">Email</label>
    <input
      id="email"
      type="email"
      value={formData.email}
      onChange={(e) => setFormData({...formData, email: e.target.value})}
      required
    />
  </div>

  <div className="form-group">
    <label htmlFor="password">Password</label>
    <input
      id="password"
      type="password"
      value={formData.password}
      onChange={(e) => setFormData({...formData, password: e.target.value})}
      minLength={8}
      required
    />
    {mode === 'register' && (
      <div className="password-hint">
        Password must be at least 8 characters
      </div>
    )}
  </div>

  {mode === 'login' && (
    <div className="form-group">
      <label className="checkbox-label">
        <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} />
        Remember me
      </label>
    </div>
  )}

  <button type="submit" className="auth-submit" disabled={loading}>
    {loading ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Register'}
  </button>

  <div className="auth-switch">
    {mode === 'login' ? (
      <span>
        Don't have an account?{' '}
        <button onClick={() => setMode('register')} className="link">
          Register here
        </button>
      </span>
    ) : (
      <span>
        Already have an account?{' '}
        <button onClick={() => setMode('login')} className="link">
          Sign in here
        </button>
      </span>
    )}
  </div>
</form>
```

## 🎨 Styling Guidelines

### Tailwind CSS Classes
- **Responsive**: Use responsive prefixes (sm:, md:, lg:)
- **Consistent Spacing**: Standardized padding/margin scales
- **Color Scheme**: Primary, secondary, and accent colors
- **Typography**: Consistent font sizes and weights
- **Accessibility**: Proper contrast ratios and ARIA labels

### Component States
- **Loading States**: Spinner animations
- **Error States**: Clear error messages and recovery
- **Success States**: Confirmation feedback
- **Disabled States**: Visual indication of disabled elements
- **Hover States**: Interactive feedback

### Accessibility Features
- **Keyboard Navigation**: Tab order and shortcuts
- **Screen Reader Support**: ARIA labels and roles
- **Focus Management**: Clear focus indicators
- **Color Independence**: Information not conveyed by color alone