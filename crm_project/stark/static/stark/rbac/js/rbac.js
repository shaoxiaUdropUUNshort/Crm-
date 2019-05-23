(function (jq) {
    jq('.multi-menu .title').click(function () {
        $(this).next().removeClass("hide");
        $(this).parent().siblings().children(".body").addClass('hide');
    });
})(jQuery);



