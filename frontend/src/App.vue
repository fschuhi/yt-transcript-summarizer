<template>
  <div id="app">
    <header>
      <img src="@/assets/logo.png" alt="Summara Logo" class="logo">
      <h1>Summara – a minimal video transcript summarizer</h1>
    </header>
    <form @submit.prevent="summarize">
      <div class="form-group">
        <label for="video-url">YouTube URL or Video ID:</label>
        <input id="video-url" v-model="videoUrl" type="text" placeholder="Enter YouTube URL or Video ID" required>
      </div>
      <div class="form-group">
        <label for="summary-length">Summary Length:</label>
        <input id="summary-length" v-model.number="summaryLength" type="number" required>
      </div>
      <div class="form-group">
        <label for="used-model">Used Model:</label>
        <select id="used-model" v-model="usedModel">
          <option value="gpt-4o-mini">GPT-4o mini</option>
        </select>
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Summarizing...' : 'Summarize' }}
      </button>
    </form>

    <div v-if="isLoading" class="loading-indicator">
      <div class="spinner"></div>
      <p>Summarizing video... Please wait.</p>
    </div>

    <div v-if="result" id="result">
      <div class="box main-info-box">
        <h2>{{ result.metadata.title }}</h2>
        <p><span class="info-label">Channel:</span> {{ result.metadata.channel_title }}</p>
        <p><span class="info-label">Description (1st line):</span> {{ firstLineDescription }}</p>
      </div>
      <div class="box summary-box">
        <h2>Summary</h2>
        <div id="summary-content" v-html="formattedSummary"></div>
        <p id="word-count">Word count: {{ result.word_count }}</p>
      </div>
      <div class="box date-counts-box">
        <p>Published: {{ formatDate(result.metadata.publish_date) }}</p>
        <p>Views: {{ result.metadata.view_count }}</p>
        <p>Likes: {{ result.metadata.like_count }}</p>
        <p>Comments: {{ result.metadata.comment_count }}</p>
      </div>
      <div class="box long-desc-box">
        <p v-html="formattedDescription"></p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      videoUrl: '',
      summaryLength: 300,
      usedModel: 'gpt-4o-mini',
      result: null,
      accessToken: null,
      isLoading: false,
    };
  },
  computed: {
    firstLineDescription() {
      return this.result?.metadata.description.split('\n')[0] || '';
    },
    formattedSummary() {
      return this.result?.summary.split('\n\n').map(p => `<p>${p}</p>`).join('') || '';
    },
    formattedDescription() {
      return this.result?.metadata.description.replace(/\n/g, '<br>') || '';
    },
  },
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString();
    },
    async login() {
      const apiKey = prompt("Enter your API key:");
      if (!apiKey) return false;

      try {
        const response = await axios.post('http://localhost:8000/login', null, {
          headers: { 'X-API-Key': apiKey }
        });
        this.accessToken = response.data.access_token;
        return true;
      } catch (error) {
        console.error('Login error:', error);
        alert("Invalid API key");
        return false;
      }
    },
    async summarize() {
      if (!this.accessToken) {
        const loggedIn = await this.login();
        if (!loggedIn) return;
      }

      this.isLoading = true;
      this.result = null;

      try {
        const response = await axios.post('http://localhost:8000/summarize', {
          video_url: this.videoUrl,
          summary_length: this.summaryLength,
          used_model: this.usedModel
        }, {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': this.accessToken
          }
        });
        this.result = response.data;
      } catch (error) {
        console.error('Summarize error:', error);
        alert(`Summarization failed: ${error.response?.data?.detail || 'Unknown error'}`);
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style>
/* You can keep your existing styles and add these new ones */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>