import { Link,useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { AuthLayout } from '../components/layout/AuthLayout';
import '../styles/Auth.css';
import { authService } from '../services/auth.service';
export function Register(){
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const [isSuccess, setIsSuccess] = useState(false);
    const [isPasswordFocused, setIsPasswordFocused] = useState(false);
    const [isPasswordConfirmFocused, setIsPasswordConfirmFocused] = useState(false);

    const navigate = useNavigate();

    const passwordRules = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[^A-Za-z0-9]/.test(password)
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if(!Object.values(passwordRules).every(Boolean)) {
            setError('Password does not meet the requirements');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            await authService.register(email, password);
            //navigate('/login');
            setIsSuccess(true);
            const timer = setTimeout(() => {
                navigate('/login');
            }, 5000);
            return () => clearTimeout(timer);
        } catch (err: any) {
            setError(err.response?.data?.message || 'Registration failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }

    if(isSuccess) {
        return (
            <AuthLayout>
                <div className="success-message-container">
                    <div className="success-icon">✉️</div>
                    <h3>We've sent you a link!</h3>
                    <p>Please check your inbox at <strong>{email}</strong> to verify your account and start your fitness journey.</p>
                    
                    <Link to="/login" className="auth-submit-btn" style={{ display: 'inline-block', textAlign: 'center', textDecoration: 'none', marginTop: '20px' }}>
                        Go to Login
                    </Link>
                </div>
            </AuthLayout>
        )
    }

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
                        onFocus={() => setIsPasswordFocused(true)}
                        onBlur={() => setIsPasswordFocused(false)}
                        required
                        placeholder="***************"
                    />

                    {isPasswordFocused && (
                        <div className="password-requirements">
                            <p>Password must contain:</p>
                            <ul>
                                <li className={passwordRules.length ? 'valid' : 'invalid'}>
                                    {passwordRules.length ? '✓' : '○'} At least 8 characters
                                </li>
                                <li className={passwordRules.uppercase ? 'valid' : 'invalid'}>
                                    {passwordRules.uppercase ? '✓' : '○'} One uppercase letter
                                </li>
                                <li className={passwordRules.number ? 'valid' : 'invalid'}>
                                    {passwordRules.number ? '✓' : '○'} One number
                                </li>
                                <li className={passwordRules.special ? 'valid' : 'invalid'}>
                                    {passwordRules.special ? '✓' : '○'} One special character
                                </li>
                            </ul>
                        </div>
                    )}

                </div>
                <div className="input-group">
                    <label className="auth-label">Confirm Password</label>
                    <input 
                        type="password" 
                        value={confirmPassword}
                        className="auth-input"
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        onFocus={() => setIsPasswordConfirmFocused(true)}
                        onBlur={() => setIsPasswordConfirmFocused(false)}
                        required
                        placeholder="***************"
                    />
                    {isPasswordConfirmFocused && (
                        <div className="password-requirements">
                            <p>Passwords must match</p>
                            <ul>
                                <li className={password && password === confirmPassword ? 'valid' : 'invalid'}>
                                    {password === confirmPassword ? '✓' : '○'} Passwords match
                                </li>
                            </ul>
                        </div>
                    )}
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