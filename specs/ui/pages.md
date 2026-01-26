# UI Pages Specification

## 📱 Page Structure

### Main Pages
```
app/
├── layout.tsx           → Root layout with auth provider
├── page.tsx            → Dashboard/Home page
├── tasks/
│   ├── page.tsx        → Task list page
│   ├── [id]/
│   │   └── page.tsx    → Task detail/edit page
│   └── new/
│       └── page.tsx    → Create new task page
├── auth/
│   ├── signin/
│   │   └── page.tsx    → Login page
│   └── signup/
│       └── page.tsx    → Registration page
└── api/                → API routes (handled by Better Auth + custom)
```

## 🏠 Dashboard Page

### URL: `/`
### Purpose: Main application landing page

#### Features
- **User Greeting**: Personalized welcome message
- **Task Overview**: Summary of task counts (total, completed, pending)
- **Quick Actions**: Add task button, view all tasks
- **Recent Activity**: Last few created/completed tasks
- **Navigation**: Links to task management and settings

#### Component Structure
```tsx
export default function Dashboard() {
  const { session } = useSession();
  const { tasks, loading } = useTasks();

  return (
    <Layout>
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Welcome back, {session?.user.email}!</h1>
          <p>Your task management dashboard</p>
        </div>

        <div className="dashboard-stats">
          <StatCard
            title="Total Tasks"
            value={tasks.length}
            icon={<TaskIcon />}
          />
          <StatCard
            title="Completed"
            value={tasks.filter(t => t.completed).length}
            icon={<CheckIcon />}
          />
          <StatCard
            title="Pending"
            value={tasks.filter(t => !t.completed).length}
            icon={<ClockIcon />}
          />
        </div>

        <div className="dashboard-actions">
          <Link href="/tasks/new" className="btn-primary">
            Create New Task
          </Link>
          <Link href="/tasks" className="btn-secondary">
            View All Tasks
          </Link>
        </div>

        {tasks.length > 0 && (
          <div className="dashboard-recent">
            <h2>Recent Activity</h2>
            <TaskList
              tasks={tasks.slice(0, 5)}
              compact={true}
            />
          </div>
        )}
      </div>
    </Layout>
  );
}
```

## 📋 Task List Page

### URL: `/tasks`
### Purpose: Main task management interface

#### Features
- **Task Filtering**: By status (all, active, completed)
- **Task Search**: Real-time search by title/description
- **Task Actions**: Create, edit, delete, toggle complete
- **Bulk Operations**: Mark all complete, delete all
- **Pagination**: For large task lists (future enhancement)
- **Empty State**: Encouraging message when no tasks

#### Component Structure
```tsx
export default function TasksPage() {
  const { session } = useSession();
  const { tasks, loading, error, refreshTasks } = useTasks();

  return (
    <Layout>
      <div className="tasks-page">
        <div className="tasks-header">
          <h1>My Tasks</h1>
          <div className="tasks-controls">
            <TaskFilter
              currentFilter={filter}
              onFilterChange={setFilter}
            />
            <TaskSearch
              value={searchQuery}
              onChange={setSearchQuery}
            />
          </div>
        </div>

        {error && (
          <Alert variant="error" onRetry={refreshTasks}>
            {error}
          </Alert>
        )}

        <div className="tasks-content">
          {loading ? (
            <LoadingSpinner />
          ) : tasks.length === 0 ? (
            <EmptyState
              title="No tasks yet"
              description="Create your first task to get started"
              actionText="Create Task"
              onAction={() => router.push('/tasks/new')}
            />
          ) : (
            <TaskList
              tasks={filteredTasks}
              onTaskUpdate={handleTaskUpdate}
              onTaskDelete={handleTaskDelete}
            />
          )}
        </div>

        <div className="tasks-footer">
          <button
            onClick={handleCreateTask}
            className="btn-primary"
          >
            Add Task
          </button>
          {filteredTasks.length > 0 && (
            <div className="bulk-actions">
              <button onClick={handleMarkAllComplete}>
                Mark All Complete
              </button>
              <button onClick={handleDeleteAll}>
                Delete All
              </button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
```

## ✏️ Task Form Page

### URL: `/tasks/new` (Create) | `/tasks/[id]` (Edit)
### Purpose: Create and edit task details

#### Features
- **Form Validation**: Real-time field validation
- **Auto-save**: Optional draft saving
- **Cancel/Save**: Clear action buttons
- **Error Handling**: Field-level error messages
- **Success Feedback**: Confirmation after save

#### Component Structure
```tsx
export default function TaskFormPage({ params }: { params: { id?: string } }) {
  const router = useRouter();
  const taskId = params.id;
  const isEditing = !!taskId;

  const { task, loading: taskLoading } = useTask(taskId);
  const { createTask, updateTask, loading: saveLoading } = useTasks();

  const handleSubmit = async (formData: TaskFormData) => {
    if (isEditing) {
      await updateTask(taskId!, formData);
    } else {
      await createTask(formData);
    }
    router.push('/tasks');
  };

  if (taskLoading && isEditing) {
    return (
      <Layout>
        <LoadingSpinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="task-form-page">
        <div className="form-header">
          <h1>{isEditing ? 'Edit Task' : 'Create New Task'}</h1>
          <Link href="/tasks" className="back-link">
            ← Back to Tasks
          </Link>
        </div>

        <TaskForm
          task={task}
          onSubmit={handleSubmit}
          onCancel={() => router.push('/tasks')}
          loading={saveLoading}
        />
      </div>
    </Layout>
  );
}
```

## 🔐 Authentication Pages

### Signin Page: `/auth/signin`
### Purpose: User login interface

#### Features
- **Form Validation**: Email/password validation
- **Error Handling**: Clear error messages
- **Redirect**: After successful login
- **Forgot Password**: Link to password reset (future)
- **Social Login**: OAuth options (future)

#### Component Structure
```tsx
export default function SignInPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await signIn('credentials', {
        email: formData.email,
        password: formData.password,
        redirect: false,
      });

      if (result?.error) {
        setError('Invalid email or password');
      } else {
        router.push('/');
      }
    } catch (err) {
      setError('An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <AuthForm
        mode="login"
        onSubmit={handleSubmit}
        loading={loading}
        error={error}
      />
    </AuthLayout>
  );
}
```

### Signup Page: `/auth/signup`
### Purpose: User registration interface

#### Features
- **Password Confirmation**: Verify password matches
- **Terms Agreement**: Accept terms and conditions
- **Email Verification**: Confirmation email (future)
- **Redirect**: After successful registration

#### Component Structure
```tsx
export default function SignUpPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!formData.agreeToTerms) {
      setError('You must agree to the terms and conditions');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await signUp({
        email: formData.email,
        password: formData.password,
      });

      if (result?.error) {
        setError('Registration failed. Please try again.');
      } else {
        router.push('/auth/signin');
      }
    } catch (err) {
      setError('An error occurred during registration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <AuthForm
        mode="register"
        onSubmit={handleSubmit}
        loading={loading}
        error={error}
      />
    </AuthLayout>
  );
}
```

## 🎨 Layout Components

### Root Layout
```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <BetterAuthProvider>
          <Layout>
            {children}
          </Layout>
        </BetterAuthProvider>
      </body>
    </html>
  );
}
```

### Main Layout
```tsx
export default function Layout({ children }: { children: React.ReactNode }) {
  const { session, signOut } = useSession();

  return (
    <div className="app-layout">
      <Navigation
        user={session?.user}
        onSignOut={signOut}
      />
      <main className="main-content">
        {children}
      </main>
      <Footer />
    </div>
  );
}
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: `< 640px` - Single column layout
- **Tablet**: `640px - 1024px` - Two column where appropriate
- **Desktop**: `> 1024px` - Full multi-column layout

### Mobile Optimizations
- **Touch Targets**: Minimum 44px tap targets
- **Simplified Navigation**: Hamburger menu
- **Optimized Forms**: Larger input fields
- **Touch Gestures**: Swipe actions for tasks