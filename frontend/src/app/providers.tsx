'use client';

import { authClient } from '../lib/auth';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <div>
      {children}
    </div>
  );
}