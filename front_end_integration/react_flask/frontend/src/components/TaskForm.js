import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Button, Card, Alert } from 'react-bootstrap';
import { getTask, createTask, updateTask } from '../services/tasks';

const TaskForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'pending'
  });
  
  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTask = async () => {
      if (isEditMode) {
        try {
          setLoading(true);
          const taskData = await getTask(id);
          setFormData({
            title: taskData.title,
            description: taskData.description || '',
            status: taskData.status
          });
          setError(null);
        } catch (err) {
          console.error('Error fetching task:', err);
          setError('Failed to load task details. Please try again later.');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchTask();
  }, [id, isEditMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSubmitting(true);
      
      if (isEditMode) {
        await updateTask(id, formData);
      } else {
        await createTask(formData);
      }
      
      navigate('/');
    } catch (err) {
      console.error('Error saving task:', err);
      setError('Failed to save task. Please try again later.');
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-center mt-5">Loading task details...</div>;
  }

  return (
    <div>
      <h1>{isEditMode ? 'Edit Task' : 'Add New Task'}</h1>
      
      <Card className="mt-4">
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3" controlId="taskTitle">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Enter task title"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="taskDescription">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Enter task description"
              />
            </Form.Group>

            <Form.Group className="mb-4" controlId="taskStatus">
              <Form.Label>Status</Form.Label>
              <Form.Select
                name="status"
                value={formData.status}
                onChange={handleChange}
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </Form.Select>
            </Form.Group>

            <div className="d-flex justify-content-between">
              <Button variant="primary" type="submit" disabled={submitting}>
                {submitting ? 'Saving...' : 'Save Task'}
              </Button>
              <Button
                variant="outline-secondary"
                onClick={() => navigate(isEditMode ? `/tasks/${id}` : '/')}
                disabled={submitting}
              >
                Cancel
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default TaskForm;
