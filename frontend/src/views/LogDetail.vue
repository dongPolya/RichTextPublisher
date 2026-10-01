<template>
  <div class="page-content">
    <div v-if="log" class="log-detail">
      <div class="log-header">
        <div class="header-content">
          <h1 class="log-title">{{ log.title }}</h1>
          <button
            v-if="!hasMap"
            class="add-map-btn"
            @click="showCreateMapModal = true"
          >
            <font-awesome-icon :icon="['fas', 'map-marked-alt']" />
            添加巡游轨迹
          </button>
          <button
            v-else
            class="edit-map-btn"
            @click="showCreateMapModal = true"
          >
            <font-awesome-icon :icon="['fas', 'edit']" />
            编辑巡游轨迹
          </button>
        </div>
        <div class="log-meta">
          <span class="log-date">{{ formatDate(log.date) }}</span>
          <span class="log-destination">
            <font-awesome-icon :icon="['fas', 'map-marker-alt']" /> {{ log.destination }}
          </span>
        </div>
      </div>

      <div class="log-description">
        {{ log.description }}
      </div>

      <div class="log-content" v-html="log.content"></div>

      <div class="log-members">
        <h3>出行成员</h3>
        <div class="members-list">
          <div v-for="(member, index) in log.members" :key="index" class="member-item">
            <img :src="member.avatar" :alt="member.name" class="member-avatar">
            <span class="member-name">{{ member.name }}</span>
          </div>
        </div>
      </div>
      <div class="log-members">
        <h3>出行工具</h3>
        <div class="members-list">
          <div v-for="(transportation, index) in log.transportation" :key="index" class="member-item">
           <span class="member-name">{{ transportation }}</span>
             <font-awesome-icon
              :icon="getTransportationIcon(transportation)"
              class="transportation-icon"
              size="2x"
            />
          </div>
        </div>
      </div>

      <div v-if="log.footer" class="log-footer">
        {{ log.footer }}
      </div>

      <div class="log-actions">
        <button class="action-btn">
          <font-awesome-icon :icon="['fas', 'heart']" /> {{ log.likes || 0 }}
        </button>
        <button class="action-btn">
          <font-awesome-icon :icon="['fas', 'comment']" /> {{ log.comments_count || 0 }}
        </button>
        <button class="action-btn">
          <font-awesome-icon :icon="['fas', 'share']" /> 分享
        </button>
      </div>

      <!-- 地图容器 - 延迟加载 -->
      <div v-if="hasMap" class="map-section" ref="mapSection">
        <h3 class="section-title">
          <font-awesome-icon :icon="['fas', 'map']" />
          巡游轨迹地图
        </h3>
        <div v-if="mapLoading" class="map-loading">
          <p>地图加载中...</p>
        </div>
        <div v-else id="logMap" class="map-container"></div>

        <!-- 站点详情面板 -->
        <div v-if="selectedStop" class="stop-details-panel">
          <h4>站点详情</h4>
          <div class="detail-row">
            <span class="label">地点：</span>
            <span class="value">{{ selectedStop.location_name }}</span>
          </div>
          <div v-if="selectedStop.timestamp" class="detail-row">
            <span class="label">时间：</span>
            <span class="value">{{ formatDateTime(selectedStop.timestamp) }}</span>
          </div>
          <div v-if="selectedStop.event" class="detail-row">
            <span class="label">事件：</span>
            <span class="value">{{ selectedStop.event }}</span>
          </div>
          <div v-if="selectedStop.route_name" class="detail-row">
            <span class="label">线路：</span>
            <span class="value">{{ selectedStop.route_name }}</span>
          </div>
          <div v-if="selectedStop.transport_mode" class="detail-row">
            <span class="label">交通方式：</span>
            <span class="value">
              <font-awesome-icon :icon="getTransportIcon(selectedStop.transport_mode)" />
              {{ getTransportLabel(selectedStop.transport_mode) }}
            </span>
          </div>
          <button class="close-details" @click="selectedStop = null">关闭</button>
        </div>
      </div>
    </div>

    <div v-else class="loading">
      加载中...
    </div>

    <!-- 创建地图模态框 -->
    <CreateMapModal
      :visible="showCreateMapModal"
      :title="hasMap ? '编辑巡游轨迹' : '添加巡游轨迹'"
      :initial-data="existingMap"
      :log-id="logId"
      @close="showCreateMapModal = false"
      @save="handleSaveMap"
    />
  </div>
</template>
<script>
import { useApi } from '@/composables/useApi'
import CreateMapModal from '@/components/CreateMapModal.vue'
import { getTransportColor, getTransportIcon, getTransportLabel } from '@/utils/mapUtils'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
export default {
  name: 'LogDetail',
   components: {
    CreateMapModal
  },
  data() {
    return {
      log: null,
      loading: false,
      error: null,
      showCreateMapModal: false,
      existingMap: null,
      hasMap: false,
      mapInstance: null,
      mapLoading: false,
      selectedStop: null,
      mapRendered: false
    }
  },
  async created() {
    const logId = this.$route.params.id
    await this.fetchLogDetail(logId)
    // 获取地图数据
    await this.fetchMapData(logId)
  },
  computed: {
    logId() {
      return this.$route.params.id
    }
  },
  methods: {
    async fetchLogDetail(logId) {
      this.loading = true
      this.error = null

      try {
        const { get } = useApi()
        this.log = await get(`/logs/${logId}/detail`)
      } catch (err) {
        console.error('Failed to fetch log detail:', err)
        this.error = '获取日志详情失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    async fetchMapData(logId) {
      console.log('Fetching map data for log:', logId)
      try {
        const { get } = useApi()
        const response = await get(`/maps/log/${logId}`)
        console.log('Map data response:', response)
        // 后端直接返回地图数据或 {map: null} 格式
        const mapData = response.map !== undefined ? response.map : response
        if (mapData && mapData.id) {
          this.existingMap = mapData
          this.hasMap = true
          console.log('Map found, hasMap set to true')
          // 数据获取成功后渲染地图
          this.$nextTick(() => {
            setTimeout(() => {
              this.renderMap()
            }, 200)
          })
        } else {
          // 没有地图数据
          this.existingMap = null
          this.hasMap = false
          console.log('No map found, hasMap set to false')
        }
      } catch (err) {
        console.error('Failed to fetch map data:', err)
        // 出错了也重置状态
        this.existingMap = null
        this.hasMap = false
      }
    },

    async handleSaveMap(mapData) {
      console.log('Saving map data:', mapData)
      try {
        const { post, put } = useApi()

        if (this.existingMap) {
          // 更新现有地图
          console.log('Updating existing map:', this.existingMap.id)
          await put(`/maps/${this.existingMap.id}`, mapData)
        } else {
          // 创建新地图
          console.log('Creating new map')
          await post('/maps', mapData)
        }

        this.showCreateMapModal = false
        // 重置地图状态
        this.mapRendered = false
        if (this.mapInstance) {
          this.mapInstance.remove()
          this.mapInstance = null
        }
        // 重新获取地图数据并渲染
        await this.fetchMapData(this.logId)

        alert('地图保存成功！')
      } catch (err) {
        console.error('Failed to save map:', err)
        alert('保存地图失败，请重试')
      }
    },

    renderMap(retryCount = 0) {
      if (!this.existingMap) return

      // 如果地图已经渲染过，先清除
      if (this.mapInstance) {
        this.mapInstance.remove()
        this.mapInstance = null
      }

      this.mapLoading = true
      this.mapRendered = false

      // 检查地图容器是否存在
      const mapContainer = document.getElementById('logMap')
      if (!mapContainer) {
        console.warn(`Map container not found, retrying... (${retryCount + 1}/10)`)
        if (retryCount < 10) {
          // 延迟重试
          setTimeout(() => {
            this.renderMap(retryCount + 1)
          }, 100)
        } else {
          console.error('Map container not found after max retries')
          this.mapLoading = false
        }
        return
      }

      // 容器存在，初始化地图
      try {

            // 初始化地图
            this.mapInstance = L.map('logMap').setView([39.9042, 116.4074], 13)

            // 使用高德地图瓦片（国内访问更稳定）
            L.tileLayer('http://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
              subdomains: ['1', '2', '3', '4'],
              maxZoom: 19,
              attribution: '© 高德地图'
            }).addTo(this.mapInstance)

            const stops = this.existingMap.stops || []
            const latlngs = []

            // 添加站点标记
            stops.forEach((stop, index) => {
              if (stop.latitude && stop.longitude) {
                const color = stop.stop_type === 'station' ? '#e74c3c' : '#3498db'

                const marker = L.circleMarker([stop.latitude, stop.longitude], {
                  radius: stop.stop_type === 'station' ? 10 : 8,
                  fillColor: color,
                  color: '#fff',
                  weight: 2,
                  opacity: 1,
                  fillOpacity: 0.9
                }).addTo(this.mapInstance)

                marker.bindPopup(`<strong>${index + 1}. ${stop.location_name}</strong>`)

                // 双击显示详情
                marker.on('dblclick', () => {
                  this.selectedStop = stop
                })

                latlngs.push([stop.latitude, stop.longitude])
              }
            })

            // 绘制彩色线路
            for (let i = 0; i < latlngs.length - 1; i++) {
              const stop = stops[i]
              const lineColor = stop.line_color || getTransportColor(stop.transport_mode)

              L.polyline([latlngs[i], latlngs[i + 1]], {
                color: lineColor,
                weight: 4,
                opacity: 0.8
              }).addTo(this.mapInstance)
            }

            // 调整视野以包含所有点
            if (latlngs.length > 0) {
              this.mapInstance.fitBounds(latlngs, { padding: [50, 50] })
            }

            this.mapRendered = true
            this.mapLoading = false
          } catch (err) {
            console.error('Failed to render map:', err)
            this.mapLoading = false
          }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    // 使用导入的函数
    getTransportIcon(mode) {
      return getTransportIcon(mode)
    },
    getTransportLabel(mode) {
      return getTransportLabel(mode)
    },
    getTransportationIcon(transportation) {
      const iconMap = {
        '火车': ['fas', 'train'],
        '飞机': ['fas', 'plane'],
        '汽车': ['fas', 'car'],
        '轮船': ['fas', 'ship'],
        '地铁': ['fas', 'subway'],
        '公交': ['fas', 'bus'],
        '骑行': ['fas', 'bicycle'],
        '步行': ['fas', 'walking'],
        '电动车': ['fas', 'motorcycle']
      }

      return iconMap[transportation] || ['fas', 'question-circle']
    }
  }
}
</script>

<style scoped>
.log-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.log-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.log-title {
  font-size: 2.2rem;
  color: #2c3e50;
  margin: 0;
}

.add-map-btn,
.edit-map-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.add-map-btn {
  background: #1abc9c;
  color: white;
}

.add-map-btn:hover {
  background: #16a085;
}

.edit-map-btn {
  background: #3498db;
  color: white;
}

.edit-map-btn:hover {
  background: #2980b9;
}

.log-meta {
  display: flex;
  gap: 20px;
  color: #7f8c8d;
}

.log-destination {
  display: flex;
  align-items: center;
  gap: 5px;
}

.log-description {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

.log-content {
  line-height: 1.8;
  color: #333;
  margin-bottom: 30px;
}

.log-content ::v-deep p {
  margin-bottom: 1rem;
}

.log-members {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.log-members h3 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.members-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.member-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.member-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

.member-name {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.log-footer {
  font-style: italic;
  color: #7f8c8d;
  text-align: center;
  margin-bottom: 30px;
  padding: 15px;
  border-top: 1px solid #eee;
}

.log-actions {
  display: flex;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  color: #7f8c8d;
}

.action-btn:hover {
  background: #e9ecef;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.transportation-icon {
  color: #3498db;
}

/* 地图区域样式 */
.map-section {
  margin-top: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.section-title {
  margin-bottom: 20px;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.map-container {
  width: 100%;
  height: 500px;
  border-radius: 8px;
  border: 2px solid #ddd;
  margin-bottom: 20px;
}

.map-loading {
  text-align: center;
  padding: 50px;
  color: #7f8c8d;
}

.stop-details-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.stop-details-panel h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.detail-row {
  display: flex;
  margin-bottom: 10px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.detail-row .label {
  font-weight: 600;
  color: #7f8c8d;
  min-width: 100px;
}

.detail-row .value {
  color: #2c3e50;
  flex: 1;
}

.close-details {
  margin-top: 15px;
  padding: 8px 20px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.close-details:hover {
  background: #7f8c8d;
}
</style>