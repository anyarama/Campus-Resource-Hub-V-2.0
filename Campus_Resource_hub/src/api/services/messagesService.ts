/**
 * Messages Service
 * Handles messaging operations
 */

import { apiClient, ApiResponse } from '../client';
import type { Message, MessageThread, PaginationParams, PaginatedResponse, MessageFormData } from '../types';

/**
 * Get user's message threads
 */
export async function getThreads(
  params?: PaginationParams
): Promise<ApiResponse<PaginatedResponse<MessageThread>>> {
  return apiClient.get<PaginatedResponse<MessageThread>>('/messages', params);
}

/**
 * Get messages in a thread
 */
export async function getThreadMessages(
  threadId: string,
  params?: PaginationParams
): Promise<ApiResponse<PaginatedResponse<Message>>> {
  return apiClient.get<PaginatedResponse<Message>>(`/messages/thread/${threadId}`, params);
}

/**
 * Send a new message
 */
export async function sendMessage(data: MessageFormData): Promise<ApiResponse<Message>> {
  return apiClient.post<Message>('/messages', data);
}

/**
 * Mark message as read
 */
export async function markMessageAsRead(id: number): Promise<ApiResponse> {
  return apiClient.put(`/messages/${id}/read`);
}

/**
 * Mark all messages in thread as read
 * Note: Backend doesn't have direct thread mark-as-read endpoint
 * This is handled automatically when viewing a thread
 */
export async function markThreadAsRead(threadId: string): Promise<ApiResponse> {
  // Backend marks thread as read automatically when GET /messages/thread/:id is called
  // This function is kept for API compatibility but returns a success response
  return Promise.resolve({ 
    data: { message: 'Thread marked as read automatically when viewing' },
    success: true,
    status: 200
  });
}

/**
 * Get unread message count
 */
export async function getUnreadCount(): Promise<ApiResponse<{ count: number }>> {
  return apiClient.get<{ count: number }>('/messages/unread-count');
}
