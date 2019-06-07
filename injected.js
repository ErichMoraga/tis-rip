while ($ === undefined) {}

$(".footer").remove();

$("link[rel=stylesheet]").each(function(e) {
    var ss = $(this);
    var href = ss[0].href;
    $.ajax({
        url: href,
        async: false,
        success: function(result) {
            $("style").remove();

            var selem = $("<style type=\"text/css\">" + result + "</style>");
            $("head").append(selem);
        },
    });
    ss.remove();
});

$("img").each(function(i, img) {
    if (img.currentSrc.indexOf("data:") !== 0) {
        var c = document.createElement("canvas");
        var ctx = c.getContext("2d");
        c.width = img.naturalWidth;
        c.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0);
        var dataURL = c.toDataURL();
        img.src = dataURL;
    } else {
        console.log("already data uri");
    }
});

$("script").remove();

return document.documentElement.outerHTML;