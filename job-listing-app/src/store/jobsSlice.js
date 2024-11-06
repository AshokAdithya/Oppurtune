// store.js
import { createSlice } from "@reduxjs/toolkit";

const jobsSlice = createSlice({
  name: "jobs",
  initialState: {
    jobs: [],
    selectedJobId: null,
    page: 1,
    search: "",
    totalPages: 0,
    topCompanies: [],
    topLocations: [],
  },
  reducers: {
    setJobs(state, action) {
      state.jobs = action.payload;
    },
    setSelectedJob(state, action) {
      state.selectedJobId = action.payload;
    },
    setPage(state, action) {
      state.page = action.payload;
    },
    setSearch(state, action) {
      state.search = action.payload;
    },
    setTotalPages(state, action) {
      state.totalPages = action.payload;
    },
    setTopCompanies(state, action) {
      state.topCompanies = action.payload;
    },
    setTopLocations(state, action) {
      state.topLocations = action.payload;
    },
  },
});

// Export actions
export const {
  setJobs,
  setSelectedJob,
  setPage,
  setSearch,
  setTotalPages,
  setTopCompanies,
  setTopLocations,
} = jobsSlice.actions;

export default jobsSlice.reducer;
