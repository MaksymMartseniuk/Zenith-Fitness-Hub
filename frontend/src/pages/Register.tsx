import { Link,useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { AuthLayout } from '../components/layout/AuthLayout';
export function Register(){
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {}
    return(
        <AuthLayout>
            <form className='auth-form' onSubmit={handleSubmit}>
                <h2 className="auth-title">Create an Account</h2>
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
                <div className="input-group">
                    <label className="auth-label">Confirm Password</label>
                    <input 
                        type="password" 
                        value={confirmPassword}
                        className="auth-input"
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        placeholder="***************"
                    />
                </div>
                <button 
                    type="submit"
                    className="auth-submit-btn"
                    disabled={isLoading}
                >
                    {isLoading ? 'Loading...' : 'Register'}
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
                <p>Already have an account? <Link to='/login' className="register-link">Log In</Link></p>
            </div>
        </AuthLayout>
    )
    
}