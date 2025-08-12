import React, { createContext, useContext, ReactNode } from 'react';
import { useSessionStore } from './useSessionStore';

const SessionContext = createContext<ReturnType<typeof useSessionStore> | null>(null);

export const SessionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const sessionStore = useSessionStore();
  
  return (
    <SessionContext.Provider value={sessionStore}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export default SessionContext;