# React + Flask Integration

This example demonstrates how to integrate a React frontend with a Flask backend API.

## Project Structure

```
react_flask/
├── api/                  # Flask backend
│   ├── app.py            # Main Flask application
│   └── requirements.txt  # Backend dependencies
├── frontend/             # React frontend
│   ├── public/           # Public assets
│   ├── src/              # React source code
│   ├── package.json      # Frontend dependencies
│   └── README.md         # Frontend documentation
└── README.md             # Project documentation
```

## Key Concepts Demonstrated

1. **API Development with Flask**
   - RESTful API design
   - JSON serialization/deserialization
   - CORS handling for cross-origin requests
   - Resource-based routing

2. **Frontend Development with React**
   - Modern React with functional components and hooks
   - State management with useState and useEffect
   - Fetching data from API endpoints
   - Handling API responses and errors

3. **Integration Patterns**
   - Separate development servers during development
   - API proxying for seamless integration
   - Authentication flow between frontend and backend
   - Environment configuration for different deployment scenarios

## Getting Started

### Backend Setup

1. Navigate to the API directory:
   ```
   cd api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask development server:
   ```
   python app.py
   ```
   The API will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the dependencies:
   ```
   npm install
   ```

3. Run the React development server:
   ```
   npm start
   ```
   The frontend will be available at http://localhost:3000

## Production Deployment

For a production deployment, you have several options:

1. **Separate Deployment**
   - Deploy the Flask API to a server/cloud provider
   - Deploy the React app to a static hosting service
   - Configure the React app to communicate with the API

2. **Combined Deployment**
   - Build the React app (`npm run build`)
   - Configure Flask to serve the React build files as static content
   - Deploy the combined application to a server/cloud provider

## Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Guide to Flask-CORS](https://flask-cors.readthedocs.io/en/latest/)
- [Create React App Documentation](https://create-react-app.dev/docs/getting-started/)
