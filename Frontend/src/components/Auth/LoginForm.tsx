import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { TrendingUp, Eye, EyeOff, Lock, User, Mail, Shield, ArrowRight, Sparkles } from 'lucide-react';

interface LoginFormProps {
  onToggleMode: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onToggleMode }) => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(formData);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{animationDelay: '4s'}}></div>
      </div>
      
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-grid-16"></div>
      
      <div className="relative z-10 min-h-screen flex">
        {/* Left side - Welcome content */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-center px-12 text-white">
          <div className="animate-fadeInUp">
            <div className="flex items-center mb-8">
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 mr-4">
                <TrendingUp className="h-12 w-12 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold">Trading System</h1>
                <p className="text-xl text-white/80">Advanced Trading Platform</p>
              </div>
            </div>
            
            <div className="space-y-6 mb-12">
              <div className="flex items-center space-x-4 animate-slideInRight" style={{animationDelay: '0.2s'}}>
                <div className="bg-white/10 backdrop-blur-lg rounded-full p-3">
                  <Shield className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Secure Trading</h3>
                  <p className="text-white/70">Bank-level security for your investments</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4 animate-slideInRight" style={{animationDelay: '0.4s'}}>
                <div className="bg-white/10 backdrop-blur-lg rounded-full p-3">
                  <Sparkles className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Real-time Analytics</h3>
                  <p className="text-white/70">Advanced market insights and predictions</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4 animate-slideInRight" style={{animationDelay: '0.6s'}}>
                <div className="bg-white/10 backdrop-blur-lg rounded-full p-3">
                  <TrendingUp className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Portfolio Management</h3>
                  <p className="text-white/70">Intelligent risk assessment and management</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right side - Login form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12">
          <div className="w-full max-w-md">
            {/* Mobile header - shown only on small screens */}
            <div className="lg:hidden text-center mb-8 text-white animate-fadeInUp">
              <div className="flex justify-center mb-4">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4">
                  <TrendingUp className="h-10 w-10 text-white" />
                </div>
              </div>
              <h1 className="text-3xl font-bold">Trading System</h1>
              <p className="text-white/80">Advanced Trading Platform</p>
            </div>
            
            {/* Login form card */}
            <div className="glass rounded-3xl p-8 shadow-2xl backdrop-blur-xl border border-white/20 animate-fadeInUp" style={{animationDelay: '0.3s'}}>
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">
                  Welcome Back
                </h2>
                <p className="text-white/70">
                  Sign in to continue your trading journey
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-500/10 backdrop-blur-lg border border-red-500/20 rounded-2xl p-4 animate-fadeInUp">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                      <p className="text-red-300 text-sm font-medium">{error}</p>
                    </div>
                  </div>
                )}
                
                <div className="space-y-5">
                  {/* Username field */}
                  <div className="relative group">
                    <label 
                      htmlFor="username" 
                      className={`absolute left-4 transition-all duration-200 pointer-events-none ${
                        focusedField === 'username' || formData.username
                          ? '-top-2 text-xs bg-white/10 px-2 rounded text-white/90'
                          : 'top-4 text-white/60'
                      }`}
                    >
                      Username
                    </label>
                    <div className="relative">
                      <User className={`absolute left-4 top-4 h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'username' ? 'text-white' : 'text-white/60'
                      }`} />
                      <input
                        id="username"
                        name="username"
                        type="text"
                        required
                        value={formData.username}
                        onChange={handleChange}
                        onFocus={() => setFocusedField('username')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-2xl focus:outline-none focus:border-white/40 focus:bg-white/20 transition-all duration-200 text-white placeholder-white/50 backdrop-blur-lg"
                        placeholder={focusedField === 'username' ? 'Enter your username' : ''}
                      />
                    </div>
                  </div>
                  
                  {/* Password field */}
                  <div className="relative group">
                    <label 
                      htmlFor="password" 
                      className={`absolute left-4 transition-all duration-200 pointer-events-none ${
                        focusedField === 'password' || formData.password
                          ? '-top-2 text-xs bg-white/10 px-2 rounded text-white/90'
                          : 'top-4 text-white/60'
                      }`}
                    >
                      Password
                    </label>
                    <div className="relative">
                      <Lock className={`absolute left-4 top-4 h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'password' ? 'text-white' : 'text-white/60'
                      }`} />
                      <input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        required
                        value={formData.password}
                        onChange={handleChange}
                        onFocus={() => setFocusedField('password')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full pl-12 pr-12 py-4 bg-white/10 border border-white/20 rounded-2xl focus:outline-none focus:border-white/40 focus:bg-white/20 transition-all duration-200 text-white placeholder-white/50 backdrop-blur-lg"
                        placeholder={focusedField === 'password' ? 'Enter your password' : ''}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-4 top-4 text-white/60 hover:text-white transition-colors duration-200"
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Login button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="group relative w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-2xl transition-all duration-200 transform hover:scale-[1.02] hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  <span className="flex items-center justify-center space-x-2">
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        <span>Signing in...</span>
                      </>
                    ) : (
                      <>
                        <span>Sign In</span>
                        <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform duration-200" />
                      </>
                    )}
                  </span>
                </button>
                
                {/* Register link */}
                <div className="text-center">
                  <p className="text-white/70 text-sm">
                    Don't have an account?{' '}
                    <button
                      type="button"
                      onClick={onToggleMode}
                      className="text-blue-300 hover:text-blue-200 font-semibold transition-colors duration-200 hover:underline"
                    >
                      Create one here
                    </button>
                  </p>
                </div>
              </form>
            </div>
            
            {/* Footer */}
            <div className="text-center mt-8 text-white/50 text-sm">
              <p>© 2024 Trading System. Secure. Reliable. Profitable.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};