import { Link,useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { AuthLayout } from '../components/layout/AuthLayout';
import '../styles/Auth.css';
import {tokenService} from '../services/token.service';
import api from '../services/api.service';
export function Login(){
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        try {
            const response = await api.post('/api/user/login/', { email, password });
            const { access, refresh } = response.data;
            tokenService.setTokens(access, refresh);
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.message || 'Login failed. Please try again.');
        } finally {
            setIsLoading(false);
        }

    }

    return(
        <AuthLayout>
            <form className='auth-form' onSubmit={handleSubmit}>
                <h2 className="auth-title">Welcome Back</h2>
                <div className="input-group">
                    <label htmlFor="email" className="auth-label">Email</label>
                    <input 
                        type="email" 
                        value={email}
                        className="auth-input"
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        placeholder="Enter your email"
                    />
                </div>
                <div className="input-group">
                    <label className="auth-label">Password</label>
                    <input 
                        type="password" 
                        value={password}
                        className="auth-input"
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        placeholder="***************"
                    />
                </div>
                <button 
                    type="submit"
                    className="auth-submit-btn"
                    disabled={isLoading}
                >
                    {isLoading ? 'Loading...' : 'Log In'}
                </button>
            </form>
            <div className="auth-divider">
                <span>or continue with</span>
            </div>
            <div className="auth-socials">
                <Link to='' className="social-btn">Google</Link>
                <Link to='' className="social-btn telegram-btn">Telegram</Link>
            </div>
           <div className="auth-footer-links">
                <Link to='/forgot-password' className="forgot-link">Forgot Password?</Link>
                <p>Don't have an account? <Link to='/register' className="register-link">Register</Link></p>
            </div>
            
        </AuthLayout>
    )
    
}