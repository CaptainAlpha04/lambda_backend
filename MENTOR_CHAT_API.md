# Mentor Chat API Documentation

## Overview
The Mentor Chat API provides AI-powered conversational mentoring with persistent conversation history. It supports multiple chat sessions per user and maintains context across conversations.

## Database Schema

### `mentor_chats` Table
```sql
CREATE TABLE public.mentor_chats (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  user_id UUID NULL,
  title TEXT NULL,
  conversation JSON NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT mentor_chats_pkey PRIMARY KEY (id),
  CONSTRAINT mentor_chats_user_id_fkey FOREIGN KEY (user_id) 
    REFERENCES users (id) ON UPDATE CASCADE ON DELETE RESTRICT
);
```

### Conversation JSON Structure
Each chat's `conversation` field contains an array of message exchanges:
```json
[
  {
    "id": "exchange-uuid",
    "user_message": "Hello, I need help with calculus",
    "mentor_response": "Hi! I'd be happy to help you with calculus. What specific topic are you working on?",
    "timestamp": "2025-09-07T10:30:00.000Z"
  },
  {
    "id": "exchange-uuid-2", 
    "user_message": "I'm struggling with derivatives",
    "mentor_response": "Derivatives can be tricky at first! Let's start with the basic concept...",
    "timestamp": "2025-09-07T10:32:15.000Z"
  }
]
```

## API Endpoints

### Base URL
```
{API_BASE_URL}/api/mentor
```

---

## 1. Send Message to Mentor

**Endpoint:** `POST /mentor/chat`

**Description:** Send a message to the AI mentor. If no `chat_id` is provided, it will use the user's most recent chat or create a new one.

### Request Body
```json
{
  "userId": "string (UUID)",
  "message": "string",
  "chat_id": "string (UUID, optional)"
}
```

### Response
```json
{
  "response": "string"
}
```

### Example
```javascript
// Send message to mentor
const response = await fetch('/api/mentor/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    userId: "123e4567-e89b-12d3-a456-426614174000",
    message: "Can you help me understand linear algebra?",
    chat_id: "optional-chat-uuid" // Optional
  })
});

const data = await response.json();
console.log(data.response); // AI mentor's response
```

---

## 2. Create New Chat Session

**Endpoint:** `POST /mentor/new-chat`

**Description:** Create a new chat session for the user.

### Request Body
```json
{
  "userId": "string (UUID)",
  "title": "string (optional)"
}
```

### Response
```json
{
  "chat": {
    "id": "string (UUID)",
    "user_id": "string (UUID)",
    "title": "string",
    "conversation": [],
    "created_at": "string (ISO timestamp)"
  }
}
```

### Example
```javascript
// Create new chat session
const response = await fetch('/api/mentor/new-chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    userId: "123e4567-e89b-12d3-a456-426614174000",
    title: "Physics Study Session" // Optional
  })
});

const data = await response.json();
console.log(data.chat.id); // New chat ID
```

---

## 3. Get User's Chat Sessions

**Endpoint:** `GET /mentor/chats/{user_id}`

**Description:** Retrieve all chat sessions for a specific user.

### URL Parameters
- `user_id` (string, UUID): The user's unique identifier

### Query Parameters
- `limit` (integer, optional): Maximum number of chats to return (default: 10)

### Response
```json
{
  "chats": [
    {
      "id": "string (UUID)",
      "title": "string",
      "created_at": "string (ISO timestamp)"
    }
  ]
}
```

### Example
```javascript
// Get user's chat sessions
const userId = "123e4567-e89b-12d3-a456-426614174000";
const response = await fetch(`/api/mentor/chats/${userId}?limit=20`);
const data = await response.json();

data.chats.forEach(chat => {
  console.log(`Chat: ${chat.title} (${chat.id})`);
});
```

---

## 4. Get Conversation History

**Endpoint:** `GET /mentor/history/{user_id}`

**Description:** Retrieve conversation history for a user or specific chat.

### URL Parameters
- `user_id` (string, UUID): The user's unique identifier

### Query Parameters
- `chat_id` (string, UUID, optional): Specific chat ID to get history for

### Response
```json
{
  "history": [
    {
      "id": "string (UUID)",
      "user_message": "string",
      "mentor_response": "string", 
      "timestamp": "string (ISO timestamp)"
    }
  ]
}
```

### Example
```javascript
// Get conversation history for specific chat
const userId = "123e4567-e89b-12d3-a456-426614174000";
const chatId = "chat-uuid-here";
const response = await fetch(`/api/mentor/history/${userId}?chat_id=${chatId}`);
const data = await response.json();

data.history.forEach(exchange => {
  console.log(`User: ${exchange.user_message}`);
  console.log(`Mentor: ${exchange.mentor_response}`);
});

// Get history from most recent chat (no chat_id parameter)
const response2 = await fetch(`/api/mentor/history/${userId}`);
```

---

## 5. Rename Chat Session

**Endpoint:** `PUT /mentor/rename-chat`

**Description:** Update the title of an existing chat session.

### Request Body
```json
{
  "chat_id": "string (UUID)",
  "title": "string"
}
```

### Response
```json
{
  "message": "Chat title updated successfully",
  "chat_id": "string (UUID)",
  "new_title": "string"
}
```

### Example
```javascript
// Rename a chat session
const response = await fetch('/api/mentor/rename-chat', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    chat_id: "chat-uuid-here",
    title: "Advanced Calculus Discussion"
  })
});

const data = await response.json();
console.log(data.message); // "Chat title updated successfully"
```

---

## 6. Delete Chat Session

**Endpoint:** `DELETE /mentor/delete-chat`

**Description:** Delete an existing chat session. Only the owner of the chat can delete it.

### Request Body
```json
{
  "chat_id": "string (UUID)",
  "user_id": "string (UUID)"
}
```

### Response
```json
{
  "message": "Chat deleted successfully",
  "chat_id": "string (UUID)"
}
```

### Example
```javascript
// Delete a chat session
const response = await fetch('/api/mentor/delete-chat', {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    chat_id: "chat-uuid-here",
    user_id: "123e4567-e89b-12d3-a456-426614174000"
  })
});

const data = await response.json();
console.log(data.message); // "Chat deleted successfully"
```

---

## Frontend Integration Guide

### 1. Chat Interface Setup

```javascript
class MentorChat {
  constructor(userId) {
    this.userId = userId;
    this.currentChatId = null;
    this.baseUrl = '/api/mentor';
  }

  async sendMessage(message) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: this.userId,
        message: message,
        chat_id: this.currentChatId
      })
    });
    
    return await response.json();
  }

  async createNewChat(title = null) {
    const response = await fetch(`${this.baseUrl}/new-chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: this.userId,
        title: title
      })
    });
    
    const data = await response.json();
    this.currentChatId = data.chat.id;
    return data.chat;
  }

  async loadChatHistory(chatId = null) {
    const url = chatId 
      ? `${this.baseUrl}/history/${this.userId}?chat_id=${chatId}`
      : `${this.baseUrl}/history/${this.userId}`;
    
    const response = await fetch(url);
    return await response.json();
  }

  async getUserChats() {
    const response = await fetch(`${this.baseUrl}/chats/${this.userId}`);
    return await response.json();
  }

  async renameChat(chatId, newTitle) {
    const response = await fetch(`${this.baseUrl}/rename-chat`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        title: newTitle
      })
    });
    
    return await response.json();
  }

  async deleteChat(chatId) {
    const response = await fetch(`${this.baseUrl}/delete-chat`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        user_id: this.userId
      })
    });
    
    return await response.json();
  }
}
```

### 2. Usage Example

```javascript
// Initialize chat for user
const chat = new MentorChat("123e4567-e89b-12d3-a456-426614174000");

// Load existing chats
const userChats = await chat.getUserChats();
if (userChats.chats.length > 0) {
  // Use most recent chat
  chat.currentChatId = userChats.chats[0].id;
  const history = await chat.loadChatHistory(chat.currentChatId);
  // Display conversation history
} else {
  // Create new chat
  await chat.createNewChat("New Conversation");
}

// Send message
const response = await chat.sendMessage("Help me with calculus derivatives");
console.log(response.response); // Display mentor's response

// Rename a chat session
if (chat.currentChatId) {
  await chat.renameChat(chat.currentChatId, "Calculus Help Session");
  console.log("Chat renamed successfully");
}

// Delete a chat session
const userChatsUpdated = await chat.getUserChats();
if (userChatsUpdated.chats.length > 1) {
  const chatToDelete = userChatsUpdated.chats[1].id; // Delete second chat
  await chat.deleteChat(chatToDelete);
  console.log("Chat deleted successfully");
}
```

## Key Features

### 🧠 **Context Awareness**
- The AI maintains context from previous messages in the conversation
- Each new message includes the last 10 message exchanges for continuity
- Responses are more coherent and build upon previous discussion

### 💾 **Persistent Storage**
- All conversations are automatically saved to the database
- Users can access conversation history anytime
- Multiple chat sessions per user are supported

### 🔄 **Session Management**
- Users can have multiple ongoing chat sessions
- Each session maintains its own conversation thread
- Easy switching between different chat topics

### 📱 **Frontend Friendly**
- Simple REST API with JSON responses
- Clear error handling with HTTP status codes
- Consistent data structures across all endpoints

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error

Error responses include a `detail` field:
```json
{
  "detail": "Error message description"
}
```

## Notes for Frontend Team

1. **User Authentication**: Ensure you pass the authenticated user's UUID as `userId`
2. **Chat Sessions**: Consider implementing a chat selector UI for multiple sessions
3. **Real-time Updates**: The API is REST-based; consider polling or WebSockets for real-time chat
4. **Error Handling**: Always handle network errors and API errors gracefully
5. **Loading States**: Chat generation may take a few seconds; show loading indicators
6. **Message Formatting**: Mentor responses may contain markdown; consider parsing for rich display
