import api from './api.service';
export const authService = {
    login: async (email: string, password: string) => {
        const response = await api.post('/api/user/login/', { email, password });
        return response;
    },
    register: async (email: string, password: string) => {
        const response = await api.post('/api/user/register/', { email, password });
        return response;
    },
    logout: () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    },
    verifyEmail: async (uid: string, token: string) => {
        const response = await api.post(`/api/user/verify-email/${uid}/${token}/`);
        return response;
    }
}