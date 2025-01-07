# Vector DB Chat Interface

A Next.js application with a Python FastAPI backend that provides a beautiful chat interface for interacting with a vector database.

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Google PaLM API key

## Setup

1. Clone the repository
2. Create a `.env` file in the `api` directory with your Google PaLM API key:

   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. Install frontend dependencies:

   ```bash
   cd chat-interface
   npm install
   ```

4. Install backend dependencies:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Python backend:

   ```bash
   cd api
   uvicorn main:app --reload
   ```

2. In a new terminal, start the Next.js frontend:

   ```bash
   cd chat-interface
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Features

- Modern and responsive chat interface
- Real-time communication with vector database
- Beautiful UI with Tailwind CSS
- TypeScript support
- FastAPI backend for efficient processing

## Project Structure

```
chat-interface/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   ├── components/        # React components
│   └── page.tsx           # Main page
├── api/                   # Python backend
│   ├── main.py           # FastAPI application
│   └── requirements.txt   # Python dependencies
└── public/               # Static files
```
