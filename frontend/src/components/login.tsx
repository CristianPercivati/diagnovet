import React from "react";

const Login: React.FC = () => {
  return (
  <div className="container">
        <div className="screen login-screen">
            <div className="logo"></div>
            <h2 className="login-title">DiagnoVET</h2>
            <p className="login-subtitle">Accede a tu plataforma de diagnóstico veterinario</p>
            <form className="width: 100%;">
                <div className="form-group">
                    <label>Email</label>
                    <input type="email" placeholder="tu@email.com" />
                </div>
                <div className="form-group">
                    <label>Contraseña</label>
                    <input type="password" placeholder="••••••••" />
                </div>
                <button type="button" className="login-btn">Iniciar Sesión</button>
            </form>
            
            <p className="margin-top: 20px; color: #666; font-size: 0.9rem; text-align: center;">
                ¿Problemas para acceder? <a href="#" className="color: #4CAF50;">Contacta soporte</a>
            </p>
        </div>
        </div>
  )
}

export default Login;
