import { useState } from "react"
import api from "../api"
import { useNavigate } from "react-router-dom"
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants"
import image from "../assets/image.png"

function Form({ route, method }) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const name = method === "login" ? "Login" : "Register"

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await api.post(route, { username, password })
      if (method === "login") {
        localStorage.setItem(ACCESS_TOKEN, res.data.access)
        localStorage.setItem(REFRESH_TOKEN, res.data.refresh)
        navigate("/")
      } else {
        navigate("/login")
      }
    } catch (error) {
      alert(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-image">
        <img src={image} alt="Fitness" />
      </div>

      <form onSubmit={handleSubmit} className="form-container">
        <h2 className="form-title">Welcome Back</h2>

        <input
          className="form-input"
          type="email"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="example@mail.com"
        />

        <input
          className="form-input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="********"
        />

        <p className="forgot-password">Forgot password?</p>

        <button className="form-button" type="submit" disabled={loading}>
          {loading ? "Loading..." : name}
        </button>

        <p className="signup-text">
          Don't have an account?{" "}
          <span onClick={() => navigate("/register")} style={{ cursor: "pointer" }}>
            Sign up
          </span>
        </p>
      </form>
    </div>
  )
}

export default Form