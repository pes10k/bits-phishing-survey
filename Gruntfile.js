module.exports = function(grunt) {

  grunt.initConfig({
    compass: {
      options: {
        config: 'compass/config.rb',
        sassDir: 'compass/sass',
        cssDir: 'static/stylesheets',
        environment: 'production'
      },
      dist: {}
    },
    coffee: {
      compile: {
        files: {
          'static/js/signin.js': ['coffeescript/signin.coffee'],
          //'static/js/survey.js': ['coffeescript/survey.coffee']
        }
      },
    }
  });

  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.registerTask('default', ['compass', 'coffee']);
};
