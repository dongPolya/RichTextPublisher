
export const TRANSPORT_MODES = {
  walking: { label: '步行', color: '#95a5a6', icon: 'walking' },
  bus: { label: '公交', color: '#f39c12', icon: 'bus' },
  subway: { label: '地铁', color: '#3498db', icon: 'subway' },
  train: { label: '火车', color: '#e74c3c', icon: 'train' },
  high_speed_rail: { label: '高铁', color: '#9b59b6', icon: 'train' },
  bicycle: { label: '骑行', color: '#2ecc71', icon: 'bicycle' },
  car: { label: '汽车', color: '#1abc9c', icon: 'car' },
  plane: { label: '飞机', color: '#e67e22', icon: 'plane' },
  ship: { label: '轮船', color: '#34495e', icon: 'ship' }
}

/**
 * 根据交通方式获取颜色
 */
export function getTransportColor(mode) {
  return TRANSPORT_MODES[mode]?.color || '#95a5a6'
}

/**
 * 根据交通方式获取标签
 */
export function getTransportLabel(mode) {
  return TRANSPORT_MODES[mode]?.label || '未知'
}

/**
 * 根据交通方式获取图标
 */
export function getTransportIcon(mode) {
  return ['fas', TRANSPORT_MODES[mode]?.icon || 'question-circle']
}

/**
 * 高德地图API密钥
 */
export const AMAP_API_KEY = '1f552bb72247d64a541a37fd68063535'

/**
 * 默认地图配置
 */
export const DEFAULT_MAP_CONFIG = {
  zoom: 13,
  center: [39.9042, 116.4074],
  tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
}
