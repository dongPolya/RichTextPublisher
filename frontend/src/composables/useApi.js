import { ref } from 'vue'

// 根据当前环境设置API基础URL
const baseURL = import.meta.env.MODE === 'development'
  ? 'http://localhost:5000/api'
  : '/api'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const request = async (url, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const requestOptions = {
        ...options,
        credentials: 'include'
      }

      // 如果是 FormData，不设置 Content-Type（浏览器会自动设置）
      // 否则设置为 application/json
      if (!(requestOptions.body instanceof FormData)) {
        requestOptions.headers = {
          'Content-Type': 'application/json',
          ...requestOptions.headers
        }

        // 如果不是 FormData 且有 body，且body还不是字符串，则将其转换为 JSON 字符串
        if (requestOptions.body && typeof requestOptions.body === 'object' && !(typeof requestOptions.body === 'string')) {
          requestOptions.body = JSON.stringify(requestOptions.body)
        }
      }

      const response = await fetch(`${baseURL}${url}`, requestOptions)

      if (!response.ok) {
        const errorText = await response.text()
        let errorMessage = `HTTP error! status: ${response.status}`

        try {
          const errorData = JSON.parse(errorText)
          errorMessage = errorData.error || errorMessage
        } catch (e) {
          // 如果不是JSON格式，使用原始文本
          if (errorText) {
            errorMessage = errorText
          }
        }

        throw new Error(errorMessage)
      }

      const data = await response.json()
      return data
    } catch (err) {
      error.value = err.message
      console.error('API request failed:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const get = (url) => request(url)

  const post = (url, data) => {
    // 如果是 FormData，直接传递，不设置 Content-Type
    if (data instanceof FormData) {
      return request(url, {
        method: 'POST',
        body: data
      })
    } else {
      // 对于普通对象，直接传递给request处理
      return request(url, {
        method: 'POST',
        body: data
      })
    }
  }

  const put = (url, data) =>
    request(url, {
      method: 'PUT',
      body: data
    })

  const del = (url) =>
    request(url, {
      method: 'DELETE'
    })

  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del
  }
}
