// import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
// import { useApi } from '../api/api';

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Dashboard</h1>
      <p className='text-red'>Welcome</p>
    </div>
  );
}