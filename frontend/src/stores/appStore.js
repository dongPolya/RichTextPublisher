import { createStore } from 'vuex'
import { useApi } from '@/composables/useApi'

const { get, post, put, delete: del  } = useApi()
export default createStore({
  state: {
    user: null,
    communities: [],
    posts: [],
    currentQuestion: null,
    score: 0,
    authChecked: false, // 添加缺失的状态
    communityDetail: null, // 添加缺失的状态
    communityPosts: [], // 添加缺失的状态
    postDetail: null,// 添加缺失的状态
  },
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setCommunities(state, communities) {
      state.communities = communities
    },
    setPosts(state, posts) {
      state.posts = posts
    },
    setCurrentQuestion(state, question) {
      state.currentQuestion = question
    },
    incrementScore(state) {
      state.score += 10
    },
    addPost(state, post) {
      state.posts.unshift(post)
    },
    addCommunity(state, community) {
      state.communities.push(community)
    },
     setAuthChecked(state, status) {
      state.authChecked = status
    },
      setCommunityDetail(state, community) {
      state.communityDetail = community
    },
    setCommunityPosts(state, posts) {
      state.communityPosts = posts
    },
    setPostDetail(state, post) {
      state.postDetail = post
    },
    addComment(state, { postId, comment }) {
      const post = state.posts.find(p => p.id === postId)
      if (post) {
        if (!post.comments) post.comments = []
        post.comments.push(comment)
        post.comments_count = (post.comments_count || 0) + 1
      }
    }
  },
  actions: {
    // 检查登录状态
async checkAuth({ commit }) {
  try {
    const response = await get('/auth/me');

    // 确保返回的是有效的用户对象
    if (response && response.user && typeof response.user === 'object' && Object.keys(response.user).length > 0) {
      commit('setUser', response.user);
      return response.user;
    } else if (response && typeof response === 'object' && Object.keys(response).length > 0 && response.id) {
      // 如果直接返回用户对象而不是包装在user字段中
      commit('setUser', response);
      return response;
    } else {
      commit('setUser', null);
      return null;
    }
  } catch (error) {
    console.error('Auth check failed:', error);
    commit('setUser', null);
    throw error;
  } finally {
    commit('setAuthChecked', true);
  }
},


    // 登录
async login({ commit }, credentials) {
  try {
    // 先检查是否已经登录
    const currentUser = await this.dispatch('checkAuth');
    if (currentUser) {
      console.log('用户已经登录:', currentUser);
      return currentUser;
    }

    const user = await post('/auth/login', credentials);
    commit('setUser', user);
    return user;
  } catch (error) {
    console.error('登录失败:', error);
    commit('setUser', null);
    throw error;
  }
},


    // 注册 - 发送验证码
    async sendVerificationCode(_, email) {
      return await post('/auth/register/send-code', { email })
    },

    // 注册 - 验证验证码
    async verifyCode(_, { email, code }) {
      return await post('/auth/register/verify-code', { email, code })
    },

    // 注册
    async register({ commit }, userData) {
      try {
        const user = await post('/auth/register', userData)
        commit('setUser', user)
        return user
      } catch (error) {
        commit('setUser', null)
        throw error
      }
    },

    // 注销
    async logout({ commit }) {
      try {
        await post('/auth/logout')
      } catch (error) {
        console.error('Logout failed:', error)
      } finally {
        commit('setUser', null)
      }
    },

    // 删除账号
    async deleteAccount({ commit }) {
      try {
        await del('/auth/delete-account')
      } catch (error) {
        console.error('Delete account failed:', error)
        throw error
      } finally {
        commit('setUser', null)
      }
    },

    async fetchUser({ commit }, userId) {
      try {
        const user = await get(`/users/${userId}`)
        commit('setUser', user)
      } catch (error) {
        console.error('Failed to fetch user:', error)
      }
    },
    async fetchCommunities({ commit }) {
      try {
        const communities = await get('/communities')
        commit('setCommunities', communities)
      } catch (error) {
        console.error('Failed to fetch communities:', error)
        // 使用默认数据
        commit('setCommunities', [
          {
            id: 1,
            name: '旅行社',
            avatar: 'https://images.unsplash.com/photo-1590649880760-2d4b0f523de7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80',
            category: '出行交流',
            member_count: 342,
            post_count: 128,
            activity_score: 78
          },
          {
            id: 2,
            name: '电子音乐',
            avatar: 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80',
            category: '电子音乐',
            member_count: 278,
            post_count: 156,
            activity_score: 85
          }
        ])
      }
    },
    async fetchPosts({ commit }, sub = null) {
      try {
        let posts = []
        if (sub === 'communication') {
          // 并行请求两种类型的帖子
          const [commPosts, homePosts] = await Promise.all([
            get(`/posts?sub=${sub}`),
            get(`/posts?mode=首页`)
          ])

          // 合并并去重（基于post id）
          const postMap = new Map()
          commPosts.forEach(post => postMap.set(post.id, post))
          homePosts.forEach(post => postMap.set(post.id, post))
          posts = Array.from(postMap.values())

          // 按时间倒序排序
          posts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        } else {
          const url = sub ? `/posts?sub=${sub}` : '/posts'
          posts = await get(url)
        }

        commit('setPosts', posts)
      } catch (error) {
        console.error('Failed to fetch posts:', error)
        // 使用默认数据
        commit('setPosts', [
          {
            id: 1,
            title: '西藏之旅：心灵的洗礼',
            content: '这次西藏之行让我感受到了前所未有的宁静与平和。布达拉宫的庄严，纳木错的纯净，还有那些虔诚的信徒，都让我对生活有了新的认识。',
            sub: 'communication',
            image: 'https://images.unsplash.com/photo-1544735716-392fe2489ffc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
            likes: 42,
            created_at: '2023-08-20T00:00:00',
            author: {
              id: 1,
              username: '旅行达人',
              avatar: 'https://randomuser.me/api/portraits/men/22.jpg'
            },
            comments_count: 15
          }
        ])
      }
    },
   async fetchRandomQuestion({ commit }) {
  try {
    const question = await get('/questions/random')
    console.log('API返回的题目数据:', question)

    // 验证数据格式
    if (!question || !question.question || !question.options) {
      console.error('题目数据格式不正确:', question)
      throw new Error('Invalid question data format')
    }

    commit('setCurrentQuestion', question)
  } catch (error) {
    console.error('Failed to fetch question:', error)
    // 使用默认数据
    const defaultQuestions = [
      {
        id: 1,
        question: '下列哪一项不是世界文化遗产？',
        options: [
          'A. 中国的长城',
          'B. 印度的泰姬陵',
          'C. 美国的自由女神像',
          'D. 埃及的金字塔'
        ],
        correct_answer: 2,
        type: 'single',
        sub:'自然人文',
        likes: 15
      },
      {
        id: 2,
        question:'世界上最大的珊瑚礁系统是？',
        options: [
            'A. 大堡礁',
            'B. 马尔代夫珊瑚礁',
            'C. 红海珊瑚礁',
            'D. 佛罗里达珊瑚礁'
        ],
        correct_answer:0,
        type:'single',
        sub:'自然人文',
        likes:12
      }
    ]
    const randomQuestion = defaultQuestions[Math.floor(Math.random() * defaultQuestions.length)]
    console.log('使用默认题目:', randomQuestion)
    commit('setCurrentQuestion', randomQuestion)
  }
},
    async createPost({ commit }, postData) {
      try {
        const newPost = await post('/posts', postData)
        commit('addPost', newPost)
        return newPost
      } catch (error) {
        console.error('Failed to create post:', error)
        throw error
      }
    },
    async createCommunity({ commit }, communityData) {
      try {
        const newCommunity = await post('/communities', communityData)
        commit('addCommunity', newCommunity)
        return newCommunity
      } catch (error) {
        console.error('Failed to create community:', error)
        throw error
      }
    },
     async joinCommunity({ commit, dispatch, state }, { communityId, userId }) {
      try {
        const updatedCommunity = await post(`/communities/${communityId}/join`, {
          user_id: userId
        })

        // 更新社区列表中的该社区
        const communities = state.communities.map(comm =>
          comm.id === communityId ? updatedCommunity : comm
        )
        commit('setCommunities', communities)

        // 重新获取用户的社区列表
        if (userId) {
          await dispatch('fetchUserCommunities', userId)
        }

        return updatedCommunity
      } catch (error) {
        console.error('Failed to join community:', error)
        throw error
      }
    },
    async createQuestion({ commit }, questionData) {
  try {
    const newQuestion = await post('/questions', questionData)
    // 不需要立即更新当前题目，因为新题目会在下次随机时出现
    return newQuestion
  } catch (error) {
    console.error('Failed to create question:', error)
    throw error
  }
},
    async fetchCommunityDetail({ commit }, communityId) {
  try {
    const community = await get(`/communities/${communityId}`)
    commit('setCommunityDetail', community)
  } catch (error) {
    console.error('Failed to fetch community detail:', error)
  }
},
async fetchCommunityPosts({ commit }, communityId) {
  try {
    const posts = await get(`/communities/${communityId}/posts`)
    commit('setCommunityPosts', posts)
  } catch (error) {
    console.error('Failed to fetch community posts:', error)
  }
},
async fetchPostDetail({ commit }, postId) {
  try {
    const post = await get(`/posts/${postId}/detail`)
    commit('setPostDetail', post)
  } catch (error) {
    console.error('Failed to fetch post detail:', error)
  }
},
async fetchUserCommunities({ commit }, userId) {
  try {
    const communities = await get(`/users/${userId}/communities`)
    commit('setCommunities', communities)
  } catch (error) {
    console.error('Failed to fetch user communities:', error)
    // 使用默认数据
    commit('setCommunities', [
      {
        id: 1,
        name: '登山爱好者',
        avatar: 'https://images.unsplash.com/photo-1590649880760-2d4b0f523de7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80',
        category: '户外运动',
        member_count: 342,
        post_count: 128,
        activity_score: 78
      },
      {
        id: 2,
        name: '旅行摄影',
        avatar: 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80',
        category: '摄影',
        member_count: 278,
        post_count: 156,
        activity_score: 85
      }
    ])
  }
},
async addComment({ commit }, { postId, content, userId }) {
  try {
    const comment = await post(`/posts/${postId}/comments`, {
      content,
      user_id: userId
    })
    commit('addComment', { postId, comment })
    return comment
  } catch (error) {
    console.error('Failed to add comment:', error)
    throw error
  }
 },
  async updatePost({ commit }, { postId, postData }) {
  try {
    const updatedPost = await put(`/posts/${postId}`, postData)
    // 如果需要更新状态中的文章数据，可以在这里添加相应的commit
    return updatedPost
  } catch (error) {
    console.error('Failed to update post:', error)
    throw error
  }
},
  async updateUserProfile({ commit, dispatch }, { userId, userData }) {
  try {
    const updatedUser = await put(`/users/${userId}`, userData)
    commit('setUser', updatedUser)
    // 重新获取用户信息以确保数据同步
    await dispatch('fetchUser', userId)
    return updatedUser
  } catch (error) {
    console.error('Failed to update user profile:', error)
    throw error
  }
}
},
  getters: {
    isAuthenticated: state => !!state.user,
    currentUser: state => state.user,
    authChecked: state => state.authChecked
  }

})