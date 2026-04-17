import axios from "axios";
import { tokenService } from './token.service';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

const PUBLIC_ENDPOINTS=['/api/user/register',
    '/api/user/login',
    '/api/user/refresh-token/',
    '/api/user/forget-password/',
    '/api/user/reset-password/',
    '/api/user/verify-email/'];

api.interceptors.request.use(
    (config) => {
        const isPiblicEndpoint = PUBLIC_ENDPOINTS.some(endpoint => config.url?.includes(endpoint));
        if (!isPiblicEndpoint) {
            const accessToken = tokenService.getAccessToken();
            if (accessToken) {
                config.headers['Authorization'] = `Bearer ${accessToken}`;
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;