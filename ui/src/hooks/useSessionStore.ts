import { useState, useEffect, useCallback } from 'react';
import { getUniqId } from '@/utils';

export interface SessionItem {
  id: string;
  title: string;
  createTime: string;
  lastMessage?: string;
  lastActiveTime: string;
}

interface SessionStore {
  sessions: SessionItem[];
  currentSessionId: string | null;
}

const STORAGE_KEY = 'genie_sessions';

// 从localStorage获取会话数据
const getSessionStore = (): SessionStore => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Failed to parse session store:', error);
  }
  return { sessions: [], currentSessionId: null };
};

// 保存会话数据到localStorage
const saveSessionStore = (store: SessionStore): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch (error) {
    console.error('Failed to save session store:', error);
  }
};

// 生成新的会话ID
export const createNewSessionId = (): string => {
  return `session-${getUniqId()}`;
};

export const useSessionStore = () => {
  const [store, setStore] = useState<SessionStore>(getSessionStore);

  // 保存到localStorage
  useEffect(() => {
    saveSessionStore(store);
  }, [store]);

  // 创建新会话
  const createSession = useCallback((title: string = '新对话'): string => {
    const newSession: SessionItem = {
      id: createNewSessionId(),
      title,
      createTime: new Date().toISOString(),
      lastActiveTime: new Date().toISOString(),
    };

    setStore(prev => ({
      sessions: [newSession, ...prev.sessions],
      currentSessionId: newSession.id,
    }));

    return newSession.id;
  }, []);

  // 更新会话信息
  const updateSession = useCallback((sessionId: string, updates: Partial<Omit<SessionItem, 'id' | 'createTime'>>) => {
    setStore(prev => ({
      ...prev,
      sessions: prev.sessions.map(session => 
        session.id === sessionId 
          ? { 
              ...session, 
              ...updates, 
              lastActiveTime: new Date().toISOString()
            }
          : session
      ),
    }));
  }, []);

  // 删除会话
  const deleteSession = useCallback((sessionId: string) => {
    setStore(prev => {
      const newSessions = prev.sessions.filter(s => s.id !== sessionId);
      const newCurrentId = prev.currentSessionId === sessionId 
        ? (newSessions.length > 0 ? newSessions[0].id : null)
        : prev.currentSessionId;
      
      return {
        sessions: newSessions,
        currentSessionId: newCurrentId,
      };
    });
  }, []);

  // 设置当前活跃会话
  const setCurrentSession = useCallback((sessionId: string | null) => {
    setStore(prev => ({
      ...prev,
      currentSessionId: sessionId,
    }));
  }, []);

  // 获取会话详情
  const getSession = useCallback((sessionId: string): SessionItem | undefined => {
    return store.sessions.find(s => s.id === sessionId);
  }, [store.sessions]);

  // 检查会话是否存在
  const hasSession = useCallback((sessionId: string): boolean => {
    return store.sessions.some(s => s.id === sessionId);
  }, [store.sessions]);

  // 清空所有会话
  const clearAllSessions = useCallback(() => {
    setStore({ sessions: [], currentSessionId: null });
  }, []);

  return {
    sessions: store.sessions,
    currentSessionId: store.currentSessionId,
    createSession,
    updateSession,
    deleteSession,
    setCurrentSession,
    getSession,
    hasSession,
    clearAllSessions,
  };
};

export default useSessionStore;