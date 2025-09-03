import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { TrendingUp, Eye, EyeOff, Lock, User, Mail, Shield, ArrowRight, Sparkles, UserPlus } from 'lucide-react';

interface RegisterFormProps {
  onToggleMode: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onToggleMode }) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🔍 Form submission started');
    console.log('📝 Form data:', formData);
    
    setIsLoading(true);
    setError('');

    // Validate required fields
    if (!formData.email || !formData.username || !formData.password) {
      const error = 'Please fill in all required fields';
      console.error('❌ Validation error:', error);
      setError(error);
      setIsLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      const error = 'Passwords do not match';
      console.error('❌ Password mismatch:', error);
      setError(error);
      setIsLoading(false);
      return;
    }

    try {
      const { confirmPassword, ...registerData } = formData;
      console.log('🚀 Calling register function with data:', registerData);
      
      // Check if register function exists
      if (typeof register !== 'function') {
        throw new Error('Register function is not available');
      }
      
      await register(registerData);
      console.log('✅ Registration successful!');
    } catch (error: any) {
      console.error('❌ Registration failed:', error);
      console.error('❌ Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setError(error.response?.data?.detail || error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    console.log(`📝 Field changed: ${name} = "${value}"`);
    
    setFormData({
      ...formData,
      [name]: value,
    });
    
    console.log('📝 Updated form data:', {
      ...formData,
      [name]: value,
    });
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-emerald-900 via-blue-900 to-indigo-800">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-emerald-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{animationDelay: '4s'}}></div>
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
                <h1 className="text-4xl font-bold">Join Trading System</h1>
                <p className="text-xl text-white/80">Start Your Trading Journey</p>
              </div>
            </div>
            
            <div className="space-y-6 mb-12">
              <div className="flex items-center space-x-4 animate-slideInRight" style={{animationDelay: '0.2s'}}>
                <div className="bg-white/10 backdrop-blur-lg rounded-full p-3">
                  <UserPlus className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Easy Registration</h3>
                  <p className="text-white/70">Get started in just a few minutes</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4 animate-slideInRight" style={{animationDelay: '0.4s'}}>
                <div className="bg-white/10 backdrop-blur-lg rounded-full p-3">
                  <Shield className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Secure & Protected</h3>
                  <p className="text-white/70">Your data is encrypted and safe with us</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4 animate-slideInRight" style={{animationDelay: '0.6s'}}>
                <div className="bg-white/10 backdrop-blur-lg rounded-full p-3">
                  <Sparkles className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Advanced Features</h3>
                  <p className="text-white/70">Access to premium trading tools</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right side - Register form */}
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
              <p className="text-white/80">Start Your Trading Journey</p>
            </div>
            
            {/* Register form card */}
            <div className="glass rounded-3xl p-8 shadow-2xl backdrop-blur-xl border border-white/20 animate-fadeInUp" style={{animationDelay: '0.3s'}}>
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">
                  Create Account
                </h2>
                <p className="text-white/70">
                  Join thousands of successful traders
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {error && (
                  <div className="bg-red-500/10 backdrop-blur-lg border border-red-500/20 rounded-2xl p-4 animate-fadeInUp">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                      <p className="text-red-300 text-sm font-medium">{error}</p>
                    </div>
                  </div>
                )}
                
                <div className="space-y-4">
                  {/* Email field */}
                  <div className="relative group">
                    <label 
                      htmlFor="email" 
                      className={`absolute left-4 transition-all duration-200 pointer-events-none ${
                        focusedField === 'email' || formData.email
                          ? '-top-2 text-xs bg-white/10 px-2 rounded text-white/90'
                          : 'top-4 text-white/60'
                      }`}
                    >
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className={`absolute left-4 top-4 h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'email' ? 'text-white' : 'text-white/60'
                      }`} />
                      <input
                        id="email"
                        name="email"
                        type="email"
                        required
                        value={formData.email}
                        onChange={handleChange}
                        onFocus={() => setFocusedField('email')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-2xl focus:outline-none focus:border-white/40 focus:bg-white/20 transition-all duration-200 text-white placeholder-white/50 backdrop-blur-lg"
                        placeholder={focusedField === 'email' ? 'Enter your email' : ''}
                      />
                    </div>
                  </div>
                  
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
                        placeholder={focusedField === 'username' ? 'Choose a username' : ''}
                      />
                    </div>
                  </div>
                  
                  {/* Full name field */}
                  <div className="relative group">
                    <label 
                      htmlFor="full_name" 
                      className={`absolute left-4 transition-all duration-200 pointer-events-none ${
                        focusedField === 'full_name' || formData.full_name
                          ? '-top-2 text-xs bg-white/10 px-2 rounded text-white/90'
                          : 'top-4 text-white/60'
                      }`}
                    >
                      Full Name (Optional)
                    </label>
                    <div className="relative">
                      <User className={`absolute left-4 top-4 h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'full_name' ? 'text-white' : 'text-white/60'
                      }`} />
                      <input
                        id="full_name"
                        name="full_name"
                        type="text"
                        value={formData.full_name}
                        onChange={handleChange}
                        onFocus={() => setFocusedField('full_name')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-2xl focus:outline-none focus:border-white/40 focus:bg-white/20 transition-all duration-200 text-white placeholder-white/50 backdrop-blur-lg"
                        placeholder={focusedField === 'full_name' ? 'Enter your full name' : ''}
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
                        placeholder={focusedField === 'password' ? 'Create a password' : ''}
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
                  
                  {/* Confirm password field */}
                  <div className="relative group">
                    <label 
                      htmlFor="confirmPassword" 
                      className={`absolute left-4 transition-all duration-200 pointer-events-none ${
                        focusedField === 'confirmPassword' || formData.confirmPassword
                          ? '-top-2 text-xs bg-white/10 px-2 rounded text-white/90'
                          : 'top-4 text-white/60'
                      }`}
                    >
                      Confirm Password
                    </label>
                    <div className="relative">
                      <Lock className={`absolute left-4 top-4 h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'confirmPassword' ? 'text-white' : 'text-white/60'
                      }`} />
                      <input
                        id="confirmPassword"
                        name="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        required
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        onFocus={() => setFocusedField('confirmPassword')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full pl-12 pr-12 py-4 bg-white/10 border border-white/20 rounded-2xl focus:outline-none focus:border-white/40 focus:bg-white/20 transition-all duration-200 text-white placeholder-white/50 backdrop-blur-lg"
                        placeholder={focusedField === 'confirmPassword' ? 'Confirm your password' : ''}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-4 top-4 text-white/60 hover:text-white transition-colors duration-200"
                      >
                        {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Register button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  onClick={() => console.log('💆 Register button clicked!')}
                  className="group relative w-full bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white font-semibold py-4 px-6 rounded-2xl transition-all duration-200 transform hover:scale-[1.02] hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none mt-6"
                >
                  <span className="flex items-center justify-center space-x-2">
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        <span>Creating account...</span>
                      </>
                    ) : (
                      <>
                        <span>Create Account</span>
                        <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform duration-200" />
                      </>
                    )}
                  </span>
                </button>
                
                {/* Login link */}
                <div className="text-center">
                  <p className="text-white/70 text-sm">
                    Already have an account?{' '}
                    <button
                      type="button"
                      onClick={onToggleMode}
                      className="text-emerald-300 hover:text-emerald-200 font-semibold transition-colors duration-200 hover:underline"
                    >
                      Sign in here
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