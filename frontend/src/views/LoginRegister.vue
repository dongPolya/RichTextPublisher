<template>
  <div class="auth-container">
    <div class="auth-background"></div>
    <div class="auth-card">
      <div class="auth-header">
        <h2>{{ isRegister ? 'Create Account' : 'Welcome Back' }}</h2>
        <p>{{ isRegister ? 'Join our travel community' : 'Sign in to your account' }}</p>
      </div>

      <!-- 登录表单 -->
      <form v-if="!isRegister" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <input
            v-model="loginForm.email"
            type="email"
            placeholder="Email"
            required
            class="form-input"
            autocomplete="username"
          >
        </div>
        <div class="form-group">
          <input
            v-model="loginForm.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            required
            class="form-input"
            autocomplete="current-password"
          >
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="password-toggle"
          >
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>

        <button type="submit" :disabled="loading" class="auth-button">
          <span v-if="loading">Signing in...</span>
          <span v-else>Sign In</span>
        </button>

        <div class="auth-links">
          <a href="#" @click.prevent="toggleMode" class="auth-link">
            Don't have an account? Sign up
          </a>
          <a href="#" class="auth-link">Forgot password?</a>
        </div>
      </form>

      <!-- 注册表单 - 步骤1: 邮箱验证 -->
      <form v-else-if="registerStep === 1" @submit.prevent="handleSendCode" class="auth-form">
        <div class="form-group">
          <input
            v-model="registerForm.email"
            type="email"
            placeholder="Email"
            required
            class="form-input"
          >
        </div>

        <button type="submit" :disabled="loading" class="auth-button">
          <span v-if="loading">Sending code...</span>
          <span v-else>Send Verification Code</span>
        </button>

        <div class="auth-links">
          <a href="#" @click.prevent="toggleMode" class="auth-link">
            Already have an account? Sign in
          </a>
        </div>
      </form>

      <!-- 注册表单 - 步骤2: 验证码验证 -->
      <form v-else-if="registerStep === 2" @submit.prevent="handleVerifyCode" class="auth-form">
        <div class="form-group">
          <input
            v-model="registerForm.email"
            type="email"
            disabled
            class="form-input"
          >
        </div>
        <div class="form-group">
          <input
            v-model="registerForm.code"
            type="text"
            placeholder="Verification Code"
            maxlength="6"
            required
            class="form-input"
          >
        </div>

        <button type="submit" :disabled="loading" class="auth-button">
          <span v-if="loading">Verifying...</span>
          <span v-else>Verify Code</span>
        </button>

        <div class="auth-links">
          <a href="#" @click="registerStep = 1" class="auth-link">
            Back to email
          </a>
        </div>
      </form>

      <!-- 注册表单 - 步骤3: 设置用户名密码 -->
      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <input
            v-model="registerForm.username"
            type="text"
            placeholder="Username"
            required
            class="form-input"
          >
        </div>
        <div class="form-group">
          <input
            v-model="registerForm.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            required
            class="form-input"
            autocomplete="new-password"
          >
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="password-toggle"
          >
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>
        <div class="form-group">
          <input
            v-model="registerForm.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            placeholder="Confirm Password"
            required
            class="form-input"
            autocomplete="new-password"
          >
          <button
            type="button"
            @click="showConfirmPassword = !showConfirmPassword"
            class="password-toggle"
          >
            <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>

        <div v-if="passwordError" class="error-message">
          {{ passwordError }}
        </div>

        <button
          type="submit"
          :disabled="loading || !isRegisterFormValid"
          class="auth-button"
        >
          <span v-if="loading">Creating account...</span>
          <span v-else>Create Account</span>
        </button>

        <div class="auth-links">
          <a href="#" @click="registerStep = 2" class="auth-link">
            Back to verification
          </a>
        </div>
      </form>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginRegister',
  setup() {
    const store = useStore()
    const router = useRouter()

    const isRegister = ref(false)
    const registerStep = ref(1)
    const loading = ref(false)
    const error = ref('')
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
 // 调试信息
  console.log('LoginRegister - Current user state:', store.state.user)
  console.log('LoginRegister - Auth checked:', store.state.authChecked)
console.log('LoginRegister - Current auth state:', {
  user: store.state.user,
  isAuthenticated: store.state.isAuthenticated,
  authChecked: store.state.authChecked
})
  // 如果已经登录，重定向到首页
  if (store.state.user) {
    console.log('User already logged in, redirecting to home')
    router.push('/')
  }
    const loginForm = ref({
      email: '',
      password: ''
    })

    const registerForm = ref({
      email: '',
      code: '',
      username: '',
      password: '',
      confirmPassword: ''
    })

    // 密码验证
    const passwordError = computed(() => {
       const { password, confirmPassword, username } = registerForm.value

      // 如果所有字段都为空，不显示错误
      if (!password && !confirmPassword && !username) {
        return ''
      }

      // 检查必需字段是否已填写
      if (!username.trim()) {
        return 'Username is required'
      }

      if (!password) {
        return 'Password is required'
      }

      if (!confirmPassword) {
        return 'Please confirm your password'
      }

      if (registerForm.value.password.length < 8) {
        return 'Password must be at least 8 characters long'
      }

      if (!/[A-Za-z]/.test(registerForm.value.password)) {
        return 'Password must contain at least one letter'
      }

      if (!/[0-9!@#$%^&*(),.?":{}|<>]/.test(registerForm.value.password)) {
        return 'Password must contain at least one number or special character'
      }

      if (registerForm.value.password !== registerForm.value.confirmPassword) {
        return 'Passwords do not match'
      }

      return ''
    })
     const isRegisterFormValid = computed(() => {
      const { username, password, confirmPassword } = registerForm.value

      // 检查所有必需字段是否已填写
      if (!username.trim() || !password || !confirmPassword) {
        return false
      }

      // 检查是否有密码错误
      if (passwordError.value) {
        return false
      }

      return true
    })

    const toggleMode = () => {
      isRegister.value = !isRegister.value
      registerStep.value = 1
      error.value = ''
      loginForm.value = { email: '', password: '' }
      registerForm.value = { email: '', code: '', username: '', password: '', confirmPassword: '' }
    }

   const handleLogin = async () => {
  loading.value = true;
  error.value = '';

  try {
    // 先检查登录状态
    const currentUser = await store.dispatch('checkAuth');
    if (currentUser) {
      console.log('用户已登录，跳转到首页');
      router.push('/');
      return;
    }

    await store.dispatch('login', loginForm.value);
    router.push('/');
  } catch (err) {
    console.error('登录错误:', err);
    if (err.message.includes('Already logged in')) {
      // 如果已经是登录状态，直接跳转
      router.push('/');
    } else {
      error.value = err.message || '登录失败';
    }
  } finally {
    loading.value = false;
  }
}

    const handleSendCode = async () => {
      loading.value = true
      error.value = ''

      try {
        await store.dispatch('sendVerificationCode', registerForm.value.email)
        registerStep.value = 2
      } catch (err) {
        error.value = err.message || 'Failed to send verification code'
      } finally {
        loading.value = false
      }
    }

    const handleVerifyCode = async () => {
      loading.value = true
      error.value = ''

      try {
        await store.dispatch('verifyCode', {
          email: registerForm.value.email,
          code: registerForm.value.code
        })
        registerStep.value = 3
      } catch (err) {
        error.value = err.message || 'Invalid verification code'
      } finally {
        loading.value = false
      }
    }

    const handleRegister = async () => {
      if (passwordError.value) return

      loading.value = true
      error.value = ''

      try {
        await store.dispatch('register', {
          email: registerForm.value.email,
          username: registerForm.value.username,
          password: registerForm.value.password
        })
        router.push('/')
      } catch (err) {
        error.value = err.message || 'Registration failed'
      } finally {
        loading.value = false
      }
    }
    // 添加调试信息，观察表单状态
    watch([registerForm, passwordError, isRegisterFormValid], () => {
      console.log('Form state:', {
        form: { ...registerForm.value },
        passwordError: passwordError.value,
        isRegisterFormValid: isRegisterFormValid.value
      })
    })

    // 如果已经登录，重定向到首页
    if (store.state.user) {
      router.push('/')
    }

    return {
      isRegister,
      registerStep,
      loading,
      error,
      showPassword,
      showConfirmPassword,
      loginForm,
      registerForm,
      isRegisterFormValid,
      passwordError,
      toggleMode,
      handleLogin,
      handleSendCode,
      handleVerifyCode,
      handleRegister
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
#app .auth-container ~ * {
  display: none !important;
}
.auth-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-image: url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2730&q=80');
  background-size: cover;
  background-position: center;
  opacity: 0.8;
}

.auth-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h2 {
  color: #333;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.auth-header p {
  color: #666;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background-color: #f8f9fa;
  opacity: 0.7;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 0.25rem;
}

.auth-button {
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.auth-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.auth-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  text-align: center;
  transition: color 0.3s ease;
}

.auth-link:hover {
  color: #764ba2;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #fcc;
  font-size: 0.9rem;
  margin-top: 1rem;
  text-align: center;
}

@media (max-width: 480px) {
  .auth-card {
    margin: 1rem;
    padding: 2rem 1.5rem;
  }
}
</style>