import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,  // Changed to true for recording
    screenshotOnRunFailure: true,
    videoCompression: 32,
    videosFolder: 'cypress/videos',
  },
});