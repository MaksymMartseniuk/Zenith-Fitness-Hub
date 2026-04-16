import { Link } from 'react-router-dom';
import '../styles/Home.css';

export function Home() {
    const features_data=[{
        id:1,
        title:'AI Form Check',
        description:'Real-time skeleton tracking using YOLOv11 to spot biomechanical errors in your squats and deadlifts.',
        icon:"/media/icons/camera.png"
    },
    {
        id:2,
        title:'Smart Coaching',
        description:'Personalized feedback and training adjustments powered by Llama 3 based on your workout data.',
        icon:"/media/icons/brain.png"
    },
    {
        id:3,
        title:'360° Tracking',
        description:'Log your sleep, nutrition, and strength progress to see the full picture of your fitness journey.',
        icon:"/media/icons/chart.png"
    }]

    const explain_data=[{
        id:1,
        number: '01',
        title:'Record Your Set',
        description:'Simply record a side-view video of your heavy squats or deadlifts. No special equipment needed.'
    },
    {
        id:2,
        number: '02',
        title:'AI Extraction',
        description:'Our system uses YOLOv11 to map your skeleton and calculate joint angles in milliseconds.'
    },
    {
        id:3,
        number: '03',
        title:'Get Coached',
        description:'Llama 3 analyzes your biomechanics and provides instant feedback to fix your form and prevent injuries.'

    }]
    return(
        <div className="home-container">
            <header className="navbar_home">
                    <div className='logo'>Zenith Fitness Hub</div>
                    <ul className='nav-actions'>
                        <li>
                            <Link to="/login" className="btn btn-outline">Login</Link>
                        </li>
                        <li>
                            <Link to="/register" className="btn btn-primary">Register</Link>
                        </li>
                    </ul>
            </header>
            <main>
                <section className='hero-section'>
                    <div className="hero-content">
                        <h1>AI-powered squat analysis to help you hit the ZENITH of your physical form.</h1>
                        <Link  to="/register" className="btn btn-primary btn-large">Try AI Analysis</Link>
                    </div>
                    <div className="hero-image-wrapper">
                        <img src="/media/square_analysis.png" alt="Square Analysis" />
                    </div>
                </section>

                <section className='features-section'>
                    <div className="features-grid">
                        {features_data.map((feature)=>(
                            <div key={feature.id} className="feature-card">
                                <img src={feature.icon} alt={feature.title} className="feature-icon" />
                                <h3>{feature.title}</h3>
                                <p>{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </section>
                <section className="how-it-works-section">
                    <h2>How It Works?</h2>
                    <div className="steps-container">
                        {explain_data.map((step) => (
                            <div key={step.id} className="step-card">
                                <div className="step-header">
                                    <span className="step-number">{step.number}</span>
                                    <h3>{step.title}</h3>
                                </div>
                                <p>{step.description}</p>
                            </div>
                        ))}
                    </div>
                </section>
                <section className="cta-section">
                    <div className="cta-card">
                        <h2>Ready to hit the ZENITH of your performance?</h2>
                        <Link to="/register" className="btn btn-primary btn-large">Try AI Analysis Now</Link>
                    </div>
                </section>
            </main>
        </div>
    )
}