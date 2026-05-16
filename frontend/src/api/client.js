import axios from "axios";

const api = axios.create({
  baseURL:
    process.env.REACT_APP_API_URL ||
    "http://localhost:5000",

  withCredentials: true,

  headers: {
    "Content-Type":
      "application/json",
  },
});


// Attach token automatically
api.interceptors.request.use(
  (config) => {

    const token =
      localStorage.getItem("token");

    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);


export const authAPI = {

  register: (data) =>
    api.post("/auth/register", data),

  login: (data) =>
    api.post("/auth/login", data),

  logout: () =>
    api.post("/auth/logout"),

  me: () =>
    api.get("/auth/me"),

  changePassword: (data) =>
    api.post(
      "/auth/change-password",
      data
    ),
};


export const resumeAPI = {

  upload: (formData) =>

    api.post(
      "/resume/upload",
      formData,
      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      }
    ),

  get: (id) =>
    api.get(`/resume/${id}`),

  list: (page = 1) =>
    api.get(`/resume/?page=${page}`),

  pollTask: (taskId) =>
    api.get(`/resume/task/${taskId}`),
};


export const evaluationAPI = {

  submit: (data) =>
    api.post("/evaluation/", data),

  get: (id) =>
    api.get(`/evaluation/${id}`),

  pollTask: (taskId) =>
    api.get(
      `/evaluation/task/${taskId}`
    ),
};


export const jobAPI = {

  create: (data) =>
    api.post("/job/", data),

  list: (page = 1) =>
    api.get(`/job/?page=${page}`),

  get: (id) =>
    api.get(`/job/${id}`),

  delete: (id) =>
    api.delete(`/job/${id}`),
};


export default api;