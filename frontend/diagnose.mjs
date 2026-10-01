// diagnose.mjs
import { fileURLToPath } from 'node:url'
import { resolve, dirname } from 'path'
import { existsSync } from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

console.log('=== 路径诊断 ===')

// 检查关键路径
const pathsToCheck = [
    { name: 'src目录', path: resolve(__dirname, 'src') },
    { name: 'stores目录', path: resolve(__dirname, 'src/stores') },
    { name: 'pageStore.js文件', path: resolve(__dirname, 'src/stores/pageStore.js') },
    { name: 'composables目录', path: resolve(__dirname, 'src/composables') },
    { name: 'useApi.js文件', path: resolve(__dirname, 'src/composables/useApi.js') }
]

pathsToCheck.forEach(item => {
    console.log(`${item.name}: ${item.path}`)
    console.log(`   存在: ${existsSync(item.path) ? '✅' : '❌'}`)
})

console.log('\n=== 别名解析测试 ===')
try {
    const aliasPath = fileURLToPath(new URL('./src', import.meta.url))
    console.log('@ 别名解析为:', aliasPath)
    console.log('@/stores/pageStore.js 应该解析为:', resolve(aliasPath, 'stores/pageStore.js'))
    console.log('该路径存在:', existsSync(resolve(aliasPath, 'stores/pageStore.js')) ? '✅' : '❌')
} catch (error) {
    console.log('别名解析错误:', error.message)
}