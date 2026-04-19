import { BrowserRouter, Routes,Route,Navigate } from 'react-router-dom'
import { Home } from './pages/Home.tsx'
import { Login } from './pages/Login.tsx'
import { Register } from './pages/Register.tsx'
import { VerifyEmail } from './pages/VerifyEmail.tsx';
function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path='/verify-email/:uid/:token' element={<VerifyEmail />} /> 
        <Route path="*" element={<Navigate to="/" />} />

      </Routes>
    </BrowserRouter>
  )
}

export default App
