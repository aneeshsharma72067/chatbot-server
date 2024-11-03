# Project: AI Powered Chat Assistant Backend

The backend server for the Gemini AI Chatbot is built with Flask to handle API requests, facilitate user interactions, and manage persistent chat sessions with PostgreSQL as the primary database. This backend enables AI-powered responses via the Gemini API, processing user inputs and dynamically generating context-aware responses.

## Key Features

- **API-Driven Architecture**: Flask REST API manages user queries, processes interactions, and communicates with the Gemini API for AI-generated responses.

- **Gemini API Integration**: Each message request is sent to the Gemini API, which returns natural language responses tailored to user inputs. The server efficiently handles and parses responses for frontend display.

- **Session and Chat Management**: PostgreSQL is used to persist chat sessions and store message histories, allowing users to continue conversations across multiple sessions. Each chat is associated with a unique session ID, enabling multi-threaded, context-aware conversations.

- **User System**: Supports basic user registration and login, enabling personalized chat history and secure access to past sessions.

- **Data Model Design**: SQLAlchemy is utilized for ORM-based models to define user accounts, chat sessions, and message histories, providing robust and scalable data structures for chat persistence.

- **Authentication and Security**: The server uses token-based authentication to ensure secure access to user-specific data. Security features are kept lightweight to optimize for small user groups and reduced latency.

## Technologies Used

- **Python / Flask**: Server framework for handling HTTP requests and API endpoints.
- **PostgreSQL**: Database for chat session storage and user data management.
- **SQLAlchemy**: ORM for database modeling and querying.
- **Gemini API**: Third-party API for AI-powered response generation.
