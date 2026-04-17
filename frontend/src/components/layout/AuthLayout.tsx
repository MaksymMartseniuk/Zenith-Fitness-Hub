import { ReactNode } from "react";
import '../../styles/AuthLayout.css';

interface AuthLayoutProps {
    children: ReactNode;
}

export function AuthLayout({children }: AuthLayoutProps) {
    return (
        <>
            <div className="auth-grid">
                <div className="auth-image-wrapper">
                    <img src="/media/deadlift_analysis.png" alt="AI Analysis" />
                    <div className="auth-image-overlay"></div>
                </div>
                <div className="auth-content">
                    <div className="auth-card">
                    {children}
                    </div>
                </div>
            </div>
        </>
    )
}