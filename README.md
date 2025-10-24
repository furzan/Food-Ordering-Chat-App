# 🍕 AI-Powered Food Ordering Chat Application

A modern, intelligent food ordering system built with FastAPI, Chainlit, and AI agents. This application provides a conversational interface for users to browse menus, manage their cart, and place orders through natural language interactions.

## ✨ Features

### 🤖 AI-Powered Chat Interface
- **Natural Language Processing**: Chat with an AI assistant that understands food ordering requests
- **Streaming Responses**: Real-time AI responses for smooth user experience
- **Context Awareness**: The AI remembers your conversation and preferences
- **Smart Recommendations**: Intelligent suggestions based on your order history

### 🛒 Shopping Cart Management
- **Add Items**: Add menu items to your cart with quantities
- **Update Quantities**: Modify item quantities or remove items
- **Cart Persistence**: Your cart is saved across sessions
- **Real-time Calculations**: Instant price updates and totals

### 📋 Order Management
- **Menu Browsing**: View available items with prices and descriptions
- **Order Placement**: Convert cart items to confirmed orders
- **Order History**: Track your previous orders and their status
- **Order Status Tracking**: Monitor order progress

### 🔐 User Authentication
- **Secure Login**: JWT-based authentication system
- **User Registration**: Create new accounts with password protection
- **Session Management**: Persistent user sessions
- **Password Security**: Bcrypt password hashing

### 🗄️ Data Management
- **PostgreSQL Database**: Robust data storage with SQLModel ORM
- **Async Operations**: High-performance async database operations
- **Data Relationships**: Proper foreign key relationships between entities
- **Conversation History**: Persistent chat history per user

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── agents/           # AI Agent Configuration
│   │   ├── main.py       # Agent setup and streaming
│   │   ├── MCP/          # Model Context Protocol server
│   │   └── my_config/    # AI model configuration
│   ├── api/              # REST API Routes
│   │   ├── user_routes.py    # User authentication endpoints
│   │   └── order_routes.py   # Order and menu endpoints
│   ├── db/               # Database Layer
│   │   ├── models/       # SQLModel database models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── main.py       # Database configuration
│   └── services/         # Business Logic
│       ├── agent_service.py  # AI agent operations
│       ├── order_service.py  # Order management
│       └── user_service.py   # User management
└── config.py             # Application configuration
```

### Frontend (Chainlit)
```
frontend/
└── main_page.py          # Chainlit chat interface
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- UV package manager 

1. **Install dependencies**
   ```bash
   uv sync
   
2. **Start the Backend**
   ```bash
   uv run uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
   ```
3. **Start the Frontend**
   ```bash
   chainlit run main_page.py --port 8001
   ```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/user/register` - Register a new user
- `POST /api/v1/user/login` - User login
- `GET /api/v1/user/chat` - Get chat history

### Menu & Order Endpoints
- `GET /api/v1/order/menu` - Get all menu items
- `POST /api/v1/order/menu` - Add new menu item (admin)
- `GET /api/v1/order/orders` - Get user's recent order
- `POST /api/v1/order/orders` - Create new order
- `POST /api/v1/order/orders_cart` - Create order from cart

### Cart Management
- `GET /api/v1/order/cartitems` - Get cart items
- `POST /api/v1/order/cartitems` - Add items to cart
- `PUT /api/v1/order/cartitems` - Update cart items
- `DELETE /api/v1/order/cartitem` - Remove specific cart item
- `DELETE /api/v1/order/cartitems` - Clear entire cart

### AI Chat
- `POST /api/v1/user/message` - Send message to AI assistant (streaming)

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL database ORM with Pydantic integration
- **PostgreSQL**: Robust relational database
- **AsyncPG**: High-performance async PostgreSQL driver
- **JWT**: JSON Web Token authentication
- **Bcrypt**: Secure password hashing

### AI & Agents
- **OpenAI Agents SDK**: Advanced AI agent framework
- **Google Gemini**: Large language model for natural language processing
- **MCP (Model Context Protocol)**: Tool integration for AI agents
- **Streaming**: Real-time AI response streaming

### Frontend
- **Chainlit**: Conversational AI interface framework
- **Real-time Chat**: WebSocket-based chat interface
- **Authentication**: Secure user login system

### Development Tools
- **UV**: Fast Python package manager
- **Pydantic**: Data validation and settings management
- **Python-Decouple**: Environment variable management
- **SQLAlchemy**: Advanced database toolkit

### Database Models
- **Users**: User accounts and authentication
- **Menu**: Restaurant menu items
- **Orders**: Customer orders
- **OrderItems**: Individual items in orders
- **CartItems**: Shopping cart items
- **ConversationMessage**: Chat history

```
**Built with ❤️ using FastAPI, Chainlit, and AI Agents**
