import { Link } from 'react-router-dom';

export function Home() {
    const features_data=[{
        id:1,
        title:'AI Form Check',
        description:'Real-time skeleton tracking using YOLOv11 to spot biomechanical errors in your squats and deadlifts.',
        icon:"src/media/icons/camera.png"
    },
    {
        id:2,
        title:'Smart Coaching',
        description:'Personalized feedback and training adjustments powered by Llama 3 based on your workout data.',
        icon:"src/media/icons/brain.png"
    },
    {
        id:3,
        title:'360° Tracking',
        description:'Log your sleep, nutrition, and strength progress to see the full picture of your fitness journey.',
        icon:"src/media/icons/chart.png"
    }]
    return(
        <>
            <header>
                <nav>
                    <div>Zenith Fitness Hub</div>
                    <ul>
                        <li>
                            <Link to="/login" className="btn btn-outline">Login</Link>
                        </li>
                        <li>
                            <Link to="/register" className="btn btn-primary">Register</Link>
                        </li>
                    </ul>
                </nav>
            </header>
            <main>
                <section >
                    <text>AI-powered squat analysis to help you hit the ZENITH of your physical form.</text>
                    <Link to="/register" className="btn btn-large">Try AI Analysis</Link>
                    <img src="src/media/square_analysis.png" alt="Square Analysis" />
                </section>

                <section>
                    {features_data.map((feature)=>(
                        <div key={feature.id}>
                            <img src={feature.icon} alt={feature.title} />
                            <h3>{feature.title}</h3>
                            <p>{feature.description}</p>
                        </div>
                    ))}
                </section>
            </main>
        </>
    )
}