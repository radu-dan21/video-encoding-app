function reload() {
    $.ajax({
        type: "get",
        url: $(location).attr("href"),
        datatype: "html",
        success: function(data) {
            const parser = new DOMParser();
            const htmlDoc = parser.parseFromString(data, 'text/html');
            const bodyContents = htmlDoc.querySelector('body').innerHTML;
            $('body').html(bodyContents);
        }
    });
}
