const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  chainWebpack: config => {
    config.resolve.extensions.add('.typescript')

    // Add this part to handle the environment variable
    config.plugin('define').tap(args => {
      const env = process.env
      args[0]['process.env'] = Object.assign(args[0]['process.env'], {
        VUE_APP_API_BASE_URL: JSON.stringify(env.VUE_APP_API_BASE_URL)
      })
      return args
    })
  }
})