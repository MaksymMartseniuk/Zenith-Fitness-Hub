import { authService } from "../services/auth.service";
import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';

export function VerifyEmail() {
    const { uid, token } = useParams<{ uid: string; token: string }>();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [errorMessage, setErrorMessage] = useState('');

    const hasFetched = useRef(false);

    useEffect(()=>{
        if (!uid || !token || hasFetched.current) return;
        hasFetched.current = true;

        const verifyEmail = async () => {
            try{
                await authService.verifyEmail(uid, token);
                setStatus('success');
            }
            catch(err: any){
                setStatus('error');
                setErrorMessage(err.response?.data?.message || 'Invalid or expired verification link.');
            }
        };

        verifyEmail();

    }, [uid, token]);

    return (
            <div className="verify-page">
            <div className="verify-card">
                
                {status === 'loading' && (
                    <div className="verify-content">
                        <div className="success-icon spinner-icon">⏳</div>
                        <h3>Verifying your account...</h3>
                        <p>Please wait a moment while we confirm your details.</p>
                    </div>
                )}

                {status === 'success' && (
                    <div className="verify-content">
                        <div className="success-icon">✅</div>
                        <h3>Account Activated!</h3>
                        <p>Your email has been verified. You can now access your Zenith Fitness Hub.</p>
                        <Link to="/login" className="auth-submit-btn verify-btn">
                            Go to Login
                        </Link>
                    </div>
                )}

                {status === 'error' && (
                    <div className="verify-content">
                        <div className="success-icon">❌</div>
                        <h3>Verification Failed</h3>
                        <div className="error-message">
                            {errorMessage}
                        </div>
                        <p>The link might have expired or your account is already verified.</p>
                        <Link to="/register" className="auth-submit-btn verify-btn">
                            Back to Registration
                        </Link>
                    </div>
                )}

            </div>
        </div>
    );
}
