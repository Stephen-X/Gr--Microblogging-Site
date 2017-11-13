/**
 * A simple jQuery script for parallax jumbotron effect.
 *
 * @author cskelly (https://www.bootply.com/103783)
 */
var jumboHeight = $('.jumbotron').outerHeight();
function parallax(){
    var scrolled = $(window).scrollTop();
    $('.profile-pic').css('height', (jumboHeight-scrolled) + 'px');
}

$(window).scroll(function(e){
    parallax();
});