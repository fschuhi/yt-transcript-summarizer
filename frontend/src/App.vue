<template>
  <div id="app">
    <header>
      <img src="@/assets/logo.png" alt="Summara Logo" class="logo">
      <h1><span class="summara-text">Summara</span> – a minimal video transcript summarizer</h1>
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

<script lang="ts">
import { defineComponent } from 'vue';
import axios, { AxiosResponse } from 'axios';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { SummarizeResult, VideoMetadata } from './types';

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000';
import '@/assets/styles.css';

interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

function isApiError(error: unknown): error is ApiError {
  if (typeof error !== 'object' || error === null) {
    return false;
  }

  const errorObj = error as { response?: unknown };

  if (!errorObj.response || typeof errorObj.response !== 'object') {
    return false;
  }

  const responseObj = errorObj.response as { data?: unknown };

  return typeof responseObj.data === 'object' && responseObj.data !== null;
}

export default defineComponent({
  name: 'App',
  data() {
    return {
      videoUrl: '',
      summaryLength: 300,
      usedModel: 'gpt-4o-mini',
      result: null as SummarizeResult | null,
      accessToken: null as string | null,
      isLoading: false,
    };
  },
  created() {
    console.log('API_BASE_URL:', API_BASE_URL);
  },
  computed: {
    firstLineDescription(): string {
      return this.result?.metadata.description.split('\n')[0] || '';
  },
    formattedSummary(): string {
      return this.result?.summary.split('\n\n').map(p => `<p>${p}</p>`).join('') || '';
    },
    formattedDescription(): string {
      return this.result?.metadata.description.replace(/\n/g, '<br>') || '';
    }
  },
  methods: {
    formatDate(dateString: string): string {
      return new Date(dateString).toLocaleDateString();
    },

    async login(): Promise<boolean> {
      const apiKey = prompt("Enter your API key:");
      if (!apiKey) return false;

      try {
        console.log('Attempting to login with API key');
        const response: AxiosResponse<{ access_token: string }> = await axios.post(`${API_BASE_URL}/login`, null, {
          headers: { 'X-API-Key': apiKey }
        });
        console.log('Login response:', response);
        this.accessToken = response.data.access_token;
        return true;
      } catch (error) {
        console.error('Login error:', error);
        if (axios.isAxiosError(error)) {
          console.error('Axios error details:', error.response?.data, error.response?.status, error.response?.headers);
          alert(`Login failed: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
        } else {
          console.error('Non-Axios error:', error);
          alert("Login failed: Unknown error");
        }
        return false;
      }
    },

    async summarize(): Promise<void> {
      if (!this.accessToken) {
        const loggedIn = await this.login();
        if (!loggedIn) return;
      }

      this.isLoading = true;
      this.result = null;

      try {
        const response: AxiosResponse<SummarizeResult> = await axios.post(`${API_BASE_URL}/summarize`, {
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
        if (isApiError(error)) {
          alert(`Summarization failed: ${error.response?.data?.detail || 'Unknown error'}`);
        } else {
          alert("Summarization failed: Unknown error");
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
});
</script>