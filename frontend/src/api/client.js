import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'X-API-Key': 'test_api_key_12345',
  },
});

export const fetchSummary = () => api.get('/api/v1/dashboard/summary').then(r => r.data);
export const fetchCharts = () => api.get('/api/v1/dashboard/charts').then(r => r.data);
export const fetchCalls = (params) => api.get('/api/v1/dashboard/calls', { params }).then(r => r.data);
export const fetchLoadsMap = () => api.get('/api/v1/dashboard/loads/map').then(r => r.data);
export const fetchLoadsDetail = () => api.get('/api/v1/dashboard/loads/detail').then(r => r.data);
export const fetchCarriers = () => api.get('/api/v1/dashboard/carriers').then(r => r.data);
export const fetchCarrierDetail = (mc) => api.get(`/api/v1/dashboard/carriers/${mc}`).then(r => r.data);

export default api;
