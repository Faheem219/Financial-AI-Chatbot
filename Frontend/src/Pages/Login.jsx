// /src/Pages/Login.jsx
import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { loginUser } from '../api/api';
import { useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await loginUser({ email, password });
      login(data, ''); // Pass an empty token if not used
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <StyledWrapper>
      <form onSubmit={handleSubmit} className="form_main">
        <p className="heading">Login</p>
        {error && <p className="error">{error}</p>}
        <div className="inputContainer">
          <svg className="inputIcon" xmlns="http://www.w3.org/2000/svg" width={16} height={16} fill="#2e2e2e" viewBox="0 0 16 16">
            <path d="M13.106 7.222c0-2.967-2.249-5.032-5.482-5.032-3.35 0-5.646 2.318-5.646 5.702 0 3.493 2.235 5.708 5.762 5.708.862 0 1.689-.123 2.304-.335v-.862c-.43.199-1.354.328-2.29.328-2.926 0-4.813-1.88-4.813-4.798 0-2.844 1.921-4.881 4.594-4.881 2.735 0 4.608 1.688 4.608 4.156 0 1.682-.554 2.769-1.416 2.769-.492 0-.772-.28-.772-.76V5.206H8.923v.834h-.11c-.266-.595-.881-.964-1.6-.964-1.4 0-2.378 1.162-2.378 2.823 0 1.737.957 2.906 2.379 2.906.8 0 1.415-.39 1.709-1.087h.11c.081.67.703 1.148 1.503 1.148 1.572 0 2.57-1.415 2.57-3.643zm-7.177.704c0-1.197.54-1.907 1.456-1.907.93 0 1.524.738 1.524 1.907S8.308 9.84 7.371 9.84c-.895 0-1.442-.725-1.442-1.914z" />
          </svg>
          <input
            type="email"
            className="inputField"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
          />
        </div>
        <div className="inputContainer">
          <svg className="inputIcon" xmlns="http://www.w3.org/2000/svg" width={16} height={16} fill="#2e2e2e" viewBox="0 0 16 16">
            <path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z" />
          </svg>
          <input
            type="password"
            className="inputField"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
        </div>
        <button type="submit" id="button">Login</button>
        <span>Don't have an account? </span>
        <Link className="forgotLink" to="/auth/SignUp">Sign-Up</Link>
      </form>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  .form_main {
    width: 380px; /* Increased width for better readability */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: rgb(255, 255, 255);
    padding: 40px; /* Increased padding for better spacing */
    box-shadow: 0px 0px 40px rgba(0, 0, 0, 0.062);
    position: relative;
    overflow: hidden;
  }

  .form_main::before {
    position: absolute;
    content: "";
    width: 350px; /* Adjusted size to match new form width */
    height: 350px;
    background-color: rgb(209, 193, 255);
    transform: rotate(45deg);
    left: -200px;
    bottom: 40px;
    z-index: 1;
    border-radius: 30px;
    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.082);
  }

  .heading {
    font-size: 2.5em; /* Larger font for heading */
    color: #2e2e2e;
    font-weight: 700;
    margin: 10px 0 20px 0;
    z-index: 2;
  }

  .inputContainer {
    width: 100%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
  }

  .inputIcon {
    position: absolute;
    left: 3px;
  }

  .inputField {
    width: 100%;
    height: 40px; /* Increased input height */
    background-color: transparent;
    border: none;
    border-bottom: 2px solid rgb(173, 173, 173);
    margin: 15px 0;
    color: black;
    font-size: 1.1em; /* Increased font size for inputs */
    font-weight: 500;
    box-sizing: border-box;
    padding-left: 30px;
  }

  .inputField:focus {
    outline: none;
    border-bottom: 2px solid rgb(199, 114, 255);
  }

  .inputField::placeholder {
    color: rgb(80, 80, 80);
    font-size: 1.1em; /* Increased placeholder font size */
    font-weight: 500;
  }

  #button {
    z-index: 2;
    position: relative;
    width: 100%;
    border: none;
    background-color: rgb(162, 104, 255);
    height: 45px; /* Larger button */
    color: white;
    font-size: 1.1em; /* Increased button font size */
    font-weight: 500;
    letter-spacing: 1px;
    margin: 15px 0;
    cursor: pointer;
  }

  #button:hover {
    background-color: rgb(126, 84, 255);
  }

  .forgotLink {
    z-index: 2;
    font-size: 1em; /* Larger font for forgot password */
    font-weight: 500;
    color: rgb(44, 24, 128);
    text-decoration: none;
    padding: 8px 15px;
    border-radius: 20px;
  }

  .error {
    color: red;
    font-size: 1em;
    margin-bottom: 15px;
  }
`;

export default Login;
