import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Badge, Button, Alert, Row, Col } from 'react-bootstrap';
import { getTask, deleteTask } from '../services/tasks';

const TaskDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        setLoading(true);
        const taskData = await getTask(id);
        setTask(taskData);
        setError(null);
      } catch (err) {
        console.error('Error fetching task:', err);
        setError('Failed to load task details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await deleteTask(id);
        navigate('/');
      } catch (err) {
        console.error('Error deleting task:', err);
        setError('Failed to delete task. Please try again later.');
      }
    }
  };

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
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  if (loading) {
    return <div className="text-center mt-5">Loading task details...</div>;
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  if (!task) {
    return <Alert variant="warning">Task not found.</Alert>;
  }

  return (
    <div className="task-detail-container">
      <Row>
        <Col md={8}>
          <h1>{task.title}</h1>
          <Badge 
            bg={getStatusBadgeVariant(task.status)} 
            className="mb-3 status-badge"
          >
            {task.status.replace('_', ' ')}
          </Badge>
          <div className="mb-4">
            <h5>Description</h5>
            <p>{task.description || 'No description provided.'}</p>
          </div>
          <div className="mb-4">
            <h5>Created At</h5>
            <p>{formatDate(task.created_at)}</p>
          </div>
        </Col>
        <Col md={4}>
          <Card>
            <Card.Body>
              <h5>Actions</h5>
              <div className="d-grid gap-2">
                <Button 
                  variant="primary" 
                  onClick={() => navigate(`/tasks/${id}/edit`)}
                >
                  Edit Task
                </Button>
                <Button 
                  variant="danger" 
                  onClick={handleDelete}
                >
                  Delete Task
                </Button>
                <Button 
                  variant="outline-secondary" 
                  onClick={() => navigate('/')}
                >
                  Back to All Tasks
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default TaskDetail;
