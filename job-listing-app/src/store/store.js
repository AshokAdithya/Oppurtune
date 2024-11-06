import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./authSlice"; // Import the auth slice
import jobsReducer from "./jobsSlice"; // Import the jobs slice

// Configure the store with both jobs and auth reducers
const store = configureStore({
  reducer: {
    auth: authReducer,
    jobs: jobsReducer,
  },
});

export default store;
