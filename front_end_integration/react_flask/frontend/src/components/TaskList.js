import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Badge, Button, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { getAllTasks } from '../services/tasks';

const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const tasksData = await getAllTasks();
        setTasks(tasksData);
        setError(null);
      } catch (err) {
        console.error('Error fetching tasks:', err);
        setError('Failed to load tasks. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'info';
      case 'pending':
        return 'warning';
      default:
        return 'secondary';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    }).format(date);
  };

  const handleTaskClick = (id) => {
    navigate(`/tasks/${id}`);
  };

  if (loading) {
    return <div className="text-center mt-5">Loading tasks...</div>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>My Tasks</h1>
        <Button
          as={Link}
          to="/tasks/new"
          variant="primary"
        >
          Add New Task
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {!loading && tasks.length === 0 ? (
        <Alert variant="info">
          You don't have any tasks yet. Click the "Add New Task" button to create one.
        </Alert>
      ) : (
        <Row>
          {tasks.map((task) => (
            <Col md={4} className="mb-4" key={task.id}>
              <Card 
                className="h-100 task-card" 
                onClick={() => handleTaskClick(task.id)}
              >
                <Card.Body>
                  <Card.Title>{task.title}</Card.Title>
                  <Badge 
                    bg={getStatusBadgeVariant(task.status)} 
                    className="mb-2 status-badge"
                  >
                    {task.status.replace('_', ' ')}
                  </Badge>
                  <Card.Text>{task.description}</Card.Text>
                </Card.Body>
                <Card.Footer className="text-muted">
                  Created: {formatDate(task.created_at)}
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default TaskList;
