<template>
  <div class="file-upload">
    <input
      ref="fileInput"
      type="file"
      @change="handleFileChange"
      accept="image/*"
      style="display: none"
    />
    
    <button @click="$refs.fileInput.click()" class="input-btn" title="Upload image">
      📷
    </button>
    
    <div v-if="selectedFile" class="file-preview">
      <div class="selected-file">
        <img :src="filePreview" alt="Selected image" class="file-image" />
        <button @click="removeFile" class="remove-file-btn" title="Remove image">
          ✕
        </button>
      </div>
      <div class="file-info">
        <small>{{ selectedFile.name }}</small>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'FileUpload',
  emits: ['fileSelected', 'fileRemoved'],
  setup(props, { emit }) {
    const selectedFile = ref(null)
    const filePreview = ref('')
    
    const handleFileChange = (event) => {
      const file = event.target.files[0]
      
      if (file) {
        selectedFile.value = file
        
        const reader = new FileReader()
        reader.onload = (e) => {
          filePreview.value = e.target.result
          emit('fileSelected', {
            file,
            preview: filePreview.value
          })
        }
        reader.readAsDataURL(file)
      }
    }
    
    const removeFile = () => {
      selectedFile.value = null
      filePreview.value = ''
      emit('fileRemoved')
    }
    
    return {
      selectedFile,
      filePreview,
      handleFileChange,
      removeFile
    }
  }
}
</script>

<style scoped>
.file-info {
  margin-top: 0.5rem;
  text-align: center;
}

.file-info small {
  color: var(--text-muted);
}
</style>
