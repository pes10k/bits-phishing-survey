module.exports = function(grunt) {

  grunt.initConfig({
    compass: {
      options: {
        config: 'compass/config.rb',
        sassDir: 'compass/sass',
        cssDir: 'static/stylesheets',
        environment: 'production'
      }
    },
    coffee: {
      compile: {
        files: {
          'static/script/main.js': ['coffeescript/*.coffee']
        }
      },
    }
  });

  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.registerTask('default', ['compass', 'coffee']);
};
