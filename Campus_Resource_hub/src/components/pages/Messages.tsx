/**
 * Messages Page
 * Displays message threads and allows users to send/receive messages
 */

import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, User, Clock } from 'lucide-react';
import { IUButton } from '../IUButton';
import { IUCard } from '../IUCard';
import { EmptyState } from '../EmptyState';
import * as messagesService from '../../api/services/messagesService';
import type { MessageThread, Message } from '../../api/types';
import { toast } from 'sonner';

export function Messages() {
  const [threads, setThreads] = useState<MessageThread[]>([]);
  const [selectedThread, setSelectedThread] = useState<MessageThread | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load threads on mount
  useEffect(() => {
    loadThreads();
  }, []);

  // Load messages when thread is selected
  useEffect(() => {
    if (selectedThread) {
      loadThreadMessages(selectedThread.thread_id);
    }
  }, [selectedThread]);

  const loadThreads = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await messagesService.getThreads({ page: 1, per_page: 50 });
      
      if (response.status === 200 && response.data) {
        setThreads(response.data.items || []);
      } else {
        throw new Error('Failed to load message threads');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load threads';
      setError(errorMessage);
      toast.error('Error loading messages', {
        description: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadThreadMessages = async (threadId: string) => {
    try {
      const response = await messagesService.getThreadMessages(threadId, { page: 1, per_page: 100 });
      
      if (response.status === 200 && response.data) {
        setMessages(response.data.items || []);
        // Mark thread as read
        await messagesService.markThreadAsRead(threadId);
      } else {
        throw new Error('Failed to load messages');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load messages';
      toast.error('Error loading messages', {
        description: errorMessage,
      });
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedThread) return;

    try {
      setSendingMessage(true);
      
      const response = await messagesService.sendMessage({
        receiverId: selectedThread.other_user.id,
        content: newMessage.trim(),
        threadId: selectedThread.thread_id,
        resourceId: selectedThread.resource?.id,
      } as any);

      if (response.status === 200 && response.data) {
        setMessages([...messages, response.data]);
        setNewMessage('');
        toast.success('Message sent successfully');
      } else {
        throw new Error('Failed to send message');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      toast.error('Error sending message', {
        description: errorMessage,
      });
    } finally {
      setSendingMessage(false);
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <MessageSquare className="w-12 h-12 text-iu-secondary mx-auto mb-4 animate-pulse" />
          <p className="text-iu-secondary">Loading messages...</p>
        </div>
      </div>
    );
  }

  if (error && threads.length === 0) {
    return (
      <EmptyState
        icon={MessageSquare}
        title="Error Loading Messages"
        description={error}
        actionLabel="Try Again"
        onAction={loadThreads}
      />
    );
  }

  return (
    <div className="h-[calc(100vh-120px)] flex gap-6">
      {/* Thread List */}
      <div className="w-80 flex-shrink-0">
        <div className="bg-iu-surface rounded-[var(--radius-lg)] shadow-iu-sm border border-iu h-full flex flex-col">
          <div className="p-4 border-b border-iu-border">
            <h2 className="admin-subtitle text-iu-primary">Messages</h2>
            <p className="admin-caption text-iu-secondary mt-1">
              {threads.length} conversation{threads.length !== 1 ? 's' : ''}
            </p>
          </div>

          <div className="flex-1 overflow-y-auto">
            {threads.length === 0 ? (
              <div className="p-8 text-center">
                <MessageSquare className="w-12 h-12 text-iu-secondary mx-auto mb-3" />
                <p className="admin-body-medium text-iu-secondary">No messages yet</p>
                <p className="admin-small text-iu-secondary mt-1">
                  Start a conversation from a resource page
                </p>
              </div>
            ) : (
              <div className="divide-y divide-iu-border">
                {threads.map((thread) => (
                  <button
                    key={thread.thread_id}
                    type="button"
                    onClick={() => setSelectedThread(thread)}
                    className={`w-full p-4 text-left transition-colors hover:bg-iu-light ${
                      selectedThread?.thread_id === thread.thread_id
                        ? 'bg-iu-light border-l-4 border-iu-primary'
                        : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-full bg-iu-primary/10 flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-iu-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <p className="admin-body-medium font-semibold text-iu-primary truncate">
                            {thread.other_user.full_name || thread.other_user.username}
                          </p>
                          {thread.unread_count > 0 && (
                            <span className="px-2 py-0.5 bg-iu-danger text-white admin-small rounded-full">
                              {thread.unread_count}
                            </span>
                          )}
                        </div>
                        {thread.resource && (
                          <p className="admin-small text-iu-secondary mb-1">
                            Re: {thread.resource.name}
                          </p>
                        )}
                        <p className="admin-small text-iu-secondary truncate">
                          {thread.last_message_preview}
                        </p>
                        <p className="admin-caption text-iu-secondary mt-1 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatTime(thread.last_message_at)}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Message View */}
      <div className="flex-1">
        {selectedThread ? (
          <div className="bg-iu-surface rounded-[var(--radius-lg)] shadow-iu-sm border border-iu h-full flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-iu-border">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-iu-primary/10 flex items-center justify-center">
                  <User className="w-5 h-5 text-iu-primary" />
                </div>
                <div>
                  <h3 className="admin-subtitle text-iu-primary">
                    {selectedThread.other_user.full_name || selectedThread.other_user.username}
                  </h3>
                  {selectedThread.resource && (
                    <p className="admin-small text-iu-secondary">
                      About: {selectedThread.resource.name}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.sender_id === selectedThread.other_user.id ? 'justify-start' : 'justify-end'
                  }`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      message.sender_id === selectedThread.other_user.id
                        ? 'bg-gray-100 text-gray-900'
                        : 'bg-iu-primary text-white'
                    }`}
                  >
                    <p className="admin-body-medium whitespace-pre-wrap">{message.content}</p>
                    <p
                      className={`admin-caption mt-1 ${
                        message.sender_id === selectedThread.other_user.id
                          ? 'text-gray-500'
                          : 'text-white/70'
                      }`}
                    >
                      {formatTime(message.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-iu-border">
              <div className="flex gap-2">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder="Type your message..."
                  className="flex-1 px-3 py-2 border border-iu-border rounded-lg admin-body-medium resize-none focus:outline-none focus:ring-2 focus:ring-iu-primary"
                  rows={3}
                  disabled={sendingMessage}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim() || sendingMessage}
                  className= "self-end inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-[var(--radius-md)] min-h-[44px] bg-iu-crimson text-white hover:bg-[var(--iu-crimson-700)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  <Send className="w-4 h-4" />
                  Send
                </button>
              </div>
              <p className="admin-caption text-iu-secondary mt-2">
                Press Enter to send, Shift+Enter for new line
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-iu-surface rounded-[var(--radius-lg)] shadow-iu-sm border border-iu h-full flex items-center justify-center">
            <div className="text-center p-8">
              <MessageSquare className="w-16 h-16 text-iu-secondary mx-auto mb-4" />
              <h3 className="admin-subtitle text-iu-primary mb-2">Select a Conversation</h3>
              <p className="admin-body-medium text-iu-secondary">
                Choose a message thread from the list to view and reply
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
