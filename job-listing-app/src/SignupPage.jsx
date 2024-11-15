// SignupPage.js
import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { login, logout } from "./store/authSlice";
import "./Auth.css";

const SignupPage = () => {
  const dispatch = useDispatch();
  const Navigate = useNavigate();

  useEffect(() => {
    const user = localStorage.getItem("user");
    if (user) {
      dispatch(login(user));
    } else {
      dispatch(logout());
    }
  });

  const { isAuthenticated } = useSelector((state) => state.auth);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match");
      return;
    }
    if (password === "") {
      setErrorMessage("Passwords cannot be empty");
      return;
    }
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/signup", {
        username,
        password,
      });
      console.log(response.data);
      if (response.data.success) {
        Navigate("/login");
      } else {
        setErrorMessage(response.data.message);
      }
    } catch (error) {
      setErrorMessage(response.data.message);
    }
  };

  if (isAuthenticated) {
    Navigate("/");
  }

  return (
    !isAuthenticated && (
      <div className="main-box">
        <div className="auth-container">
          <h2>Sign Up to Opportune</h2>
          {errorMessage && <p className="error">{errorMessage}</p>}
          <form onSubmit={handleSignup}>
            <div>
              <label>Username:</label>
              <input
                type="text"
                name="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <label>Password:</label>
              <input
                type="password"
                name="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div>
              <label>Confirm Password:</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit">Sign Up</button>
          </form>
          <p>
            Already have an account? <a href="/login">Login</a>
          </p>
        </div>
      </div>
    )
  );
};

export default SignupPage;
