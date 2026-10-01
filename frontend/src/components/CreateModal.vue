<template>
  <div class="modal-overlay" v-if="visible" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="modal-body">
        <slot></slot>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">取消</button>
        <button class="btn btn-primary" @click="submit">提交</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreateModal',
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: '创建新内容'
    }
  },
  emits: ['close', 'submit'],
  methods: {
    close() {
      this.$emit('close')
    },
    submit() {
      this.$emit('submit')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
}

.close-btn:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  background-color: #1abc9c;
  color: white;
}

.btn-primary:hover {
  background-color: #16a085;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}
</style>